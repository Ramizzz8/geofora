import logging
import re

# httpx escribe la URL de cada petición; la de Last.fm lleva la clave en la query
SECRET_PARAM = re.compile(r"(api_key=)[^&\s\"']+")


class RedactSecrets(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = SECRET_PARAM.sub(r"\1***", message)
        if redacted != message:
            record.msg, record.args = redacted, None
        return True


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    for handler in logging.getLogger().handlers:
        handler.addFilter(RedactSecrets())
