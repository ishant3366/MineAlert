import random
import math
from datetime import datetime
from utils import generate_unique_id

class DetectionSimulator:
    """
    Simulates the detection of objects by the drone's sensors.
    Provides realistic detection events based on location and probability.
    """
    
    def __init__(self):
        """Initialize the detection simulator"""
        # Define hotspots for different types of objects
        self.landmine_hotspots = [
            {"lat": 34.0522, "lon": -118.2437, "radius": 0.001, "probability": 0.7},  # Los Angeles
            {"lat": 34.0530, "lon": -118.2450, "radius": 0.0008, "probability": 0.6},
            {"lat": 34.0515, "lon": -118.2420, "radius": 0.0005, "probability": 0.8},
        ]
        
        self.debris_hotspots = [
            {"lat": 34.0525, "lon": -118.2440, "radius": 0.002, "probability": 0.5},
            {"lat": 34.0518, "lon": -118.2435, "radius": 0.001, "probability": 0.4},
            {"lat": 34.0528, "lon": -118.2430, "radius": 0.001, "probability": 0.6},
        ]
        
        self.safe_hotspots = [
            {"lat": 34.0535, "lon": -118.2455, "radius": 0.002, "probability": 0.9},
            {"lat": 34.0510, "lon": -118.2415, "radius": 0.001, "probability": 0.8},
        ]
    
    def distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two geographic coordinates"""
        # Simple Euclidean distance for demo purposes
        # In a real system, you would use the Haversine formula
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
    
    def is_near_hotspot(self, lat, lon):
        """Check if the drone is near a hotspot and return the type"""
        # Check landmine hotspots
        for hotspot in self.landmine_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"]:
                if random.random() < hotspot["probability"]:
                    return "Landmine", hotspot["probability"] * 100
        
        # Check debris hotspots
        for hotspot in self.debris_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"]:
                if random.random() < hotspot["probability"]:
                    return "Metal Debris", hotspot["probability"] * 100
        
        # Check safe hotspots
        for hotspot in self.safe_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"]:
                if random.random() < hotspot["probability"]:
                    return "Safe Zone", hotspot["probability"] * 100
        
        # If random detection is enabled (for demo), occasionally generate a detection
        if random.random() < 0.05:  # 5% chance of random detection
            detection_type = random.choices(
                ["Landmine", "Metal Debris", "Safe Zone"], 
                weights=[0.2, 0.5, 0.3]
            )[0]
            confidence = random.uniform(70, 95)
            return detection_type, confidence
            
        return None, 0
    
    def check_for_detection(self, lat, lon):
        """
        Check if the drone detects anything at the current position
        Returns a detection object or None
        """
        detection_type, confidence = self.is_near_hotspot(lat, lon)
        
        if detection_type:
            # Create a detection event
            detection = {
                "id": generate_unique_id(),
                "timestamp": datetime.now(),
                "latitude": lat,
                "longitude": lon,
                "classification": detection_type,
                "confidence": confidence
            }
            return detection
        
        return None

    def get_metal_detector_reading(self, lat, lon):
        """Simulate metal detector sensor reading (0-100)"""
        # Base reading
        reading = 10  # Ambient noise
        
        # Check landmine hotspots
        for hotspot in self.landmine_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"] * 1.5:  # Larger detection radius
                # Closer = stronger reading
                strength = (1 - dist / (hotspot["radius"] * 1.5)) * 100
                reading = max(reading, strength)
        
        # Check debris hotspots
        for hotspot in self.debris_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"] * 1.5:
                strength = (1 - dist / (hotspot["radius"] * 1.5)) * 75  # Less intense than landmines
                reading = max(reading, strength)
                
        # Add noise
        reading += random.uniform(-5, 5)
        
        # Clamp to 0-100 range
        return max(0, min(100, reading))
    
    def get_thermal_reading(self, lat, lon):
        """Simulate thermal anomaly detector reading (0-100)"""
        # Base reading
        reading = 5  # Ambient thermal noise
        
        # Landmines can have thermal signatures
        for hotspot in self.landmine_hotspots:
            dist = self.distance(lat, lon, hotspot["lat"], hotspot["lon"])
            if dist < hotspot["radius"] * 1.2:
                # Landmines can have thermal signatures from buried explosives
                strength = (1 - dist / (hotspot["radius"] * 1.2)) * 85
                reading = max(reading, strength)
        
        # Add daily variation - thermal signatures are stronger in the afternoon
        hour = datetime.now().hour
        time_factor = 1.0
        if 10 <= hour <= 16:  # Peak sun hours
            time_factor = 1.2
        elif 6 <= hour <= 9 or 17 <= hour <= 19:  # Morning and evening
            time_factor = 1.1
        
        reading *= time_factor
        
        # Add noise
        reading += random.uniform(-3, 3)
        
        # Clamp to 0-100 range
        return max(0, min(100, reading))