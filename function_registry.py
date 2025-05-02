from abc import ABC, abstractmethod
from enum import Enum
import json
import inspect
import logging
import re
from typing import Callable

from parser import DocStringParser

decorated_ai_functions = {}


class AIFunctionParameter(object):
    def __init__(self, name: str, enum: list[str] = None):
        self._name = name
        self._enum = enum

    @property
    def name(self) -> str:
        return self._name

    @property
    def enum(self) -> list[str]:
        return self._enum


def ai_function(params: list[AIFunctionParameter] = None):
    def decorator(func):
        decorated_ai_functions[func.__name__] = {
            'callable': func,
            'params': {p.name: p for p in params} if params is not None else {}
        }
        return func

    return decorator


class FunctionRegistry:
    def __init__(self, docstring_parser: DocStringParser):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._docstring_parser = docstring_parser
        self._functions = {}
        self._type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            Enum: "string",
            inspect.Parameter.empty: "any"
        }

    def register_function(self, function: Callable, params: dict = None):
        if not callable(function):
            raise ValueError("Function must be callable")
        if function.__name__ in self._functions:
            self.logger.warning(f"Function {function.__name__} already registered and will be overwritten")
        self._functions[function.__name__] = {
            "callable": function,
            "description": self._get_tool_description(function, params)
        }

    def register_decorated_functions(self):
        for name, func_desc in decorated_ai_functions.items():
            self.logger.debug(f"registering function '{name}'")
            self.register_function(func_desc["callable"], func_desc["params"])

    def call_function(self, function_name, **kwargs):
        self.logger.debug(f"Calling function '{function_name}'")
        return self._functions[function_name]["callable"](**kwargs)

    def _map_type(self, python_type) -> str:
        for py_type, mapped_type in self._type_mapping.items():
            if issubclass(python_type, py_type):
                return mapped_type
        raise ValueError("Function has unknown parameter type")

    def _get_tool_description(self, func: Callable, params: dict[str, AIFunctionParameter] = None) -> dict:
        tool = {}
        signature = inspect.signature(func)
        tool["name"] = func.__name__
        tool["description"] = ""
        tool["parameters"] = {}
        tool["parameters"]["type"] = "object"
        tool["parameters"]["properties"] = {}
        tool["parameters"]["required"] = []
        for param_name, param in inspect.signature(func).parameters.items():
            tool["parameters"]["properties"][param_name] = {}
            tool["parameters"]["properties"][param_name]["type"] = self._map_type(param.annotation)
            if param_name in params and params[param_name].enum:
                tool["parameters"]["properties"][param_name]["enum"] = params[param_name].enum
            if issubclass(param.annotation, Enum):
                tool["parameters"]["properties"][param_name]["enum"] = list(param.annotation.__members__.keys())

            if param.default is inspect.Parameter.empty:
                tool["parameters"]["required"].append(param_name)
        if func.__doc__:
            tool["description"] = self._docstring_parser.get_description(func)
            for param_name, param in inspect.signature(func).parameters.items():
                tool["parameters"]["properties"][param_name][
                    "description"] = self._docstring_parser.get_parameter_description(func, param_name)
        else:
            self.logger.warning(f"No docstring found for function {func.__name__}")

        return {"type": "function", "function": tool}

    def get_tools(self):
        self.logger.debug(json.dumps([value["description"] for key, value in self._functions.items()], indent=4))
        return [value["description"] for key, value in self._functions.items()]
