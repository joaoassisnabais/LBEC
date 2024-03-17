from datetime import datetime
from collections import namedtuple
from ideal import ideal_consumption, is_within_time_range

# Define a namedtuple to represent temperature ranges
TempRange = namedtuple("TempRange", ["min", "max"])

def test_ideal_consumption():
    # Test case 1: User is not at home
    assert ideal_consumption(datetime(2024, 3, 18, 12),TempRange(20, 25), [{"start_time": "09:00", "end_time": "17:00"}], 22, 18) == 0.032

    # Test case 2: Current temperature within the ideal range
    assert ideal_consumption(datetime(2024, 3, 18, 6),TempRange(20, 25), [{"start_time": "00:00", "end_time": "06:00"}], 23, 18) == 0.032

    # Test case 3: Current temperature outside the ideal range
    assert ideal_consumption(datetime(2024, 3, 18, 15),TempRange(20, 25), [{"start_time": "00:00", "end_time": "06:00"}], 18, 25) == 1.1 * abs(18 - 25) * 0.25 * (18-20)

def test_is_within_time_range():
    # Test case 1: Current time within the time period
    assert is_within_time_range(datetime.strptime("05:00", "%H:%M"), {"start_time": "00:00", "end_time": "06:00"}) == True

    # Test case 2: Current time outside the time period
    assert is_within_time_range(datetime.strptime("08:00", "%H:%M"), {"start_time": "00:00", "end_time": "06:00"}) == False

if __name__ == "__main__":
    test_ideal_consumption()
    test_is_within_time_range()
    print("All tests passed.")