"""
This module contains constants used in the DataformerApp base module.

Constants:
- STREAM_INFO_TEXT: A string representing the information about streaming the response from the model.
- NODE_FORMAT_ATTRIBUTES: A list of attributes used for formatting nodes.
- FIELD_FORMAT_ATTRIBUTES: A list of attributes used for formatting fields.
"""

import orjson

STREAM_INFO_TEXT = "Stream the response from the model. Streaming works only in Chat."

NODE_FORMAT_ATTRIBUTES = ["beta", "icon", "display_name", "description", "output_types"]


FIELD_FORMAT_ATTRIBUTES = [
    "info",
    "display_name",
    "required",
    "list",
    "multiline",
    "fileTypes",
    "password",
    "input_types",
    "title_case",
    "real_time_refresh",
    "refresh_button",
    "refresh_button_text",
    "options",
]

ORJSON_OPTIONS = orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS | orjson.OPT_OMIT_MICROSECONDS
