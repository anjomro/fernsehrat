from typing import Dict, List

import httpx

from node import Node

from requester import get_url, get_document, categories_overview_url


def get_categories() -> Dict[str, str]:
    result = get_url(categories_overview_url)
    # cluster / 0 / teaser
    # { (id): (titel) }
    categories_list = result["cluster"][0]["teaser"]
    return {category["id"]: category["titel"] for category in categories_list}


def get_category(category_id: str) -> List[Node]:
    result = get_document(category_id)
    elements = []
    cluster_list = result["cluster"]
    for cluster in cluster_list:
        teaser_list = cluster["teaser"]
        for element in teaser_list:
            new_node = Node(element)
            elements.append(new_node)
    return elements


elm = []

cats = get_categories()

for category_id, category_title in cats.items():
    print(f"{category_id}: {category_title}")
    elm.append(get_category(category_id))

#elm[0][621].get_children_pool()
test = 0
