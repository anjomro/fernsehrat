from functools import cache

import httpx

BASE_URL = "https://zdf-cdn.live.cellular.de/mediathekV2/document/"

USER_AGENT = "com.zdf.android.mediathek/5.19 Dalvik/2.1.0 (Linux; U; Android 9; Galaxy S10 Build/PI)"


@cache
def get_url(url: str) -> dict:
    headers = {
        "User-Agent": USER_AGENT,
    }
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


def get_id(did: str) -> dict:
    return get_url(BASE_URL + did)