from enum import Enum

import requests
import urllib.parse
import os
import logging
import json

from langchain_core.messages.tool import tool_call
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from function_registry import ai_function, AIFunctionParameter

logger = logging.getLogger(__name__)

facility_id = 124851
project_id = 114051


def get_attribute_value(asset, name: str):
    for attribute in asset["attributes"]:
        if attribute["name"] == name:
            return attribute["value"]


def get_floor_id(name: str) -> int:
    register = {
        "1. Obergeschoss": 126803,
        "2. Obergeschoss": 126804,
        "Erdgeschoss": 126802,
        "Dachgeschoss": 159901,
        "Untergeschoss": 126801,
    }
    return register[name]


def get_possible_floors() -> list[str]:
    values = [
        "1. Obergeschoss",
        "2. Obergeschoss",
        "Erdgeschoss",
        "Dachgeschoss",
        "Untergeschoss",
    ]
    return values


def get_possible_component_types() -> list[str]:
    return [
        "IfcWindow",
        "IfcDoor"
    ]


# @ai_function(params=[
#     AIFunctionParameter("asset_component_type", get_possible_component_types()),
#     AIFunctionParameter("floor", get_possible_floors())
# ])
# def calculate_m2_for_asset_components(asset_component_type: str = None, floor: str = None):
#     """
#     calculate the square meters of an asset component
#     :param asset_component_type: the ifc standard component type
#     :param floor: floor of the building where the asset component is located
#     :return: square meters of all asset components
#     """
#     url = f"https://etl.libal-tech.de/api/asset-components?page=0&size=2000&extObject.equals={asset_component_type}&owningFacilityId.equals={facility_id}&entityFetch.equals=ATTRIBUTES&sort=id,asc"
#     if floor:
#         logger.info(f"Calculating m2 for: {get_floor_id(floor)}")
#         url += f"&floorId.equals={get_floor_id(floor)}"
#
#     response = requests.get(
#         url,
#         headers={
#             'accept': 'application/json, text/plain, */*',
#             'X-API-KEY': os.getenv("LIBAL_API"),
#             'X-Project-Id': str(project_id),
#             'content-type': 'application/json'
#         }
#     )
#
#     square_meter = 0
#     for asset in response.json():
#         area = get_attribute_value(asset, "Area")
#         if area:
#             square_meter += float(area.replace(",", "."))
#         else:
#             height = get_attribute_value(asset, "Height")
#             width = get_attribute_value(asset, "Width")
#             if not height:
#                 height = get_attribute_value(asset, "Höhe")
#             if not width:
#                 width = get_attribute_value(asset, "Breite")
#             if height and width:
#                 square_meter += float(height.replace(",", ".")) * float(width.replace(",", "."))
#     return square_meter

FLOOR_ID = {
    "1. Obergeschoss": 126_803,
    "2. Obergeschoss": 126_804,
    "Erdgeschoss":     126_802,
    "Dachgeschoss":    159_901,
    "Untergeschoss":   126_801,
}

# ----------------- Enums für Pydantic‑Schema -------------------------------
class ComponentEnum(str, Enum):
    IfcWindow = "IfcWindow"
    IfcDoor   = "IfcDoor"

class FloorEnum(str, Enum):
    OG1 = "1. Obergeschoss"
    OG2 = "2. Obergeschoss"
    EG  = "Erdgeschoss"
    DG  = "Dachgeschoss"
    UG  = "Untergeschoss"

class CalcM2Input(BaseModel):
    asset_component_type: ComponentEnum  = Field(..., description="the ifc standard component type")
    floor: FloorEnum = Field(..., description="floor of the building where the asset component is located")

@tool(
    args_schema=CalcM2Input,
    name_or_callable="calculate_m2_for_asset_components",
)
def calculate_m2_for_asset_components(asset_component_type: str = None, floor: str = None):
    """
    calculate the square meters of an asset component
    :param asset_component_type: the ifc standard component type
    :param floor: floor of the building where the asset component is located
    :return: square meters of all asset components
    """
    url = f"https://etl.libal-tech.de/api/asset-components?page=0&size=2000&extObject.equals={asset_component_type}&owningFacilityId.equals={facility_id}&entityFetch.equals=ATTRIBUTES&sort=id,asc"
    if floor:
        logger.info(f"Calculating m2 for: {get_floor_id(floor)}")
        url += f"&floorId.equals={get_floor_id(floor)}"

    response = requests.get(
        url,
        headers={
            'accept': 'application/json, text/plain, */*',
            'X-API-KEY': os.getenv("LIBAL_API"),
            'X-Project-Id': str(project_id),
            'content-type': 'application/json'
        }
    )

    square_meter = 0
    for asset in response.json():
        area = get_attribute_value(asset, "Area")
        if area:
            square_meter += float(area.replace(",", "."))
        else:
            height = get_attribute_value(asset, "Height")
            width = get_attribute_value(asset, "Width")
            if not height:
                height = get_attribute_value(asset, "Höhe")
            if not width:
                width = get_attribute_value(asset, "Breite")
            if height and width:
                square_meter += float(height.replace(",", ".")) * float(width.replace(",", "."))
    return square_meter