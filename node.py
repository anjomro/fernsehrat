import json
import mimetypes
from functools import cache
from threading import Thread
from typing import List, Optional

from nicegui import ui

import requester
import config


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

    def get_brand(self) -> Optional["Node"]:
        if self.type == "brand":
            return self
        if "brandInfo" in self.raw:
            return Node(self.raw["brandInfo"])
        return None

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

    def get_img_by_preference(self, preference: List[int]) -> dict:
        source = self.raw
        if "document" in self.raw:
            source = self.raw["document"]
        image = source.get("image", {})
        teaserbild = source.get("teaserBild", {})
        for pref in preference:
            img_width = image.get(str(pref), {})
            if img_width:
                # Prefer image over teaserbild
                return img_width
            img_width = teaserbild.get(str(pref), {})
            if img_width:
                return img_width
        return {}

    def get_img_url(self, preference: Optional[List[int]] = None) -> str:
        if not preference:
            preference = [7, 276]
        img = self.get_img_by_preference(preference)
        return img.get("url", "")

    def get_img_ui(self, requested_width: Optional[List[int]] = None):
        if requested_width is None:
            requested_width = [276, 384, 7]
        img = self.get_img_by_preference(requested_width)
        actual_width = img.get("width", 0)
        url = img.get("url", "")
        return ui.image(url).props(f"width={actual_width}")

    def get_preview_ui(self):
        with ui.link(target=f"/doc/{self.uid}"):
            with ui.card().tight().classes("w-72"):
                ui.image(self.get_img_url()).classes("h-full")
                # element.get_img_ui()
                with ui.card_section():
                    ui.label(self.title)

    def get_preview_html(self) -> str:
        return f"""
        <a href="{self.get_internal_url()}" target="_self" class="nicegui-link">
        <div class="q-card nicegui-card nicegui-card-tight w-72">
        <div class="q-img q-img--menu h-full" role="img">
        <div style="padding-bottom: 56.1594%;"></div>
        <div class="q-img__container absolute-full">
        <img class="q-img__image q-img__image--with-transition q-img__image--loaded" style="object-fit: cover; object-position: 50% 50%;" loading="lazy" fetchpriority="auto" aria-hidden="true" draggable="false" src="{self.get_img_url()}"></div>
        <div class="q-img__content absolute-full q-anchor--skip"></div></div>
        <div class="q-card__section q-card__section--vert"><div>{self.title}</div></div></div></a>"""

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

    @cache
    def get_video_url(self) -> str:
        if self.type == "video":
            if "document" in self.raw and "formitaeten" in self.raw["document"]:
                formitaeten = self.raw["document"]["formitaeten"]
                mime_type_priorities = ["video/mp4", "application/x-mpegURL"]
                quality_priorities = ["fhd", "hd", "veryhigh", "high", "medium", "low"]
                for mime_type in mime_type_priorities:
                    for quality in quality_priorities:
                        for formitaet in formitaeten:
                            if formitaet.get("mimeType", "") == mime_type and formitaet.get("quality", "") == quality:
                                return formitaet.get("url", "")
        else:
            return ""

    def download(self, button: Optional[ui.button] = None):
        if not config.enable_server_download():
            ui.notify("Server download is not enabled!")
            return
        if button:
            button.disable()
        url = self.get_video_url()
        video_name = self.raw.get("document", self.raw).get("videoId", self.uid)
        file_extension = url.split(".")[-1]
        file_name = f"{video_name}.{file_extension}"
        path = self.raw.get("document", self.raw).get("brandTitle", "")
        if path:
            file_name = f"{path}/{file_name}"
        file_name = f"downloads/{file_name}"
        file_name.replace("//", "/")
        #thread = Thread(target=requester.download_file, args=(url, file_name))
        #thread.start()
        ui.notify(f"Download gestartet: {self.title}")

    def get_standalone_ui(self):
        if self.type == "category":
            i = 0
            for cluster_index, cluster in enumerate(self.raw.get("cluster", [])):
                html_elements = ""
                cl_name = cluster.get("name", "")
                if cl_name:
                    html_elements += f'<div class="q-card nicegui-card self-stretch place-content-center w-min"><div style="writing-mode: sideways-lr; text-orientation: sideways; font-weight: bold;">{cl_name}</div></div>'
                for element in self.get_teasers_from_cluster(cluster_index):
                    # element.get_preview_ui()
                    html_elements += element.get_preview_html()
                    i += 1
                ui.html(f'<div class="nicegui-row wrap">{html_elements}</div')

            print(f"Total elements: {i}")
        elif self.type == "video":
            brand = self.get_brand()
            with ui.row().classes("justify-center w-full"):
                # big central player with video, fit video to screen
                with ui.card().tight().classes("w-2/3 mr-auto ml-auto"):
                    extension = self.get_video_url().split(".")[-1]
                    ext_mime = {
                        "mp4": "video/mp4",
                        "m3u8": "application/x-mpegURL"
                    }
                    mime = ext_mime.get(extension, mimetypes.guess_type(self.get_video_url())[0])
                    ui.video(self.get_video_url(), autoplay=True, controls=True).props(f"type={mime}")
            with ui.row().classes("justify-center w-full items-stretch"):
                with ui.card().classes("w-1/3"):
                    with ui.column():
                        ui.label(self.title).classes("text-lg font-medium")
                        ui.label(self.description)
                        ui.label(self.long_description)
                if brand:
                    with ui.card().tight().classes("w-1/6"):
                        with ui.link(target=brand.get_internal_url()).classes("w-full h-full"):
                            ui.image(brand.get_img_url([380, 384, 314])).classes("w-full h-full rounded")
                with ui.card().classes("w-1/6"):
                    with ui.row().classes("w-full h-full justify-center items-center"):
                        with ui.element("a").props(f"href={self.get_video_url()} download"):
                            ui.button(icon="file_download")
                        if config.enable_server_download():
                            ui.button(icon="cloud_download", on_click=self.download)
                        ui.button(icon="content_copy")
                with ui.card().tight().classes("w-2/3"):
                    with ui.expansion("Raw Data").classes("w-full"):
                        ui.json_editor({'content': {'json': self.raw}}).classes("w-full")
        elif self.type == "brand":
            with ui.row().classes("justify-center w-full"):
                ui.label(self.title).classes("text-xl font-medium")
            for cluster_index, cluster in enumerate(self.raw.get("cluster", [])):
                with ui.row().classes("w-full"):
                    cl_name = cluster.get("name", "")
                    if cl_name:
                        with ui.card().classes("self-stretch place-content-center w-min"):
                            ui.label(cl_name).style(
                                "writing-mode: sideways-lr; text-orientation: sideways; font-weight: bold;")
                    for element in self.get_teasers_from_cluster(cluster_index):
                        element.get_preview_ui()
        else:
            html_elements = ""
            for element in self.get_children_pool():
                html_elements += element.get_preview_html()
            ui.html(f'<div class="nicegui-row wrap">{html_elements}</div')

    @staticmethod
    def load(uid: str) -> "Node":
        return Node(requester.get_id(uid))
