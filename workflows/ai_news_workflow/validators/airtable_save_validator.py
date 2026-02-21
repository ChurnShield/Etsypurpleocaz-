"""
Airtable Save Validator
========================
Checks that articles were successfully saved to Airtable.

Runs after SaveToAirtableTool to confirm the API calls worked
and the expected number of records were created.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_validator import BaseValidator


class AirtableSaveValidator(BaseValidator):
    """Validates that the Airtable save completed successfully."""

    def validate(self, data, context=None) -> dict:
        """
        Check that articles were saved to Airtable.

        Args:
            data: The tool result dict from SaveToAirtableTool.
                  Expected: {'success': True, 'data': {'saved_count': N, ...}, ...}
            context: Optional dict with 'expected_count' (how many we tried to save).

        Returns:
            Standard validator result dict.
        """
        issues = []

        # Handle tool result dict
        if isinstance(data, dict):
            save_result = data.get('data') or {}
            tool_success = data.get('success', False)
            tool_error = data.get('error')
        else:
            save_result = {}
            tool_success = False
            tool_error = "Unexpected data format"

        # Check 1: Did the tool report success?
        if not tool_success:
            issues.append(f"Save tool failed: {tool_error or 'unknown error'}")

        # Check 2: Were any records saved?
        saved_count = save_result.get('saved_count', 0) if isinstance(save_result, dict) else 0

        if tool_success and saved_count == 0:
            issues.append("Tool reported success but saved 0 records")

        # Check 3: Did we save the expected number? (if context tells us)
        if context and 'expected_count' in context:
            expected = context['expected_count']
            if saved_count < expected:
                issues.append(
                    f"Only saved {saved_count} of {expected} articles"
                )

        passed = len(issues) == 0

        return {
            'passed': passed,
            'issues': issues,
            'needs_more': not passed,
            'validator_name': self.get_name(),
            'metadata': {
                'saved_count': saved_count,
                'tool_success': tool_success,
            }
        }
