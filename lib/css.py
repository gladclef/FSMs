import tinycss
import re

def css_get_size(selector):
    parser = tinycss.make_parser()
    ss = parser.parse_stylesheet_file("static/main.css")
    table_css = list(filter(lambda r: r.selector.as_css() == selector, ss.rules))[0]

    width_dec = list(filter(lambda d: d.name == "width", table_css.declarations))[0]
    height_dec = list(filter(lambda d: d.name == "height", table_css.declarations))[0]
    width = int(re.findall(r'\d+', width_dec.value.as_css())[0])
    height = int(re.findall(r'\d+', height_dec.value.as_css())[0])

    return width, height