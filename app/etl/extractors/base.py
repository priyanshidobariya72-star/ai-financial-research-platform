from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable


class BaseExtractor(ABC):
    """Abstract base class for ETL extractors."""

    @abstractmethod
    async def fetch(self, symbols: Iterable[str]) -> Iterable[Dict[str, Any]]:
        """Fetch raw records for given symbols asynchronously."""
        raise NotImplementedError()
