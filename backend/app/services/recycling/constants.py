"""
Constants and waste category search mappings for Smart Recycling Center Finder.
"""
from typing import Dict, List, Set

# The 8 production waste categories
VALID_WASTE_TYPES: Set[str] = {
    "biodegradable",
    "cardboard",
    "e_waste",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash",
}

# Domain-specific keyword templates for external search queries
WASTE_SEARCH_TEMPLATES: Dict[str, List[str]] = {
    "biodegradable": [
        "organic waste composting center",
        "wet waste collection center",
        "composting plant",
        "organic waste recycling",
    ],
    "cardboard": [
        "cardboard recycling center",
        "paper packaging scrap dealer",
        "paper recycling facility",
    ],
    "e_waste": [
        "e-waste recycling center",
        "electronic waste collection center",
        "e-waste drop off point",
        "electronics recycling facility",
    ],
    "glass": [
        "glass recycling center",
        "glass bottle scrap dealer",
        "glass waste collection",
    ],
    "metal": [
        "scrap metal recycling center",
        "metal scrap dealer",
        "aluminum can collection recycling",
    ],
    "paper": [
        "paper recycling center",
        "waste paper collection center",
        "paper scrap dealer",
    ],
    "plastic": [
        "plastic recycling center",
        "plastic waste collection center",
        "dry waste sorting center",
    ],
    "trash": [
        "municipal waste management facility",
        "waste transfer station",
        "dry waste collection center",
    ],
}
