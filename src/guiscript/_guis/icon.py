import pygame
import typing
import warnings
import requests
import threading
import io
if typing.TYPE_CHECKING:
    from .components import UIIconComp

_empty = pygame.Surface((1, 1), pygame.SRCALPHA)
_empty.fill(0)


def _download_add(name: str, url: str, is_async: bool = False):
    response = requests.request("get", url)
    if not response.ok:
        warnings.warn(
            f"Request for icon '{name}' at url '{url}' failed with status code '{response.status_code}'", category=UserWarning)
    image = pygame.image.load(io.BytesIO(response.content)).convert_alpha()
    Icons.icons[name] = image
    if is_async:
        if name in Icons.adding_async:
            Icons.adding_async.remove(name)
        for icon_comp in Icons.rebuild_async:
            icon_comp._build(icon_comp.element.style)


class Icons:
    """Icon manager for the icon element component"""
    icons: dict[str, pygame.Surface] = {
        "empty": _empty
    }
    rebuild_async: list["UIIconComp"] = []
    adding_async: list[str] = []

    @classmethod
    def download(cls, name: str, url: str):
        """Download an icon from the internet"""
        _download_add(name, url, False)

    @classmethod
    def downloads(cls, **names_urls: str):
        """Download multiple icons from the internet"""
        for name, url in names_urls.items():
            cls.download(name, url)

    @classmethod
    def download_async(cls, name: str, url: str):
        """Download an icon from the internet but let the rest of the code execute, refreshing the icon component when it's ready"""
        cls.adding_async.append(name)
        thread = threading.Thread(None, _download_add, args=(name, url, True))
        thread.start()

    @classmethod
    def downloads_async(cls, **names_urls: str):
        """Download multiple icons from the internet but let the rest of the code execute, refreshing the icon components when it's ready"""
        for name, url in names_urls.items():
            cls.download_async(name, url)

    @classmethod
    def add(cls, name: str, surface: pygame.Surface):
        """Bind a surface icon to a name"""
        cls.icons[name] = surface

    @classmethod
    def adds(cls, **name_surfs: pygame.Surface):
        """Bind surfaces to icon names"""
        for name, surf in name_surfs.items():
            cls.add(name, surf)

    @classmethod
    def get(cls, name: str | None, icon_comp=None) -> pygame.Surface:
        """Get the icon surface from a name"""
        if name is None:
            return cls.icons["empty"]
        if name in cls.adding_async and icon_comp:
            cls.rebuild_async.append(icon_comp)
            return cls.icons["empty"]
        surf = cls.icons.get(name, None)
        if not surf:
            warnings.warn(
                f"No icon '{name}' was added, returing default", category=UserWarning)
            return cls.icons["empty"]
        return surf
