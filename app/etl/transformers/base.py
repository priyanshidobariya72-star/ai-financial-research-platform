from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):
    """Abstract base class for ETL transformers."""

    @abstractmethod
    def transform(self, raw: dict[str, Any]) -> Any:
        """Transform raw extractor output into normalized dict for DB insertion."""
        raise NotImplementedError()
