---
name: tool-creator
description: "Creates new tools and validators following project conventions. Use when
              adding a new tool, validator, or extending an existing workflow with new steps."
---

## Tool Creation Protocol

When creating a new tool:

1. Read `docs/architecture/03-tool-patterns.md` for the full pattern
2. Read `lib/orchestrator/base_tool.py` to understand the ABC contract
3. Create the tool file in the appropriate workflow's `tools/` directory
4. Use `snake_case.py` naming (e.g., `my_new_tool.py`)

## Required Tool Structure

```python
from lib.orchestrator.base_tool import BaseTool
from lib.orchestrator.execution_logger import ExecutionLogger
from config import RELEVANT_CONFIG_VALUES

class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__(tool_name="my_new_tool")

    def execute(self, **kwargs):
        logger = ExecutionLogger(workflow="workflow_name", tool="my_new_tool")
        try:
            # Tool logic here
            result = self._do_work(**kwargs)
            logger.log_success(metadata={"key": "value"})
            return {
                "success": True,
                "data": result,
                "error": None,
                "tool_name": self.tool_name,
                "metadata": {}
            }
        except Exception as e:
            logger.log_error(str(e))
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.tool_name,
                "metadata": {}
            }
        finally:
            logger.flush()  # NEVER skip this
```

## Validator Creation

Follow `docs/architecture/04-validator-patterns.md` and extend `BaseValidator`.
Return: `{passed, issues, needs_more, validator_name, metadata}`

## After Creation
- Add a test file in `tests/test_{tool_name}.py`
- Run `pytest tests/ -v` to verify
- Wire the tool into the workflow's phase configuration
