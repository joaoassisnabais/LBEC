from datetime import datetime

def timestamp_to_string(timestamp, format="%Y-%m-%d %H:%M:%S"):
  """
  Converts a timestamp (either a Unix timestamp in seconds or a Python datetime object)
  to a formatted string.

  Args:
      timestamp: The timestamp to convert (int or datetime object).
      format (str, optional): The desired output format string using strftime directives.
          Defaults to "%Y-%m-%d %H:%M:%S" (YYYY-MM-DD HH:MM:SS).

  Returns:
      str: The formatted string representation of the timestamp.
  """

  if isinstance(timestamp, int):
    # Convert Unix timestamp (seconds) to datetime object
    timestamp = datetime.fromtimestamp(timestamp)

  # Ensure timestamp is a datetime object
  if not isinstance(timestamp, datetime):
    raise TypeError("timestamp must be an integer (Unix timestamp) or a datetime object")

  return timestamp.strftime(format)

class Resource:
    def __init__(self, price_per_unit, unit_type):
        if price_per_unit < 0:
            raise ValueError('Price per unit must be greater than 0')
        self.price_per_unit = price_per_unit    #In Euro
        self.unit_type = unit_type  #e.g. liters, kwh, etc.
    
    def get_price(self, amount):
        if amount < 0:
            raise ValueError('Amount must be greater than 0')
        return self.price_per_unit * amount
    
    def get_unit_type(self):
        return self.unit_type
    
    def get_price_per_unit(self):
        return self.price_per_unit

class Energy(Resource):
    def __init__(self, price_per_unit=0.1537, unit_type='kwh'):
        super().__init__(price_per_unit, unit_type)
        
class Water(Resource):
    def __init__(self, price_per_unit = 0.7080, unit_type = 'm3'):
        super().__init__(price_per_unit, unit_type)

class Gas(Resource):
    def __init__(self, price_per_unit = 0.1127, unit_type = 'kwh'):
        super().__init__(price_per_unit, unit_type)
    
class Consumption_Type:
    def __init__(self, resource, amount=0, at_home=True):
        self.resource = resource
        self.amount = amount
    
    def to_json(self):
        return {
            "amount": self.amount,
            "units": self.resource.unit_type,
            "price_per_unit": self.resource.price_per_unit
        }
    
class Consumption:
    def __init__(self, area, energy=0, water=0, gas=0 , at_home=True, timestamp=datetime.now()):
        self.area = area
        self.timestamp = timestamp
        self.at_home = at_home
        self.energy = Consumption_Type(Energy(), energy, at_home)
        self.water = Consumption_Type(Water(), water, at_home)
        self.gas = Consumption_Type(Gas(), gas, at_home)

        
    def to_json(self):
        return {
            "area": self.area,
            "timestamp": timestamp_to_string(self.timestamp),
            "energy": self.energy.to_json,
            "water": self.water.to_json,
            "gas": self.gas.to_json,
        }
