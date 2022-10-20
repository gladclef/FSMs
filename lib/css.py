from __future__ import annotations

import tinycss
import re

def css_get_size(selector: str) -> tuple[float|None, float|None]:
    parser = tinycss.make_parser()
    ss = parser.parse_stylesheet_file("static/main.css")
    table_css = list(filter(lambda r: r.selector.as_css() == selector, ss.rules))[0]

    width, height = None, None

    for wstr in ["width", "min-width", "max-width"]:
        width_decs = list(filter(lambda d: d.name == wstr, table_css.declarations))
        if len(width_decs) > 0:
            width = int(re.findall(r'\d+', width_decs[0].value.as_css())[0])
            break

    for hstr in ["height", "min-height", "max-height", "font-size"]:
        height_decs = list(filter(lambda d: d.name == hstr, table_css.declarations))
        if len(height_decs) > 0:
            height = int(re.findall(r'\d+', height_decs[0].value.as_css())[0])
            break

    return width, height
