import pytest
from lib.orchestrator.base_validator import BaseValidator
from lib.orchestrator.base_tool import BaseTool


class MockValidator(BaseValidator):
    def validate(self, data, context=None):
        return {
            "passed": True,
            "issues": [],
            "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {}
        }


class MockTool(BaseTool):
    def execute(self, **kwargs):
        return {
            "success": True,
            "data": {"result": "success"},
            "error": None,
            "tool_name": self.get_name(),
            "metadata": {}
        }


def test_base_validator_implementation():
    validator = MockValidator()
    result = validator.validate({"test": "data"})
    
    assert result["passed"] is True
    assert result["issues"] == []
    assert result["validator_name"] == "MockValidator"


def test_base_tool_implementation():
    tool = MockTool()
    result = tool.execute(param="value")
    
    assert result["success"] is True
    assert result["data"]["result"] == "success"
    assert result["tool_name"] == "MockTool"


def test_validator_name():
    validator = MockValidator()
    assert validator.get_name() == "MockValidator"


def test_tool_name():
    tool = MockTool()
    assert tool.get_name() == "MockTool"
