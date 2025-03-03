""" 
Description: 
 - AiReport project.

History:
 - 2024/07/22 by Hysun (hysun.he@oracle.com): Created
"""

from urllib.parse import urlparse


def format_response_to_rows(query_json) -> str:
    query_json = ensure_list(query_json)
    if is_primitive(query_json[0]):
        return "\n".join(query_json)

    txt = ""
    for row in query_json:
        row_str = ""
        for k in row:
            row_str = f"{row_str}, {k}: {row[k]}" if row_str else f"{k}: {row[k]}"
        txt = txt + "\n" + row_str if txt else row_str
    return txt


def format_response_to_valuestring(query_json) -> str:
    query_json = ensure_list(query_json)
    if is_primitive(query_json[0]):
        return " | ".join(query_json)

    txt = ""
    for row in query_json:
        row_str = ""
        for k in row:
            row_str = f"{row_str} | {row[k]}" if row_str else f"{row[k]}"
        txt = txt + "\n" + row_str if txt else row_str
    return txt


def format_response_to_list(query_json: list[dict]) -> str:
    txt = ""
    for row in query_json:
        txt = txt + "\n" if txt else ""
        for k in row:
            txt = f"{txt}\n{k}: {row[k]}" if txt else f"{k}: {row[k]}"
    return txt


def format_response_to_table(query_json: list[dict]) -> str:
    html = "<table class='result_table'>"
    first_row = query_json[0]
    html = f"{html}<tr class='result_table_tr'>"
    for k in first_row:
        html = f"{html}<th class='result_table_th'>{k}</th>"
    html = f"{html}</tr>"

    for row in query_json:
        html = f"{html}<tr class='result_table_tr'>"
        for k in row:
            html = f"{html}<td class='result_table_td'>{row[k]}</td>"
        html = f"{html}</tr>"
    html = f"{html}</table>"
    return html


def is_empty_result(obj) -> bool:
    if not obj:
        return True
    query_json = ensure_list(obj)
    if "No data found" in query_json or "NO_DATA_FOUND" in query_json:
        return True
    return False


def is_primitive(obj):
    primitives = (bool, str, int, float)
    return isinstance(obj, primitives)


def ensure_list(obj):
    return obj if isinstance(obj, list) else [obj]


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def escape(text: str) -> str:
    return text.replace("'", "''").replace(":", "：")
