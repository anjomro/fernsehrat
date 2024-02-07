from contextlib import contextmanager

from nicegui import ui


@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
    with ui.header().classes('justify-between items-center text-white'):
        with ui.link(target="/"):
            ui.button('Fernsehrat', icon="home").props('flat color=white')
        with ui.row():
            with ui.link(target="/doc/sendungen-100"):
                ui.button('A-Z', icon="format_list_numbered").props('flat color=white')
            with ui.link(target="/doc/filme-104"):
                ui.button('Filme', icon="movie").props('flat color=white')
            with ui.link(target="/doc/serien-100"):
                ui.button('Serien', icon="dvr").props('flat color=white')
        ui.button(icon='menu').props('flat color=white')
    yield