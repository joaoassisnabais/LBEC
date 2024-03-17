from datetime import datetime

class Event:
    def __init__(self, title, date, description):
        self.title = title
        self.date = date
        self.description = description
        
        if not isinstance(date, datetime):
            raise ValueError
    
        
class Calendar:
    def __init__(self):
        self.events = {}

    def add_event(self, event):
        # Verifica evento
        if not isinstance(event, Event):
            raise ValueError
        key = self.get_key(event)
        if key not in self.events:  # Initialize list for new keys
            self.events[key] = []
        self.events[key].append(event)  # Correct append syntax
        
    def remove_event(self, event):
        
        if isinstance(event, Event):
            # Remove by reference (object)
            key = self.get_key(event)
            try:
                self.events[key].remove(event)
                if not self.events[key]:  # if empty day
                    del self.events[key]  
            except (KeyError, ValueError):
                raise ValueError
    
    def get_key(self, event):
        return (event.date.month,event.date.day)
      

        
        