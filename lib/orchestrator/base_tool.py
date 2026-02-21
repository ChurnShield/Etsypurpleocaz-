from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Base class for all tools.

    Every tool returns a standard dict with:
    - success: Did the tool execute without error?
    - data: The result payload
    - error: Error message if failed
    """

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Returns:
            {
                'success': bool,
                'data': Any,
                'error': Optional[str],
                'tool_name': str,
                'metadata': Dict[str, Any]
            }
        """
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
