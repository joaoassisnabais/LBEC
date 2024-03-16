import datetime

class Resource:
    def __init__(self, price_per_unit, unit_type):
        if price_per_unit < 0:
            raise ValueError('Price per unit must be greater than 0')
        self.price_per_unit = price_per_unit    #In Euro
        self.unit_type = unit_type  #e.g. liters, kwh, etc.

class Energy(Resource):
    def __init__(self, price_per_unit=0.1537, unit_type='kwh'):
        super().__init__(price_per_unit, unit_type)
        
class Water(Resource):
    def __init__(self, price_per_unit = 0.7080, unit_type = 'm3'):
        super().__init__(price_per_unit, unit_type)

class Gas(Resource):
    def __init__(self, price_per_unit = 0.11270, unit_type = 'kwh'):
        super().__init__(price_per_unit, unit_type)
    
class Consumption:
    def __init__(self, resource, amount):
        self.resource = resource
        self.amount = amount
        self.timestamp = datetime.now()
        self.at_home = True

