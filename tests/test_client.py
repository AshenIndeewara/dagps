import pytest
from datetime import date, datetime, timezone, timedelta

from app.client import (
    between,
    day_end_ms,
    day_ms,
    local_today,
    parse,
    stay_seconds,
    to_dicts,
)


class TestBetween:
    def test_found(self):
        assert between("abc login_id=123&xyz", "login_id=", "&") == "123"

    def test_not_found(self):
        assert between("no match", "x", "y") == ""


class TestDateFunctions:
    def test_day_ms(self):
        today = date(2024, 1, 1)
        ms = day_ms(today)
        assert ms > 0

    def test_day_end_ms(self):
        today = date(2024, 1, 1)
        assert day_end_ms(today) == day_ms(today + timedelta(days=1)) - 1000

    def test_local_today(self):
        result = local_today()
        assert isinstance(result, date)


class TestStaySeconds:
    def test_full(self):
        assert stay_seconds("10Hour40Minute18Second") == 10 * 3600 + 40 * 60 + 18

    def test_partial(self):
        assert stay_seconds("5Minute30Second") == 5 * 60 + 30

    def test_hour_only(self):
        assert stay_seconds("1Hour") == 3600

    def test_empty(self):
        assert stay_seconds("") == 0


class TestToDicts:
    def test_conversion(self):
        data = {
            "key": {"id": 0, "name": 1, "speed": 2},
            "records": [["dev1", "Vehicle1", "50.5"]]
        }
        result = to_dicts(data)
        assert len(result) == 1
        assert result[0]["id"] == "dev1"
        assert result[0]["name"] == "Vehicle1"
        assert result[0]["speed"] == 50.5


class TestParse:
    def test_plain_json(self):
        assert parse('{"key": "value"}') == {"key": "value"}

    def test_jsonp(self):
        assert parse('DFRAME.selectCustBack({"key": "value"})') == {"key": "value"}

    def test_jsonp_with_semicolon(self):
        assert parse('cb({"key": "value"});') == {"key": "value"}
