"""Edition themes for the Peace by Page journal engine (folder: calm-pages).

A theme is everything that makes an edition look and sound like itself: the series title,
palette, art module (accents, cover art, coloring designs, mood tracker cells) and the
flavor text. The page layouts in build_journal.py and the product builder in
build_products.py read only from the active theme, so a new edition is a new theme module.

    import themes
    T = themes.get("petals")      # "wings", "petals" or "nights"

Each theme module (theme_<key>.py) defines THEME = Theme(...).
"""
import importlib

from reportlab.lib.colors import HexColor

# The umbrella brand (chosen 10/2). Change it here and rebuild.
BRAND = "Peace by Page"

KEYS = ("wings", "petals", "nights")


def colors(palette):
    return {k: HexColor(v) for k, v in palette.items()}


class Theme:
    """A bag of attributes. Required ones are listed in REQUIRED; see theme_wings.py for a full example."""

    REQUIRED = (
        "key", "slug", "title", "subtitle", "file_prefix", "palette", "img",
        "accent", "cover_art", "lifecycle", "exhale", "exhale_center", "sos_coloring", "weekly",
        "weekly_titles", "mood_cells", "rating_icon", "coloring_pack", "pack_covers", "image_art",
        "txt", "content", "mock",
    )

    def __init__(self, **kw):
        missing = [k for k in self.REQUIRED if k not in kw]
        if missing:
            raise ValueError(f"theme is missing {missing}")
        # defaults
        self.brand_mark = False          # draw the umbrella brand on covers and listing images
        self.store = None                # store name used in printed help text; None = neutral wording
        self.extra_sos = []              # extra SOS page names (after "This will pass")
        self.confidence = ["fear_ladder", "ladder_log", "lift_menu", "wind_down", "values_page", "worry_time"]
        self.subtitle_personal = "A 90-Day Journal for {name}"
        self.file_personal = self.file_generic = None
        self.__dict__.update(kw)
        self.colors = colors(self.palette)
        if self.file_generic is None:
            self.file_generic = f"{self.file_prefix}_90_Day_Anxiety_Journal.pdf"
        if self.file_personal is None:
            self.file_personal = self.file_prefix + "_{name}.pdf"

    @property
    def brand(self):
        return BRAND


_cache = {}


def get(key):
    if isinstance(key, Theme):
        return key
    key = key.replace("calm-", "")
    if key not in _cache:
        _cache[key] = importlib.import_module(f"theme_{key}").THEME
    return _cache[key]
