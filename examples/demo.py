from datetime import date, datetime, timezone, timedelta
from app.client import day_ms, day_end_ms, local_today, stay_seconds, to_dicts, between, parse

def test_between():
    text = "abc login_id=123&xyz"
    assert between(text, "login_id=", "&") == "123"
    assert between("no match", "x", "y") == ""
    print("[OK] between() works")

def test_date_functions():
    today = date(2024, 1, 1)
    ms = day_ms(today)
    assert ms > 0
    assert day_end_ms(today) == day_ms(today + timedelta(days=1)) - 1000
    print("[OK] date functions work")

def test_stay_seconds():
    assert stay_seconds("10Hour40Minute18Second") == 10 * 3600 + 40 * 60 + 18
    assert stay_seconds("5Minute30Second") == 5 * 60 + 30
    assert stay_seconds("1Hour") == 3600
    assert stay_seconds("") == 0
    print("[OK] stay_seconds() works")

def test_to_dicts():
    data = {
        "key": {"id": 0, "name": 1, "speed": 2},
        "records": [["dev1", "Vehicle1", "50.5"]]
    }
    result = to_dicts(data)
    assert len(result) == 1
    assert result[0]["id"] == "dev1"
    assert result[0]["name"] == "Vehicle1"
    assert result[0]["speed"] == 50.5
    print("[OK] to_dicts() works")

def test_parse():
    assert parse('{"key": "value"}') == {"key": "value"}
    assert parse('DFRAME.selectCustBack({"key": "value"})') == {"key": "value"}
    assert parse('cb({"key": "value"});') == {"key": "value"}
    print("[OK] parse() works")

if __name__ == "__main__":
    print("Running demo checks...\n")
    test_between()
    test_date_functions()
    test_stay_seconds()
    test_to_dicts()
    test_parse()
    print("\n[OK] All demo checks passed!")
