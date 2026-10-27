import httpx

USER_AGENT = "GEOFORA/1.0 (ajulianrague@gmail.com)"


def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=10.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
