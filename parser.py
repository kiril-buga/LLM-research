# parsers.py
from abc import ABC, abstractmethod
from typing import Callable

from docstring_parser import parse


class DocStringParser(ABC):

    @abstractmethod
    def get_description(self, func: Callable) -> str:
        pass

    @abstractmethod
    def get_parameter_description(self, func: Callable, param_name: str) -> str:
        pass


class GoogleParser(DocStringParser):
    def get_description(self, func):
        doc = parse(func.__doc__ or "")
        return doc.short_description or ""

    def get_parameter_description(self, func, param):
        doc = parse(func.__doc__ or "")
        for p in doc.params:
            if p.arg_name == param:
                return p.description or ""
        return ""
