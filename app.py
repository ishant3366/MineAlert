import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime
import time
import io
import json
import random
import os
from drone_simulator import DroneSimulator
from detection_simulator import DetectionSimulator
from utils import get_status_color, format_timestamp, generate_unique_id
import db

# Page configuration
st.set_page_config(
    page_title="Landmine Detection Drone Dashboard",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'drone' not in st.session_state:
    st.session_state.drone = DroneSimulator(
        initial_lat=34.0522,  # Los Angeles
        initial_lng=-118.2437
    )

if 'detector' not in st.session_state:
    st.session_state.detector = DetectionSimulator()

if 'events' not in st.session_state:
    # Load events from database if available
    db_events = db.get_all_events()
    st.session_state.events = db_events if db_events else []

if 'detections' not in st.session_state:
    # Load detections from database if available
    db_detections = db.get_all_detections()
    st.session_state.detections = db_detections if db_detections else []

if 'is_flying' not in st.session_state:
    st.session_state.is_flying = False

if 'auto_update' not in st.session_state:
    st.session_state.auto_update = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Title and description
st.title("Landmine Detection Drone Dashboard")
st.markdown("Real-time monitoring and control system for landmine detection drones")

# Main layout with three columns
col1, col2, col3 = st.columns([1, 2, 1])

# Column 1: Drone Controls and Status
with col1:
    st.subheader("Drone Controls")
    
    # Flight controls
    flight_controls = st.container()
    with flight_controls:
        if st.session_state.is_flying:
            if st.button("🛬 Land", key="land_button", use_container_width=True):
                st.session_state.drone.land()
                st.session_state.is_flying = False
                event_data = {
                    "id": generate_unique_id(),
                    "time": datetime.now(),
                    "type": "CONTROL",
                    "message": "Drone landed",
                    "severity": "info"
                }
                st.session_state.events.append(event_data)
                db.save_event(event_data)
                st.rerun()
        else:
            if st.button("🛫 Take Off", key="takeoff_button", use_container_width=True):
                st.session_state.drone.takeoff()
                st.session_state.is_flying = True
                event_data = {
                    "id": generate_unique_id(),
                    "time": datetime.now(),
                    "type": "CONTROL",
                    "message": "Drone took off",
                    "severity": "info"
                }
                st.session_state.events.append(event_data)
                db.save_event(event_data)
                st.rerun()
    
    # Emergency controls
    emergency_controls = st.container()
    with emergency_controls:
        emergency_col1, emergency_col2 = st.columns(2)
        
        with emergency_col1:
            if st.button("🏠 Return Home", key="return_home", use_container_width=True):
                st.session_state.drone.return_to_home()
                event_data = {
                    "id": generate_unique_id(),
                    "time": datetime.now(),
                    "type": "CONTROL",
                    "message": "Return to home initiated",
                    "severity": "warning"
                }
                st.session_state.events.append(event_data)
                db.save_event(event_data)
                st.rerun()
        
        with emergency_col2:
            if st.button("⚠️ Emergency Stop", key="emergency_stop", use_container_width=True):
                st.session_state.drone.emergency_stop()
                st.session_state.is_flying = False
                event_data = {
                    "id": generate_unique_id(),
                    "time": datetime.now(),
                    "type": "CONTROL",
                    "message": "EMERGENCY STOP triggered",
                    "severity": "danger"
                }
                st.session_state.events.append(event_data)
                db.save_event(event_data)
                st.rerun()
    
    # Directional controls (only enabled when flying)
    directional_controls = st.container()
    directional_enabled = st.session_state.is_flying
    
    with directional_controls:
        st.markdown("#### Navigation")
        
        # Up/Down controls
        ud_col1, ud_col2, ud_col3 = st.columns([1, 1, 1])
        with ud_col2:
            if st.button("⬆️", key="move_up", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_up()
                st.rerun()
        
        # Left/Forward/Right controls
        lrf_col1, lrf_col2, lrf_col3 = st.columns([1, 1, 1])
        with lrf_col1:
            if st.button("⬅️", key="move_left", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_left()
                st.rerun()
        
        with lrf_col2:
            if st.button("⬆️", key="move_forward", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_forward()
                st.rerun()
        
        with lrf_col3:
            if st.button("➡️", key="move_right", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_right()
                st.rerun()
        
        # Down control
        ud2_col1, ud2_col2, ud2_col3 = st.columns([1, 1, 1])
        with ud2_col2:
            if st.button("⬇️", key="move_down", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_down()
                st.rerun()
        
        # Backward control
        b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
        with b_col2:
            if st.button("⬇️", key="move_backward", disabled=not directional_enabled, use_container_width=True):
                st.session_state.drone.move_backward()
                st.rerun()
    
    # Drone Status
    st.subheader("Drone Status")
    
    # Auto-update toggle
    st.session_state.auto_update = st.toggle("Auto-update status (enable for automatic scanning)", value=st.session_state.auto_update)
    
    if st.session_state.auto_update:
        # Only update if more than 1 second has passed (increased frequency for demo)
        if (datetime.now() - st.session_state.last_update).total_seconds() > 1:
            st.session_state.drone.update_status()
            
            # Check for new detections if the drone is flying
            if st.session_state.is_flying:
                # Check for multiple detections at once to increase sample data
                for _ in range(3):  # Try up to 3 detection points around current position
                    # Add small random offsets for detection points
                    lat_offset = random.uniform(-0.0001, 0.0001)
                    lon_offset = random.uniform(-0.0001, 0.0001)
                    
                    detection = st.session_state.detector.check_for_detection(
                        st.session_state.drone.latitude + lat_offset, 
                        st.session_state.drone.longitude + lon_offset
                    )
                    
                    if detection:
                        st.session_state.detections.append(detection)
                        
                        # Create event object for both session state and database
                        event_data = {
                            "id": generate_unique_id(),
                            "time": datetime.now(),
                            "type": "DETECTION",
                            "message": f"{detection['classification']} detected with {detection['confidence']:.2f}% confidence",
                            "severity": "danger" if detection['classification'] == "Landmine" else "warning" if detection['classification'] == "Metal Debris" else "info"
                        }
                        
                        # Add to session state
                        st.session_state.events.append(event_data)
                        
                        # Save to database
                        db.save_detection(detection)
                        db.save_event(event_data)
            
            st.session_state.last_update = datetime.now()
    
    if st.button("Refresh Status", use_container_width=True):
        st.session_state.drone.update_status()
        
        # Check for new detections if the drone is flying
        if st.session_state.is_flying:
            detection = st.session_state.detector.check_for_detection(
                st.session_state.drone.latitude, 
                st.session_state.drone.longitude
            )
            
            if detection:
                st.session_state.detections.append(detection)
                
                # Create event object for both session state and database
                event_data = {
                    "id": generate_unique_id(),
                    "time": datetime.now(),
                    "type": "DETECTION",
                    "message": f"{detection['classification']} detected with {detection['confidence']:.2f}% confidence",
                    "severity": "danger" if detection['classification'] == "Landmine" else "warning" if detection['classification'] == "Metal Debris" else "info"
                }
                
                # Add to session state
                st.session_state.events.append(event_data)
                
                # Save to database
                db.save_detection(detection)
                db.save_event(event_data)
    
    # Display drone status
    drone_status = st.session_state.drone.get_status()
    
    st.markdown(f"**Flight Status:** {'Flying' if st.session_state.is_flying else 'Landed'}")
    
    # Battery progress bar with color coding
    battery_level = drone_status['battery_level']
    battery_color = "green" if battery_level > 50 else "orange" if battery_level > 20 else "red"
    
    st.markdown(f"**Battery:** {battery_level}%")
    st.progress(battery_level / 100.0, text=f"{battery_level}%")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown(f"**Altitude:** {drone_status['altitude']:.1f}m")
        st.markdown(f"**Speed:** {drone_status['speed']:.1f}m/s")
    
    with status_col2:
        st.markdown(f"**Lat:** {drone_status['latitude']:.6f}")
        st.markdown(f"**Lng:** {drone_status['longitude']:.6f}")
    
    st.markdown(f"**Signal Strength:** {drone_status['signal_strength']}%")

# Column 2: Map visualization
with col2:
    st.subheader("Mission Map")
    
    # Get drone position and detections
    drone_status = st.session_state.drone.get_status()
    detections = st.session_state.detections
    
    # Create a map centered on the drone's position with OpenStreetMap (more reliable)
    m = folium.Map(
        location=[drone_status['latitude'], drone_status['longitude']],
        zoom_start=18
    )
    
    # Add the drone marker with a distinctive icon
    folium.Marker(
        [drone_status['latitude'], drone_status['longitude']],
        popup="Drone",
        icon=folium.Icon(icon="plane", prefix="fa", color="blue"),
        tooltip="Current Drone Position"
    ).add_to(m)
    
    # Add a circle to show drone's general area for better visibility
    folium.Circle(
        [drone_status['latitude'], drone_status['longitude']],
        radius=10,  # meters
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.4
    ).add_to(m)
    
    # Add detection markers
    for detection in detections:
        # Determine color based on classification
        if detection['classification'] == "Landmine":
            color = "red"
            icon = "warning"
        elif detection['classification'] == "Metal Debris":
            color = "orange"
            icon = "info"
        else:  # Safe Zone
            color = "green"
            icon = "ok"
        
        # Add marker to map with tooltip
        folium.Marker(
            [detection['latitude'], detection['longitude']],
            popup=f"{detection['classification']} ({detection['confidence']:.2f}%)",
            icon=folium.Icon(icon=icon, prefix="fa", color=color),
            tooltip=f"{detection['classification']}: {detection['confidence']:.1f}%"
        ).add_to(m)
        
        # Add circle for better visibility on satellite imagery
        folium.Circle(
            [detection['latitude'], detection['longitude']],
            radius=5,  # meters
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.4
        ).add_to(m)
    
    # Display the map in Streamlit with a simplified approach
    try:
        # Use a simpler way to display the map that is more reliable
        st_data = st_folium(m, width=700, height=500, returned_objects=[])
    except Exception as e:
        st.error(f"Map display error: {e}")
        # Show a placeholder instead
        st.info("Map loading... If it doesn't appear, please refresh the page.")
    
    # Sensor Data Visualization
    st.subheader("Sensor Data")
    
    # Simulated sensor readings
    sensor_col1, sensor_col2 = st.columns(2)
    
    with sensor_col1:
        # Metal detector readings
        st.markdown("**Metal Detector Reading**")
        metal_reading = st.session_state.detector.get_metal_detector_reading(
            st.session_state.drone.latitude, 
            st.session_state.drone.longitude
        )
        st.progress(metal_reading / 100.0, text=f"{metal_reading}%")
    
    with sensor_col2:
        # Thermal readings
        st.markdown("**Thermal Anomaly Detection**")
        thermal_reading = st.session_state.detector.get_thermal_reading(
            st.session_state.drone.latitude, 
            st.session_state.drone.longitude
        )
        st.progress(thermal_reading / 100.0, text=f"{thermal_reading}%")
    
    # Display event stream
    st.subheader("Event Stream")
    
    # Reverse events to show newest first
    recent_events = list(reversed(st.session_state.events))[:10]
    
    if not recent_events:
        st.info("No events recorded yet.")
    else:
        for event in recent_events:
            event_time = format_timestamp(event['time'])
            
            if event['severity'] == "danger":
                st.error(f"**{event_time}** - {event['message']}")
            elif event['severity'] == "warning":
                st.warning(f"**{event_time}** - {event['message']}")
            else:
                st.info(f"**{event_time}** - {event['message']}")

# Column 3: Detection Results and Analytics
with col3:
    st.subheader("Detection Results")
    
    # Filter by classification
    classification_filter = st.multiselect(
        "Filter by Classification",
        options=["Landmine", "Metal Debris", "Safe Zone"],
        default=["Landmine", "Metal Debris", "Safe Zone"]
    )
    
    # Filter detections
    filtered_detections = [d for d in st.session_state.detections if d['classification'] in classification_filter]
    
    # Display detection count
    detection_counts = {
        "Landmine": len([d for d in st.session_state.detections if d['classification'] == "Landmine"]),
        "Metal Debris": len([d for d in st.session_state.detections if d['classification'] == "Metal Debris"]),
        "Safe Zone": len([d for d in st.session_state.detections if d['classification'] == "Safe Zone"])
    }
    
    # Detection stats
    st.markdown("#### Detection Stats")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    with stats_col1:
        st.markdown(f"**Landmines**")
        st.markdown(f"### {detection_counts['Landmine']}")
    
    with stats_col2:
        st.markdown(f"**Debris**")
        st.markdown(f"### {detection_counts['Metal Debris']}")
    
    with stats_col3:
        st.markdown(f"**Safe Areas**")
        st.markdown(f"### {detection_counts['Safe Zone']}")
    
    # Display detection list
    st.markdown("#### Detection List")
    
    if not filtered_detections:
        st.info("No detections recorded yet.")
    else:
        for i, detection in enumerate(filtered_detections):
            # Create an expander for each detection
            with st.expander(f"{detection['classification']} at {format_timestamp(detection['timestamp'])}"):
                st.markdown(f"**Classification:** {detection['classification']}")
                st.markdown(f"**Confidence:** {detection['confidence']:.2f}%")
                st.markdown(f"**Coordinates:** {detection['latitude']:.6f}, {detection['longitude']:.6f}")
                st.markdown(f"**Detected at:** {format_timestamp(detection['timestamp'])}")
    
    # Export options
    st.subheader("Data Export")
    
    export_format = st.radio("Export Format", ["CSV", "JSON"])
    
    if st.button("Export Detection Data", use_container_width=True):
        if export_format == "CSV":
            # Convert detections to DataFrame and then to CSV
            detections_df = pd.DataFrame(st.session_state.detections)
            
            # Format the timestamp column
            if not detections_df.empty:
                detections_df['timestamp'] = detections_df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Create a download link
            csv = detections_df.to_csv(index=False)
            
            # Create a download button
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"landmine_detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:  # JSON
            # Convert detections to JSON
            detections_json = []
            
            for detection in st.session_state.detections:
                # Create a copy of the detection to avoid modifying the original
                detection_copy = detection.copy()
                
                # Convert timestamp to string
                detection_copy['timestamp'] = detection_copy['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                
                detections_json.append(detection_copy)
            
            # Create a download button
            st.download_button(
                label="Download JSON",
                data=json.dumps(detections_json, indent=2),
                file_name=f"landmine_detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # System Status
    st.subheader("System Status")
    
    # AI and system statuses
    ai_status = "Online"
    connection_status = "Connected"
    
    system_col1, system_col2 = st.columns(2)
    
    with system_col1:
        st.markdown("**AI System:**")
        st.markdown(f"### {ai_status}")
    
    with system_col2:
        st.markdown("**Connection:**")
        st.markdown(f"### {connection_status}")
    
    # Add a help section
    with st.expander("Help & Instructions"):
        st.markdown("""
        ### Using the Drone Dashboard
        
        **Drone Controls:**
        - Use the Take Off / Land button to start or end flight
        - Navigate using the directional controls when drone is flying
        - Emergency buttons provide quick safety actions
        
        **Map View:**
        - Shows drone position and detected objects
        - Red markers: Potential landmines
        - Orange markers: Metal debris
        - Green markers: Confirmed safe zones
        
        **Detection Results:**
        - Lists all detected objects with details
        - Filter by classification type
        - Export data for reporting
        
        **Event Stream:**
        - Shows real-time system events and alerts
        
        **For Emergencies:**
        - Use "Emergency Stop" to immediately halt the drone
        - "Return Home" will direct the drone back to its starting position
        """)
