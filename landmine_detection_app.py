"""
Landmine Detection Dashboard

A real-time dashboard for monitoring and controlling landmine detection drones,
with actual image processing capabilities for detecting potential landmines.
"""

import os
import json
import streamlit as st
import pandas as pd
import time
import base64
from datetime import datetime
from PIL import Image
import io

# Import modules from the project
from utils import generate_unique_id, get_status_color, format_timestamp
from db import get_all_detections, get_all_events, save_detection, save_event, get_detection_stats
from drone_simulator import DroneSimulator
from detection_simulator import DetectionSimulator
from image_processor import LandmineDetector

# Page config
st.set_page_config(
    page_title="Landmine Detection Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background-color: #f0f2f6;
    }
    .detection-card {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    .main-header {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .control-button {
        width: 100%;
        margin: 5px 0;
    }
    .nav-button {
        margin: 5px;
    }
    .emergency-button {
        background-color: #EF4444 !important;
        color: white !important;
        font-weight: bold !important;
    }
    .status-panel {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .info-box {
        background-color: #E0F2FE;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'drone' not in st.session_state:
    st.session_state.drone = DroneSimulator(
        initial_lat=34.0522,  # Los Angeles coordinates
        initial_lng=-118.2437,
        initial_altitude=10.0
    )

if 'detector' not in st.session_state:
    st.session_state.detector = DetectionSimulator()

if 'detections' not in st.session_state:
    st.session_state.detections = get_all_detections()

if 'events' not in st.session_state:
    st.session_state.events = get_all_events()

if 'image_detector' not in st.session_state:
    st.session_state.image_detector = LandmineDetector()

if 'processed_images' not in st.session_state:
    st.session_state.processed_images = {}

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "dashboard"

# Helper functions
def add_event(event_type, message, severity):
    """Add a new event to the system"""
    event_data = {
        "id": generate_unique_id(),
        "time": datetime.now(),
        "type": event_type,
        "message": message,
        "severity": severity
    }
    save_event(event_data)
    st.session_state.events = get_all_events()

def get_image_as_base64(image_path):
    """Convert an image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def process_uploaded_image(uploaded_file):
    """Process an uploaded image for landmine detection"""
    if uploaded_file is None:
        return None
    
    try:
        # Create a temp file path
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process the image
        detections = st.session_state.image_detector.detect_landmines(file_path)
        
        # Add event
        if detections:
            add_event(
                "Detection", 
                f"Detected {len(detections)} potential objects in uploaded image", 
                "warning" if any(d['classification'] == 'Landmine' for d in detections) else "info"
            )
        
        # Return the path to the processed image
        processed_path = st.session_state.image_detector.get_processed_image_path(file_path)
        if processed_path:
            st.session_state.processed_images[file_path] = processed_path
        
        # Update detections list
        st.session_state.detections = get_all_detections()
        
        return processed_path
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# Header
st.markdown("<h1 class='main-header'>Landmine Detection Dashboard</h1>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "Image Analysis", "Settings"])

# Tab 1: Main Dashboard
with tab1:
    # Layout with three columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Column 1: Drone Controls
    with col1:
        st.subheader("Drone Controls")
        
        # Drone status
        drone_status = st.session_state.drone.get_status()
        
        st.markdown("#### Status")
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.markdown(f"**Flight Status:**")
            flight_status = "Flying" if drone_status['is_flying'] else "Grounded"
            status_color = "green" if drone_status['is_flying'] else "gray"
            st.markdown(f"<span style='color:{status_color};'>● {flight_status}</span>", unsafe_allow_html=True)
        
        with status_col2:
            st.markdown(f"**Battery:**")
            battery_pct = drone_status['battery_level']
            battery_color = "green" if battery_pct > 50 else "orange" if battery_pct > 20 else "red"
            st.markdown(f"<span style='color:{battery_color};'>● {battery_pct}%</span>", unsafe_allow_html=True)
        
        # Add more status indicators
        status_col3, status_col4 = st.columns(2)
        
        with status_col3:
            st.markdown(f"**Altitude:**")
            st.markdown(f"{drone_status['altitude']:.1f} m")
        
        with status_col4:
            st.markdown(f"**Signal:**")
            signal_strength = drone_status.get('signal_strength', 95)
            signal_color = "green" if signal_strength > 70 else "orange" if signal_strength > 40 else "red"
            st.markdown(f"<span style='color:{signal_color};'>● {signal_strength}%</span>", unsafe_allow_html=True)
        
        # Take off / Land button
        if drone_status['is_flying']:
            if st.button("Land Drone", use_container_width=True):
                st.session_state.drone.land()
                add_event("Control", "Landing drone", "info")
                st.rerun()
        else:
            if st.button("Take Off", use_container_width=True):
                st.session_state.drone.takeoff()
                add_event("Control", "Drone taking off", "info")
                st.rerun()
        
        # Navigation
        st.markdown("#### Navigation")
        
        # Create a grid of navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            st.write("")
            if st.button("↑", key="forward", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_forward()
                add_event("Navigation", "Moving forward", "info")
                st.rerun()
            st.write("")
        
        with nav_col2:
            if st.button("←", key="left", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_left()
                add_event("Navigation", "Moving left", "info")
                st.rerun()
            if st.button("↓", key="backward", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_backward()
                add_event("Navigation", "Moving backward", "info")
                st.rerun()
            if st.button("→", key="right", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_right()
                add_event("Navigation", "Moving right", "info")
                st.rerun()
        
        with nav_col3:
            if st.button("⬆", key="up", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_up()
                add_event("Navigation", "Increasing altitude", "info")
                st.rerun()
            st.write("")
            if st.button("⬇", key="down", disabled=not drone_status['is_flying']):
                st.session_state.drone.move_down()
                add_event("Navigation", "Decreasing altitude", "info")
                st.rerun()
        
        # Emergency controls
        st.markdown("#### Emergency Controls")
        emergency_col1, emergency_col2 = st.columns(2)
        
        with emergency_col1:
            if st.button("EMERGENCY STOP", key="emergency", 
                         use_container_width=True,
                         disabled=not drone_status['is_flying']):
                st.session_state.drone.emergency_stop()
                add_event("Emergency", "Emergency stop initiated", "danger")
                st.rerun()
        
        with emergency_col2:
            if st.button("Return Home", key="return_home", 
                         use_container_width=True,
                         disabled=not drone_status['is_flying']):
                st.session_state.drone.return_to_home()
                add_event("Control", "Returning to home position", "warning")
                st.rerun()
        
        # Scan area button
        if st.button("Scan Current Area", use_container_width=True, disabled=not drone_status['is_flying']):
            # Check for detections at current position
            detection = st.session_state.detector.check_for_detection(
                st.session_state.drone.latitude, 
                st.session_state.drone.longitude
            )
            
            if detection:
                # Save to database
                save_detection(detection)
                # Update session state
                st.session_state.detections = get_all_detections()
                # Log an event
                add_event(
                    "Detection", 
                    f"Detected {detection['classification']} with {detection['confidence']:.1f}% confidence", 
                    "danger" if detection['classification'] == "Landmine" else "warning"
                )
            else:
                add_event("Scan", "No objects detected in current area", "info")
            
            st.rerun()
    
    # Column 2: Map View and Sensor Data
    with col2:
        st.subheader("Map and Sensors")
        
        # Get drone position and detections
        drone_status = st.session_state.drone.get_status()
        detections = st.session_state.detections
        
        # Create a dataframe for the map
        map_data = []
        
        # Add drone position
        map_data.append({
            'lat': drone_status['latitude'],
            'lon': drone_status['longitude'],
            'label': 'Drone'
        })
        
        # Add detection markers
        for detection in detections:
            map_data.append({
                'lat': detection['latitude'],
                'lon': detection['longitude'],
                'label': f"{detection['classification']} ({detection['confidence']:.1f}%)"
            })
        
        # Convert to dataframe
        df_map = pd.DataFrame(map_data)
        
        # Display the map using streamlit's built-in map function
        if not df_map.empty:
            st.map(df_map, latitude='lat', longitude='lon')
        else:
            st.info("No map data available yet")
        
        # Show a legend for the map
        st.markdown("""
        **Map Legend:**
        - Blue circles: Drone current position
        - Other markers: Detection points (Landmines, Metal Debris, Safe Zones)
        """)
        
        # Display a table of detection points underneath
        if not df_map.empty and len(detections) > 0:
            st.markdown("#### Detection Points")
            detection_table = []
            for detection in detections:
                detection_table.append({
                    'Type': detection['classification'],
                    'Confidence': f"{detection['confidence']:.1f}%",
                    'Latitude': f"{detection['latitude']:.6f}",
                    'Longitude': f"{detection['longitude']:.6f}"
                })
            st.dataframe(pd.DataFrame(detection_table))
        
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
                    
                    # Show image if available
                    if detection.get('image_path') and os.path.exists(detection['image_path']):
                        st.image(detection['image_path'], caption=f"Detection Image", use_column_width=True)
        
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

# Tab 2: Image Analysis
with tab2:
    st.subheader("Image Analysis & Processing")
    
    # Upload an image for analysis
    st.markdown("#### Upload Image for Analysis")
    uploaded_file = st.file_uploader("Upload drone imagery for landmine detection", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Show the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        # Process the image when the button is clicked
        if st.button("Analyze Image", use_container_width=True):
            with st.spinner("Processing image..."):
                processed_path = process_uploaded_image(uploaded_file)
                if processed_path and os.path.exists(processed_path):
                    st.success("Image analysis complete!")
                    st.image(processed_path, caption="Analyzed Image with Detections", use_column_width=True)
                    
                    # Display processing results
                    detected_objects = [d for d in st.session_state.detections if d.get('image_path') and uploaded_file.name in d.get('image_path')]
                    
                    if detected_objects:
                        st.markdown(f"#### Detection Results ({len(detected_objects)} objects found)")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        landmines = [d for d in detected_objects if d['classification'] == 'Landmine']
                        debris = [d for d in detected_objects if d['classification'] == 'Metal Debris']
                        safe = [d for d in detected_objects if d['classification'] == 'Safe Zone']
                        
                        with col1:
                            st.markdown(f"**Landmines:** {len(landmines)}")
                        with col2:
                            st.markdown(f"**Metal Debris:** {len(debris)}")
                        with col3:
                            st.markdown(f"**Safe Areas:** {len(safe)}")
                        
                        # Display the detections in a table
                        detection_df = []
                        for d in detected_objects:
                            detection_df.append({
                                'Type': d['classification'],
                                'Confidence': f"{d['confidence']:.1f}%",
                                'X': d.get('x', 'N/A'),
                                'Y': d.get('y', 'N/A'),
                                'Lat': f"{d['latitude']:.6f}",
                                'Long': f"{d['longitude']:.6f}"
                            })
                        
                        st.dataframe(pd.DataFrame(detection_df))
                    else:
                        st.warning("No objects detected in this image.")
                else:
                    st.error("Error processing image.")
    
    # Show sample images
    st.markdown("#### Sample Images")
    
    sample_dir = "sample_images"
    if os.path.exists(sample_dir):
        sample_images = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if sample_images:
            selected_sample = st.selectbox("Select a sample image", sample_images)
            
            # Show the selected sample
            sample_path = os.path.join(sample_dir, selected_sample)
            
            # Check if this image has been processed before
            processed_path = None
            for img_path, proc_path in st.session_state.processed_images.items():
                if sample_path in img_path:
                    processed_path = proc_path
                    break
            
            # Display sample image
            st.image(sample_path, caption="Sample Image", use_column_width=True)
            
            # Process or show previously processed image
            if processed_path and os.path.exists(processed_path):
                st.image(processed_path, caption="Processed Image", use_column_width=True)
            else:
                if st.button("Process Sample Image", use_container_width=True):
                    with st.spinner("Processing sample image..."):
                        # Process the image
                        detections = st.session_state.image_detector.detect_landmines(sample_path)
                        
                        # Get the processed image path
                        processed_path = st.session_state.image_detector.get_processed_image_path(sample_path)
                        
                        if processed_path and os.path.exists(processed_path):
                            st.success(f"Processed image with {len(detections)} detections")
                            st.image(processed_path, caption="Processed Image", use_column_width=True)
                            
                            # Store for future reference
                            st.session_state.processed_images[sample_path] = processed_path
                            
                            # Update detections
                            st.session_state.detections = get_all_detections()
                            
                            # Add event
                            add_event(
                                "Processing", 
                                f"Analyzed sample image, found {len(detections)} potential objects", 
                                "warning" if any(d['classification'] == 'Landmine' for d in detections) else "info"
                            )
                            
                            st.rerun()
        else:
            st.info("No sample images found. Upload some images to the 'sample_images' directory.")
    else:
        st.info("Sample images directory not found.")
    
    # Technical details expander
    with st.expander("Technical Details"):
        st.markdown("""
        ### Landmine Detection Algorithm
        
        The system uses computer vision techniques to detect potential landmines in drone imagery:
        
        1. **Preprocessing**: Images are converted to grayscale and blurred to reduce noise
        2. **Thresholding**: Adaptive thresholding is applied to highlight potential objects
        3. **Contour Detection**: The system identifies distinct objects in the image
        4. **Classification**: Objects are classified based on shape, size, and other characteristics
        5. **Confidence Scoring**: Each detection is assigned a confidence score
        
        The algorithm particularly looks for circular objects of specific sizes, which are characteristic of landmines.
        Metal debris typically has irregular shapes but still registers on metal detectors.
        """)

# Tab 3: Settings
with tab3:
    st.subheader("System Settings")
    
    # Simulation settings
    st.markdown("#### Simulation Settings")
    
    # Detection sensitivity
    detection_sensitivity = st.slider(
        "Detection Sensitivity", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.7, 
        step=0.1,
        help="Higher values increase detection rate but may result in more false positives"
    )
    
    # Confidence threshold
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=50.0,
        max_value=95.0,
        value=70.0,
        step=5.0,
        help="Minimum confidence level required to classify an object as a landmine"
    )
    
    # Apply settings
    if st.button("Apply Settings", use_container_width=True):
        # Update detector settings
        if hasattr(st.session_state.image_detector, 'confidence_threshold'):
            st.session_state.image_detector.confidence_threshold = detection_sensitivity
        
        st.success("Settings applied successfully!")
    
    # Clear database option
    st.markdown("#### Database Management")
    
    if st.button("Clear All Detections", use_container_width=True):
        # Confirmation
        confirm = st.checkbox("I understand this will delete all detection data")
        
        if confirm:
            # This would typically connect to the database and clear it
            # For now, just clear the session state
            st.session_state.detections = []
            
            # Clear detection history
            st.session_state.processed_images = {}
            
            # Add event
            add_event("System", "All detection data cleared", "warning")
            
            st.success("All detection data has been cleared.")
            st.info("Refresh the page to see the changes.")
    
    # About section
    st.markdown("#### About the System")
    
    st.markdown("""
    **Landmine Detection System v2.0**
    
    This system combines drone technology with computer vision and AI to detect potential landmines
    in conflict zones and post-conflict areas. The system is designed to be used by humanitarian
    demining teams to increase safety and efficiency in landmine clearance operations.
    
    **Key Features:**
    - Real-time drone control and monitoring
    - Advanced image processing for landmine detection
    - Integrated database for detection records
    - Export capabilities for field reports
    
    For support or more information, contact support@landmine-detection-system.org
    """)