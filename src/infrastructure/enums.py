from enum import Enum


class TextType(str, Enum):
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    PLAIN = "PLAIN"
