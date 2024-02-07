from typing import List

from nicegui import ui

import requester


class Node:
    uid: str
    title: str
    type: str
    description: str
    long_description: str
    raw: dict

    def __init__(self, raw_data: dict):
        self.raw = raw_data
        document_data = raw_data
        if "document" in raw_data:
            document_data = raw_data["document"]
        self.uid = document_data.get("id", "")
        self.title = document_data.get("titel", "")
        self.type = document_data.get("type", "")
        self.description = document_data.get("beschreibung", "")
        self.long_description = document_data.get("textLong", "")

    def get_api_url(self) -> str:
        return f"https://zdf-cdn.live.cellular.de/mediathekV2/documents/{self.uid}"

    def get_internal_url(self) -> str:
        return f"/doc/{self.uid}"

    def __str__(self):
        return self.title

    def get_children_pool(self) -> List["Node"]:
        result = requester.get_id(self.uid)
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

    def get_img_url(self, width: int = 1) -> str:
        teaserbild = self.raw.get("teaserBild", {})
        img_width = teaserbild.get(str(width), {})
        return img_width.get("url", "")

    def get_img_ui(self, requested_width: int = 1):
        teaserbild = self.raw.get("teaserBild", {})
        img_width = teaserbild.get(str(requested_width), {})
        actual_width = img_width.get("width", 0)
        url = img_width.get("url", "")
        return ui.image(url).props(f"width={actual_width}")

    def get_preview_ui(self):
        with ui.link(target=f"/doc/{self.uid}"):
            with ui.card().tight().classes("w-72"):
                ui.image(self.get_img_url(7)).classes("h-full")
                # element.get_img_ui(7)
                with ui.card_section():
                    ui.label(self.title)

    def get_teasers_from_cluster(self, cluster_index: int) -> List["Node"]:
        elements = []
        cluster_list = self.raw.get("cluster", [])
        # Check that index is present, else return empty list
        if len(cluster_list) > cluster_index:
            teaser_list = cluster_list[cluster_index].get("teaser", [])
            for element in teaser_list:
                new_node = Node(element)
                elements.append(new_node)
        return elements

    def get_standalone_ui(self):
        if self.type == "category":
            for cluster_index in range(0, len(self.raw.get("cluster", []))):
                with ui.row():
                    for element in self.get_teasers_from_cluster(cluster_index):
                        element.get_preview_ui()
        else:
            with ui.row().classes('items-stretch'):
                for element in self.get_children_pool():
                    element.get_preview_ui()

    @staticmethod
    def load(uid: str) -> "Node":
        return Node(requester.get_id(uid))
