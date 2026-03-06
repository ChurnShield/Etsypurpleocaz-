from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseValidator(ABC):
    """Base class for all validators.

    Every validator returns a standard dict with:
    - passed: Did it meet the threshold?
    - issues: What problems were found?
    - needs_more: Should the Orchestrator retry?
    """

    @abstractmethod
    def validate(self, data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Returns:
            {
                'passed': bool,
                'issues': List[str],
                'needs_more': bool,
                'validator_name': str,
                'metadata': Dict[str, Any]
            }
        """
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
