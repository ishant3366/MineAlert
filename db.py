import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Always use SQLite for this application to avoid database connection issues
DATABASE_URL = "sqlite:///landmine_detection.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for declarative models
Base = declarative_base()

# Define Detection model
class Detection(Base):
    __tablename__ = 'detections'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    classification = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    image_path = Column(String(255), nullable=True)
    x = Column(Integer, nullable=True)
    y = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Detection(id='{self.id}', classification='{self.classification}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "classification": self.classification,
            "confidence": self.confidence,
            "image_path": self.image_path,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

# Define Event model
class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String, primary_key=True)
    time = Column(DateTime, default=datetime.now)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<Event(id='{self.id}', type='{self.type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "type": self.type,
            "message": self.message,
            "severity": self.severity
        }

# Create all tables
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get a database session
def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Functions to handle database operations
def save_detection(detection_data):
    """Save a detection to the database"""
    db = SessionLocal()
    try:
        detection = Detection(
            id=detection_data['id'],
            timestamp=detection_data['timestamp'],
            latitude=detection_data['latitude'],
            longitude=detection_data['longitude'],
            classification=detection_data['classification'],
            confidence=detection_data['confidence'],
            image_path=detection_data.get('image_path'),
            x=detection_data.get('x'),
            y=detection_data.get('y'),
            width=detection_data.get('width'),
            height=detection_data.get('height')
        )
        db.add(detection)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving detection: {e}")
        return False
    finally:
        db.close()

def save_event(event_data):
    """Save an event to the database"""
    db = SessionLocal()
    try:
        event = Event(
            id=event_data['id'],
            time=event_data['time'],
            type=event_data['type'],
            message=event_data['message'],
            severity=event_data['severity']
        )
        db.add(event)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving event: {e}")
        return False
    finally:
        db.close()

def get_all_detections():
    """Get all detections from the database"""
    db = SessionLocal()
    try:
        return [detection.to_dict() for detection in db.query(Detection).all()]
    finally:
        db.close()

def get_all_events():
    """Get all events from the database"""
    db = SessionLocal()
    try:
        return [event.to_dict() for event in db.query(Event).all()]
    finally:
        db.close()

def get_detections_by_classification(classification):
    """Get detections filtered by classification"""
    db = SessionLocal()
    try:
        return [
            detection.to_dict() 
            for detection in db.query(Detection).filter(Detection.classification == classification).all()
        ]
    finally:
        db.close()

def get_detection_stats():
    """Get statistics about detections by classification"""
    db = SessionLocal()
    try:
        stats = {}
        for classification in ["Landmine", "Metal Debris", "Safe Zone"]:
            count = db.query(Detection).filter(Detection.classification == classification).count()
            stats[classification] = count
        return stats
    finally:
        db.close()