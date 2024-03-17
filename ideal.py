from datetime import datetime

def ideal_consumption(date, temp_range, not_at_home_periods, current_temp, external_temp):
    not_at_home = any(is_within_time_range(date, period) for period in not_at_home_periods) 
    
    if not_at_home:
        # User is not at home, so ideal consumption is minimal (adjust based on your system)
        return 0.032  # kWh (assuming minimal consumption when not at home)
    elif temp_range.min > current_temp: 
        return get_time_on(current_temp, external_temp, temp_range.min) * 2.5
    elif temp_range.max < current_temp: 
        return get_time_on(current_temp, external_temp, temp_range.max) * 2.5
    else: return 0.270

def is_within_time_range(current_time, time_period):
    """Checks if a given time falls within a time period."""
    start_time = datetime.strptime(time_period["start_time"], "%H:%M")  
    end_time = datetime.strptime(time_period["end_time"], "%H:%M")  

    return start_time.hour <= current_time.hour <= end_time.hour


def get_time_on(current_temp, external_temp, optimal):
    return 1.1 * abs(current_temp - external_temp) * 0.25 * abs(current_temp - optimal) #h