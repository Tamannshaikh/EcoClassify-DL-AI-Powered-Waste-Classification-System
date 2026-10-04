"""
Abstract Base Class for Recycling Center Providers.
"""
from abc import ABC, abstractmethod
from typing import List
from backend.app.schemas import RecyclingCenterItem


class BaseRecyclingProvider(ABC):
    """
    Abstract interface for recycling center directory providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical provider name identifier."""
        pass

    @abstractmethod
    async def search(
        self,
        latitude: float,
        longitude: float,
        waste_type: str,
        radius_km: float,
        limit: int,
    ) -> List[RecyclingCenterItem]:
        """
        Search for recycling centers relevant to the given waste type near the origin coordinates.
        """
        pass
