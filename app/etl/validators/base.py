from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseValidator(ABC):
    """Abstract base class for ETL validators."""

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> bool:
        """Return True if record is valid, False otherwise."""
        raise NotImplementedError()
