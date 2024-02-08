from api import get_category, get_categories
from nicegui import ui

from node import Node
from ui.theme import frame


@ui.page("/")
def home():
    categories = get_categories()
    # Display categories as cards
    with frame("Home"):
        with ui.row():
            for category_id, category_title in categories.items():
                with ui.link(target=f"/doc/{category_id}"):
                    with ui.card().tight():
                        # ui.label(category_title)
                        ui.button(category_title)


def brand():
    pass


@ui.page("/doc/{document_id}")
def document(document_id: str):
    with frame("Document"):
        node = Node.load(document_id)
        node.get_standalone_ui()


ui.add_head_html('<meta name="referrer" content="same-origin" />')
ui.html('<meta name="referrer" content="same-origin" />')
ui.run(title="Fernsehrat", reload=False)
