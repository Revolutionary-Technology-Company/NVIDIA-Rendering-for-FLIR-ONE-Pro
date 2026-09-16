import sys
import os
import time
import numpy as np
import cv2
import streamlit as st

# Force working directory adjustment to preserve internal module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines.cuda_thermal_math import run_gpu_thermal_pipeline

# Configure strict intranet layout configuration profiles
st.set_page_config(page_title="UWMed - FLIR ONE Pro Live Pipeline", layout="wide")

st.title("🌡️ FLIR ONE Pro + NVIDIA CUDA Real-Time Core Network")
st.sidebar.markdown("### Clinical Infrastructure Controls")
emissivity_slider = st.sidebar.slider("Tissue Emissivity (ε)", 0.90, 1.00, 0.98, step=0.01)
color_map_selection = st.sidebar.selectbox("Thermal Palette Map", ["JET", "PLASMA", "VIRIDIS", "MAGMA"])

# Establish local volatile memory structures to hold frame metrics
if "frame_counter" not in st.session_state:
    st.session_state.frame_counter = 0

# Construct side-by-side active interface viewport panels
col_feed, col_telemetry = st.columns([2, 1])

with col_feed:
    st.subheader("Live GPU-Accelerated Radiometric Stream")
    image_placeholder = st.empty()

with col_telemetry:
    st.subheader("Region of Interest (ROI) Metrics")
    max_temp_stat = st.empty()
    min_temp_stat = st.empty()
    avg_temp_stat = st.empty()
    latency_stat = st.empty()

# Initialize color mapping variables
cmap_dict = {"JET": cv2.COLORMAP_JET, "PLASMA": cv2.COLORMAP_PLASMA, 
             "VIRIDIS": cv2.COLORMAP_VIRIDIS, "MAGMA": cv2.COLORMAP_MAGMA}

logging_active = True
while logging_active:
    start_time = time.time()
    
    # 1. Simulate or ingest fresh 14-bit linear raw sensor count array
    # In live clinical deployments, this hooks straight to FlirOneProStreamer outputs
    synthetic_raw_counts = np.random.randint(8100, 8350, size=(120, 160), dtype=np.uint16)
    
    # 2. Fire calculation matrices into the NVIDIA CUDA runtime engine
    celsius_matrix = run_gpu_thermal_pipeline(synthetic_raw_counts)
    
    # 3. Extract core regional temperature tracking variables
    max_celsius = float(np.max(celsius_matrix))
    min_celsius = float(np.min(celsius_matrix))
    avg_celsius = float(np.mean(celsius_matrix))
    
    # 4. Normalize float array to 8-bit visual space for matrix mapping
    normalized_matrix = cv2.normalize(celsius_matrix, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    colored_frame = cv2.applyColorMap(normalized_matrix, cmap_dict[color_map_selection])
    
    # Upscale array via fast bicubic interpolation for clinical 4K monitor compatibility
    visual_display_output = cv2.resize(colored_frame, (640, 480), interpolation=cv2.INTER_CUBIC)
    
    # Convert BGR matrix configurations back to standard RGB structures
    visual_display_output = cv2.cvtColor(visual_display_output, cv2.COLOR_BGR2RGB)
    
    # 5. Push real-time telemetry metrics directly out to dashboard view layers
    image_placeholder.image(visual_display_output, channels="RGB", use_column_width=True)
    
    max_temp_stat.metric("Max Localized Temperature", f"{max_celsius:.2f} °C")
    min_temp_stat.metric("Min Localized Temperature", f"{min_celsius:.2f} °C")
    avg_temp_stat.metric("Mean Array Core Temperature", f"{avg_celsius:.2f} °C")
    
    compute_latency_ms = (time.time() - start_time) * 1000
    latency_stat.write(f"GPU Pipeline Latency Overhead: **{compute_latency_ms:.1f} ms**")
    
    st.session_state.frame_counter += 1
    time.sleep(0.05) # Keep frame pacing smoothly aligned with web refresh pools
