import random
import time
from datetime import datetime

class DroneSimulator:
    """
    A class to simulate a drone for landmine detection operations.
    Provides realistic positioning and status information without requiring actual hardware.
    """
    
    def __init__(self, initial_lat=0.0, initial_lng=0.0, initial_altitude=10.0):
        """
        Initialize the drone simulator with starting position.
        
        Args:
            initial_lat (float): Initial latitude
            initial_lng (float): Initial longitude
            initial_altitude (float): Initial altitude in meters
        """
        # Position and orientation
        self.initial_lat = initial_lat
        self.initial_lng = initial_lng
        self.latitude = initial_lat
        self.longitude = initial_lng
        self.altitude = initial_altitude
        self.speed = 0.0
        self.heading = 0  # North
        
        # System status
        self.battery_level = 100
        self.signal_strength = 95
        self.last_update_time = time.time()
        self.is_flying = False
        
        # Flight characteristics
        self.max_speed = 10.0  # m/s
        self.max_altitude = 50.0  # meters
        self.min_altitude = 5.0   # meters
        self.movement_step = 0.0001  # Degrees (approx. 11 meters)
        
    def takeoff(self):
        """Simulate drone takeoff"""
        self.is_flying = True
        self.altitude = 10.0
        self.speed = 1.0
        
    def land(self):
        """Simulate drone landing"""
        self.is_flying = False
        self.altitude = 0.0
        self.speed = 0.0
        
    def move_forward(self):
        """Move drone forward (north)"""
        if self.is_flying:
            self.latitude += self.movement_step
            self.speed = 2.0
            self.heading = 0
            self._consume_battery(0.2)
            
    def move_backward(self):
        """Move drone backward (south)"""
        if self.is_flying:
            self.latitude -= self.movement_step
            self.speed = 2.0
            self.heading = 180
            self._consume_battery(0.2)
            
    def move_left(self):
        """Move drone left (west)"""
        if self.is_flying:
            self.longitude -= self.movement_step
            self.speed = 2.0
            self.heading = 270
            self._consume_battery(0.2)
            
    def move_right(self):
        """Move drone right (east)"""
        if self.is_flying:
            self.longitude += self.movement_step
            self.speed = 2.0
            self.heading = 90
            self._consume_battery(0.2)
            
    def move_up(self):
        """Increase drone altitude"""
        if self.is_flying and self.altitude < self.max_altitude:
            self.altitude += 1.0
            self._consume_battery(0.3)
            
    def move_down(self):
        """Decrease drone altitude"""
        if self.is_flying and self.altitude > self.min_altitude:
            self.altitude -= 1.0
            self._consume_battery(0.1)
            
    def return_to_home(self):
        """Return drone to its initial position"""
        if self.is_flying:
            # Gradually move toward home position
            self.latitude = self.latitude * 0.8 + self.initial_lat * 0.2
            self.longitude = self.longitude * 0.8 + self.initial_lng * 0.2
            self.speed = 5.0
            self._consume_battery(0.5)
            
    def emergency_stop(self):
        """Emergency stop procedure - rapidly reduce altitude"""
        self.speed = 0.0
        self.altitude = 0.0
        self.is_flying = False
        
    def update_status(self):
        """Update drone status based on elapsed time and activity"""
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        
        # Basic battery drain over time
        if self.is_flying:
            self._consume_battery(0.05 * elapsed_time)
            
            # Add slight position drift for realism
            if random.random() < 0.3:  # 30% chance of drift
                self.latitude += random.uniform(-0.00001, 0.00001)
                self.longitude += random.uniform(-0.00001, 0.00001)
                
            # Vary speed slightly
            self.speed += random.uniform(-0.2, 0.2)
            self.speed = max(0, min(self.max_speed, self.speed))
        else:
            self._consume_battery(0.01 * elapsed_time)
            self.speed = 0.0
            
        # Update signal strength with some realistic variation
        self.signal_strength += random.uniform(-2, 2)
        self.signal_strength = max(60, min(100, self.signal_strength))
        
        self.last_update_time = current_time
        
    def _consume_battery(self, amount):
        """Consume battery by the specified percentage"""
        self.battery_level = max(0, self.battery_level - amount)
        
    def get_status(self):
        """Get current drone status"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "heading": self.heading,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "is_flying": self.is_flying,
            "timestamp": datetime.now()
        }