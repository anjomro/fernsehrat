from typing import Dict

import httpx

BASE_URL = "https://zdf-cdn.live.cellular.de/mediathekV2/"

USER_AGENT = "com.zdf.android.mediathek/5.19 Dalvik/2.1.0 (Linux; U; Android 9; Galaxy S10 Build/PI)"

categories_overview_url = BASE_URL + "categories-overview"


def get_categories() -> Dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
    }
    with httpx.Client() as client:
        response = client.get(categories_overview_url, headers=headers)
        response.raise_for_status()
        result = response.json()
        # cluster / 0 / teaser
        # { (id): (titel) }
        categories_list = result["cluster"][0]["teaser"]
        return {category["id"]: category["titel"] for category in categories_list}


def get_category(category_id: str) -> Dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
    }
    with httpx.Client() as client:
        response = client.get(BASE_URL + "document" + category_id, headers=headers)
        response.raise_for_status()
        # cluster / 0-n / teaser / 0-n
        # { (id): (titel) }
        result = response.json()



for category_id, category_title in get_categories().items():
    print(f"{category_id}: {category_title}")
