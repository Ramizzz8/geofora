import logging

from app.logs import RedactSecrets


def test_redacts_api_key_in_logged_urls():
    record = logging.LogRecord("httpx", logging.INFO, __file__, 1,
                               'HTTP Request: %s %s "%s"',
                               ("GET", "https://ws.audioscrobbler.com/2.0/?method=x&api_key=SECRETKEY123&format=json", "200 OK"),
                               None)
    assert RedactSecrets().filter(record) is True
    msg = record.getMessage()
    assert "SECRETKEY123" not in msg
    assert "api_key=***&format=json" in msg
