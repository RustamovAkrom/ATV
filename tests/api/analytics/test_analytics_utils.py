import pytest
from fastapi import HTTPException

from api.v1.analytics._utils import (
    parse_optional_datetime,
    sanitize_search,
)


class TestAnalyticsUtils:
    def test_parse_optional_datetime_invalid(self):
        with pytest.raises(HTTPException) as exc:
            parse_optional_datetime("invalid-date")
        assert exc.value.status_code == 422

    def test_sanitize_search_special_chars(self):
        result = sanitize_search("test%with%wildcards")
        assert result == "test with wildcards"
        assert "%" not in result

    def test_sanitize_search_empty(self):
        assert sanitize_search("   ") is None
        assert sanitize_search("") is None
