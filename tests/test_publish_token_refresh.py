"""Tests for proactive OAuth token refresh in PublishListingsTool."""

import json
import os
import sys
import time
import tempfile
import urllib.error

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from unittest.mock import patch, MagicMock
from workflows.auto_listing_creator.tools.publish_listings_tool import PublishListingsTool


def _make_token_file(tmpdir, access_token="tok_abc", refresh_token="ref_xyz",
                     expires_at=None, expires_in=None):
    """Create a temporary token file and return its path."""
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    if expires_at is not None:
        tokens["expires_at"] = expires_at
    if expires_in is not None:
        tokens["expires_in"] = expires_in
    path = os.path.join(tmpdir, "etsy_tokens.json")
    with open(path, "w") as f:
        json.dump(tokens, f)
    return path


class TestProactiveTokenRefresh:
    """Proactive refresh: token refreshed before expiry, not on 401."""

    def test_token_near_expiry_triggers_proactive_refresh(self, tmp_path):
        """Token expiring within buffer window should refresh without API call."""
        tool = PublishListingsTool()
        # Token expires in 60 seconds — within the 300s buffer
        expires_at = time.time() + 60
        token_file = _make_token_file(tmp_path, expires_at=expires_at)

        new_tokens = {
            "access_token": "tok_refreshed",
            "refresh_token": "ref_new",
            "expires_in": 3600,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            # First call: refresh endpoint returns new tokens
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(new_tokens).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_refreshed"
        # Verify the token file was updated with expires_at
        with open(token_file) as f:
            saved = json.load(f)
        assert saved["access_token"] == "tok_refreshed"
        assert "expires_at" in saved
        assert saved["expires_at"] > time.time()

    def test_token_not_near_expiry_skips_refresh(self, tmp_path):
        """Token with plenty of time left should validate via API, not refresh."""
        tool = PublishListingsTool()
        # Token expires in 1 hour — well outside the 300s buffer
        expires_at = time.time() + 3600
        token_file = _make_token_file(tmp_path, expires_at=expires_at)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Validation call succeeds
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_abc"
        # Only one call (validation), no refresh
        assert mock_urlopen.call_count == 1

    def test_expired_token_triggers_proactive_refresh(self, tmp_path):
        """Token already expired should refresh proactively."""
        tool = PublishListingsTool()
        # Token expired 10 minutes ago
        expires_at = time.time() - 600
        token_file = _make_token_file(tmp_path, expires_at=expires_at)

        new_tokens = {
            "access_token": "tok_fresh",
            "refresh_token": "ref_fresh",
            "expires_in": 3600,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(new_tokens).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_fresh"

    def test_no_expires_at_falls_back_to_validation(self, tmp_path):
        """Token file without expires_at should validate via API call."""
        tool = PublishListingsTool()
        # No expires_at in token file — legacy format
        token_file = _make_token_file(tmp_path)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_abc"

    def test_proactive_refresh_failure_falls_back_to_validation(self, tmp_path):
        """If proactive refresh fails, still try the existing token."""
        tool = PublishListingsTool()
        # Token expiring soon
        expires_at = time.time() + 30
        token_file = _make_token_file(tmp_path, expires_at=expires_at)

        call_count = [0]

        def side_effect(req, timeout=None):
            call_count[0] += 1
            if call_count[0] == 1:
                # Refresh call fails
                raise urllib.error.URLError("network error")
            # Validation call succeeds (token still valid for a few seconds)
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=side_effect):
            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_abc"

    def test_refresh_persists_expires_at(self, tmp_path):
        """_try_refresh should compute and save expires_at from expires_in."""
        tool = PublishListingsTool()
        tokens = {"access_token": "old", "refresh_token": "ref_xyz"}
        token_file = os.path.join(tmp_path, "etsy_tokens.json")
        with open(token_file, "w") as f:
            json.dump(tokens, f)

        new_tokens = {
            "access_token": "tok_new",
            "refresh_token": "ref_new",
            "expires_in": 7200,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(new_tokens).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = tool._try_refresh(tokens, "keystring:secret", token_file)

        assert result == "tok_new"
        with open(token_file) as f:
            saved = json.load(f)
        assert "expires_at" in saved
        # Should be roughly now + 7200 (within 5 seconds tolerance)
        assert abs(saved["expires_at"] - (time.time() + 7200)) < 5


class TestReactive401Refresh:
    """Reactive refresh: 401 error triggers token refresh as fallback."""

    def test_401_triggers_refresh(self, tmp_path):
        """401 from validation should attempt refresh."""
        tool = PublishListingsTool()
        # Token with far-future expiry so proactive check passes
        expires_at = time.time() + 9999
        token_file = _make_token_file(tmp_path, expires_at=expires_at)

        call_count = [0]
        new_tokens = {
            "access_token": "tok_after_401",
            "refresh_token": "ref_after_401",
            "expires_in": 3600,
        }

        def side_effect(req, timeout=None):
            call_count[0] += 1
            if call_count[0] == 1:
                # Validation returns 401
                err = urllib.error.HTTPError(
                    req.full_url, 401, "Unauthorized", {}, None
                )
                raise err
            # Refresh call succeeds
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(new_tokens).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=side_effect):
            result = tool._load_access_token(token_file, "keystring:secret")

        assert result == "tok_after_401"
