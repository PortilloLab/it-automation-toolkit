"""
Base Connector interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConnector(ABC):
    """
    Abstract base class for all ITAT connectors.
    """

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the remote endpoint or service is reachable.
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send data to the target endpoint.
        """
        raise NotImplementedError
