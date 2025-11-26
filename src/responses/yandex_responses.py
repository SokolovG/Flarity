from msgspec import Struct


class _YandexMessageDict(Struct):
    role: str
    text: str


class _YandexAlternativesDict(Struct):
    message: _YandexMessageDict
    status: str


class _YandexUsageDict(Struct):
    inputTextTokens: str
    completionTokens: str
    totalTokens: str


class _YandexResultDict(Struct):
    alternatives: list[_YandexAlternativesDict]
    usage: _YandexUsageDict
    modelVersion: str


class YandexResponse(Struct):
    result: _YandexResultDict
