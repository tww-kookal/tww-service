class RoomNotAvailableException(Exception):    
    def __init__(self, message="Rooms Not Available"):
        self.message = message
        super().__init__(self.message) # Call the parent class's __init__

class UserNotAvailableException(Exception):    
    def __init__(self, message="Booking User Not Available"):
        self.message = message
        super().__init__(self.message) # Call the parent class's __init__
        
class CustomerNotAvailableException(Exception):    
    def __init__(self, message="Customer Not Available"):
        self.message = message
        super().__init__(self.message) # Call the parent class's __init__
