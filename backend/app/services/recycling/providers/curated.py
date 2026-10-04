"""
Curated Regional Recycling Center Provider.

Serves as an offline, zero-config benchmark provider populated with verified
municipal dry waste centers, authorized e-waste collection points, composting units,
and scrap aggregators.
"""
from typing import List, Dict, Any
from backend.app.schemas import RecyclingCenterItem
from backend.app.services.recycling.distance import haversine_distance_km
from backend.app.services.recycling.providers.base import BaseRecyclingProvider


CURATED_FACILITIES: List[Dict[str, Any]] = [
    # E-Waste
    {
        "id": "curated_ewaste_001",
        "name": "Navi Mumbai Authorized E-Waste Collection Hub",
        "address": "Sector 19A, APMC Market Road, Vashi, Navi Mumbai, Maharashtra 400703",
        "latitude": 19.0772,
        "longitude": 72.9981,
        "phone": "+91 22 2789 1100",
        "opening_hours": "Mon-Sat: 09:00 AM - 06:00 PM",
        "categories": ["e_waste", "metal"],
    },
    {
        "id": "curated_ewaste_002",
        "name": "Mumbai E-Waste & Electronics Drop-off Center",
        "address": "Marol Industrial Area, Andheri East, Mumbai, Maharashtra 400093",
        "latitude": 19.1197,
        "longitude": 72.8826,
        "phone": "+91 22 2836 4400",
        "opening_hours": "Mon-Fri: 10:00 AM - 05:30 PM",
        "categories": ["e_waste", "metal"],
    },
    {
        "id": "curated_ewaste_003",
        "name": "Thane Regional E-Waste Recycling Unit",
        "address": "Wagle Industrial Estate, Thane West, Maharashtra 400604",
        "latitude": 19.1915,
        "longitude": 72.9510,
        "phone": "+91 22 2582 7700",
        "opening_hours": "Mon-Sat: 09:30 AM - 06:00 PM",
        "categories": ["e_waste"],
    },
    # Biodegradable / Organic
    {
        "id": "curated_bio_001",
        "name": "Navi Mumbai Municipal Bio-Composting & Wet Waste Plant",
        "address": "Turbhe MIDC Road, Sector 20, Turbhe, Navi Mumbai, Maharashtra 400705",
        "latitude": 19.0834,
        "longitude": 73.0162,
        "phone": "+91 22 2768 5520",
        "opening_hours": "Mon-Sun: 08:00 AM - 05:00 PM",
        "categories": ["biodegradable"],
    },
    {
        "id": "curated_bio_002",
        "name": "Bandra Wet Waste Composting & Biogas Facility",
        "address": "Near Bandra Reclamation, Bandra West, Mumbai, Maharashtra 400050",
        "latitude": 19.0434,
        "longitude": 72.8315,
        "phone": "+91 22 2642 8810",
        "opening_hours": "Mon-Sat: 08:30 AM - 04:30 PM",
        "categories": ["biodegradable"],
    },
    {
        "id": "curated_bio_003",
        "name": "Powai Community Organic Waste Processing Station",
        "address": "Hiranandani Gardens, Powai, Mumbai, Maharashtra 400076",
        "latitude": 19.1176,
        "longitude": 72.9060,
        "phone": "+91 22 2570 3344",
        "opening_hours": "Mon-Sat: 09:00 AM - 05:00 PM",
        "categories": ["biodegradable"],
    },
    # Plastic
    {
        "id": "curated_plastic_001",
        "name": "Navi Mumbai Dry Waste & Plastic Sorting Center",
        "address": "Sector 11, Kopar Khairane, Navi Mumbai, Maharashtra 400709",
        "latitude": 19.1021,
        "longitude": 73.0034,
        "phone": "+91 22 2754 1188",
        "opening_hours": "Mon-Sat: 09:00 AM - 06:30 PM",
        "categories": ["plastic", "cardboard", "paper"],
    },
    {
        "id": "curated_plastic_002",
        "name": "Mumbai Central PET & Rigid Plastic Recycling Depot",
        "address": "Dharavi Leather Goods & Scrap Sector, Mumbai, Maharashtra 400017",
        "latitude": 19.0410,
        "longitude": 72.8540,
        "phone": "+91 22 2407 9922",
        "opening_hours": "Mon-Sat: 08:30 AM - 07:00 PM",
        "categories": ["plastic"],
    },
    {
        "id": "curated_plastic_003",
        "name": "Goregaon Dry Waste Sorting & Plastic Collection Hub",
        "address": "SV Road, Goregaon West, Mumbai, Maharashtra 400104",
        "latitude": 19.1646,
        "longitude": 72.8465,
        "phone": "+91 22 2872 6655",
        "opening_hours": "Mon-Sat: 09:00 AM - 06:00 PM",
        "categories": ["plastic", "paper"],
    },
    # Cardboard & Paper
    {
        "id": "curated_paper_001",
        "name": "Vashi Industrial Paper & Cardboard Baler Depot",
        "address": "Sector 26, Vashi, Navi Mumbai, Maharashtra 400705",
        "latitude": 19.0689,
        "longitude": 72.9912,
        "phone": "+91 22 2788 4433",
        "opening_hours": "Mon-Sat: 09:00 AM - 06:00 PM",
        "categories": ["cardboard", "paper"],
    },
    {
        "id": "curated_paper_002",
        "name": "Kurla Recycled Paper & Packaging Scrap Hub",
        "address": "LBS Marg, Kurla West, Mumbai, Maharashtra 400070",
        "latitude": 19.0726,
        "longitude": 72.8845,
        "phone": "+91 22 2503 1290",
        "opening_hours": "Mon-Sat: 09:30 AM - 06:30 PM",
        "categories": ["cardboard", "paper"],
    },
    # Metal
    {
        "id": "curated_metal_001",
        "name": "Navi Mumbai Scrap Metal & Aluminum Recyclers",
        "address": "Pawane MIDC, TTC Industrial Area, Navi Mumbai, Maharashtra 400705",
        "latitude": 19.0945,
        "longitude": 73.0189,
        "phone": "+91 22 2761 9800",
        "opening_hours": "Mon-Sat: 08:30 AM - 06:00 PM",
        "categories": ["metal"],
    },
    {
        "id": "curated_metal_002",
        "name": "Sewri Metal Scrap & Can Recycling Depot",
        "address": "Harbour Road, Sewri, Mumbai, Maharashtra 400015",
        "latitude": 19.0012,
        "longitude": 72.8590,
        "phone": "+91 22 2413 5500",
        "opening_hours": "Mon-Sat: 09:00 AM - 05:30 PM",
        "categories": ["metal"],
    },
    # Glass
    {
        "id": "curated_glass_001",
        "name": "Thane Glass Bottle & Cullet Aggregators",
        "address": "Ghodbunder Road, Manpada, Thane West, Maharashtra 400607",
        "latitude": 19.2310,
        "longitude": 72.9750,
        "phone": "+91 22 2589 3311",
        "opening_hours": "Mon-Sat: 09:00 AM - 05:30 PM",
        "categories": ["glass"],
    },
    {
        "id": "curated_glass_002",
        "name": "Mumbai Glass Waste Collection Point",
        "address": "Reay Road, Mazgaon, Mumbai, Maharashtra 400010",
        "latitude": 18.9715,
        "longitude": 72.8480,
        "phone": "+91 22 2371 4422",
        "opening_hours": "Mon-Fri: 09:00 AM - 05:00 PM",
        "categories": ["glass"],
    },
    # Trash / General Municipal Transfer
    {
        "id": "curated_trash_001",
        "name": "Navi Mumbai Municipal Solid Waste Transfer Station",
        "address": "MIDC Sector 2, Shiravane, Nerul, Navi Mumbai, Maharashtra 400706",
        "latitude": 19.0345,
        "longitude": 73.0230,
        "phone": "+91 22 2770 1200",
        "opening_hours": "Mon-Sun: 07:00 AM - 07:00 PM",
        "categories": ["trash", "plastic", "metal", "cardboard", "paper"],
    },
    {
        "id": "curated_trash_002",
        "name": "Deonar Municipal Waste Transfer & Segregation Station",
        "address": "Ghatkopar-Mankhurd Link Road, Deonar, Mumbai, Maharashtra 400043",
        "latitude": 19.0620,
        "longitude": 72.9240,
        "phone": "+91 22 2556 7800",
        "opening_hours": "Mon-Sun: 06:00 AM - 08:00 PM",
        "categories": ["trash", "biodegradable"],
    },
]


