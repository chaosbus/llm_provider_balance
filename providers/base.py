from abc import ABC, abstractmethod

import requests


class BaseProvider(ABC):
    """Base class for LLM provider API clients."""

    name: str = ""
    base_url: str = ""

    def __init__(self, api_key: str):
        self.api_key = api_key or ""
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    @abstractmethod
    def fetch_balance(self) -> dict:
        """Return {'primary': str, 'items': list[tuple[str, str]]}."""
        ...

    @abstractmethod
    def fetch_models(self) -> list[str]:
        """Return list of model ID strings."""
        ...
