import pytest
from fastapi import HTTPException

from api.v1.analytics._utils import (
    parse_optional_datetime,
    parse_rate_limit,
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

    def test_parse_rate_limit_hour(self):
        amount, period = parse_rate_limit("100/hour")
        assert amount == 100
        assert period == 3600

    def test_parse_rate_limit_invalid_format(self):
        amount, period = parse_rate_limit("invalid")
        assert amount == 20
        assert period == 60