class CuratedRecyclingProvider(BaseRecyclingProvider):
    """
    In-memory curated provider returning distance-sorted facilities matching the waste category.
    """

    @property
    def provider_name(self) -> str:
        return "curated"

    async def search(
        self,
        latitude: float,
        longitude: float,
        waste_type: str,
        radius_km: float,
        limit: int,
    ) -> List[RecyclingCenterItem]:
        results: List[RecyclingCenterItem] = []

        # Filter facilities that support the requested category
        for facility in CURATED_FACILITIES:
            if waste_type in facility["categories"]:
                dist = haversine_distance_km(
                    latitude, longitude, facility["latitude"], facility["longitude"]
                )

                # Filter within requested search radius
                if dist <= radius_km:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={facility['latitude']},{facility['longitude']}"
                    directions_url = (
                        f"https://www.google.com/maps/dir/?api=1"
                        f"&origin={latitude},{longitude}"
                        f"&destination={facility['latitude']},{facility['longitude']}"
                        f"&travelmode=driving"
                    )

                    item = RecyclingCenterItem(
                        id=facility["id"],
                        name=facility["name"],
                        address=facility["address"],
                        latitude=facility["latitude"],
                        longitude=facility["longitude"],
                        distance_km=dist,
                        maps_url=maps_url,
                        directions_url=directions_url,
                        phone=facility.get("phone"),
                        opening_hours=facility.get("opening_hours"),
                        waste_categories_handled=facility.get("categories"),
                        source="curated",
                    )
                    results.append(item)

        # Sort strictly ascending by distance (nearest first)
        results.sort(key=lambda x: x.distance_km)

        return results[:limit]
