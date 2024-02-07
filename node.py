from typing import List

import requester


class Node:
    uid: str
    url: str
    title: str
    type: str
    description: str
    long_description: str
    raw: dict

    def __init__(self, raw_data: dict):
        self.raw = raw_data
        self.uid = raw_data.get("id", "")
        self.url = raw_data.get("url", "")
        self.title = raw_data.get("titel", "")
        self.type = raw_data.get("type", "")
        self.description = raw_data.get("beschreibung", "")
        self.long_description = raw_data.get("textLong", "")

    def __str__(self):
        return self.title

    def get_children_pool(self) -> List["Node"]:
        result = requester.get_document(self.uid)
        elements = []
        element_ids = []
        cluster_list = result["cluster"]
        for cluster in cluster_list:
            # exclude if recommendation type: teaserPoster
            if cluster.get("type", "") != "teaserPoster":
                teaser_list = cluster["teaser"]
                for element in teaser_list:
                    new_node = Node(element)
                    if new_node.uid not in element_ids:
                        element_ids.append(new_node.uid)
                        elements.append(new_node)
        return elements
