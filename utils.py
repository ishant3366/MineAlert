import uuid
from datetime import datetime

def generate_unique_id():
    """Generate a unique ID for events and detections"""
    return str(uuid.uuid4())

def get_status_color(status):
    """
    Return the appropriate color for a status value
    
    Args:
        status (str): Status value
        
    Returns:
        str: CSS color code
    """
    if status == "Online" or status == "Connected":
        return "green"
    elif status == "Warning" or status == "Degraded":
        return "orange"
    elif status == "Offline" or status == "Disconnected" or status == "Error":
        return "red"
    else:
        return "gray"

def format_timestamp(timestamp):
    """
    Format a timestamp for display
    
    Args:
        timestamp (datetime): The timestamp to format
        
    Returns:
        str: Formatted timestamp string
    """
    if timestamp is None:
        return "N/A"
    
    now = datetime.now()
    delta = now - timestamp
    
    if delta.days == 0:
        # Today
        if delta.seconds < 60:
            return "Just now"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
    elif delta.days == 1:
        # Yesterday
        return "Yesterday"
    else:
        # Format date
        return timestamp.strftime("%Y-%m-%d %H:%M")