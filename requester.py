from functools import cache
from pathlib import Path

import httpx

BASE_URL = "https://zdf-cdn.live.cellular.de/mediathekV2/document/"

USER_AGENT = "com.zdf.android.mediathek/5.19 Dalvik/2.1.0 (Linux; U; Android 9; Galaxy S10 Build/PI)"


def get_url(url: str) -> dict:
    print(f"Requesting: {url}")
    headers = {
        "User-Agent": USER_AGENT,
    }
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


def get_id(did: str) -> dict:
    return get_url(BASE_URL + did)


def download_file(url: str, dest_path: str):
    path = Path(dest_path)
    # Check if path exists, if not create it
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading: {url} to {path}")
    with httpx.stream("GET", url) as response:
        with path.open("wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
    print(f"Downloaded {path}")