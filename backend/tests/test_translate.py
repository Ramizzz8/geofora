import httpx
import pytest
import respx

from app.db import connect, init_db
from app.news.gdelt import Article
from app.translate import DEEPL_URL, DeepLTranslator, translate_titles


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "t.db"))
    init_db(c)
    return c


def art(title, lang):
    return Article(f"https://x/{title}", title, lang, "x.com", "", 1.0)


class FakeTranslator:
    def __init__(self):
        self.calls = []

    async def translate(self, texts, source, target):
        self.calls.append((tuple(texts), source, target))
        return [f"ES:{t}" for t in texts]


async def test_spanish_title_not_translated(conn):
    t = FakeTranslator()
    out = await translate_titles(conn, t, [art("Hola mundo", "es")])
    assert t.calls == []
    assert out[0].title == "Hola mundo"
    assert out[0].translated is False


async def test_translates_and_caches(conn):
    t = FakeTranslator()
    out = await translate_titles(conn, t, [art("Hello", "en"), art("Bonjour", "fr")])
    assert [o.title for o in out] == ["ES:Hello", "ES:Bonjour"]
    assert all(o.translated for o in out)
    assert out[0].title_original == "Hello"
    assert len(t.calls) == 2  # una llamada por idioma

    t2 = FakeTranslator()
    out2 = await translate_titles(conn, t2, [art("Hello", "en")])
    assert t2.calls == []
    assert out2[0].title == "ES:Hello"


async def test_no_translator_returns_originals(conn):
    out = await translate_titles(conn, None, [art("Hello", "en")])
    assert out[0].title == "Hello"
    assert out[0].translated is False


@respx.mock
async def test_deepl_quota_exceeded_returns_originals(conn):
    respx.post(DEEPL_URL).mock(return_value=httpx.Response(456, json={"message": "Quota exceeded"}))
    async with httpx.AsyncClient() as client:
        out = await translate_titles(conn, DeepLTranslator("k", client), [art("Hello", "en")])
    assert out[0].translated is False
    assert out[0].title == out[0].title_original == "Hello"


@respx.mock
async def test_deepl_request_format():
    route = respx.post(DEEPL_URL).mock(return_value=httpx.Response(200, json={"translations": [{"text": "Hola"}]}))
    async with httpx.AsyncClient() as client:
        assert await DeepLTranslator("k", client).translate(["Hello"], "en", "es") == ["Hola"]
    req = route.calls.last.request
    assert req.headers["Authorization"] == "DeepL-Auth-Key k"
    import json
    assert json.loads(req.content) == {"text": ["Hello"], "target_lang": "ES", "source_lang": "EN"}
