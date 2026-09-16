# NVIDIA-Accelerated FLIR ONE Pro Edge Pipeline (UW Medicine)

An enterprise-grade, edge-optimized medical research pipeline designed to capture high-fidelity radiometric thermal streams from the **FLIR ONE Pro (Lepton 3.5 Core)**. This system establishes a hardware-accelerated processing engine on **NVIDIA RTX 6000 Ada** workstations and **NVIDIA Jetson Orin** edge units to extract true kelvin/celsius matrices, handle co-registration with visible MSX feeds, and perform zero-copy VRAM spatial delta tracking.

**Developed for the UW Medicine Clinical Imaging & Research Network.**

## Architecture Ecosystem Overview

The platform implements an asynchronous, multi-threaded worker pipeline to ingest mobile thermal arrays without frame dropping, maintaining a stable 8.7 Hz execution rate (FLIR regulatory ceiling):

1. **Hardware Ingestion Layer (`flir_stream_ingest.py`)**: Utilizes low-level `libusb`/`pyusb` endpoints to bypass proprietary mobile applications. It establishes direct raw byte-stream communication to extract the interleaved MSX visible (640x480) and raw radiometric thermal (160x120) sub-frames.
2. **NVIDIA CUDA Thermal Core (`cuda_thermal_math.py`)**: Shifts raw 14-bit linear ADC counts directly onto GPU registers. Using compiled CUDA kernels, it executes real-time radiometric calibration calculations (Planck constant corrections, ambient temperature, distance, and emissivity scaling) across the entire frame matrix simultaneously.
3. **Anatomical Co-Registration Layer (`ocr_layer.py / pipelines/`)**: Utilizes **NVIDIA TensorRT**-optimized models to dynamically warp and map the lower-resolution thermal map perfectly onto the high-resolution visible matrix, accounting for parallax offsets.
4. **Clinical Telemetry Hub (`stream_dashboard.py`)**: Forwards localized region-of-interest (ROI) max/min delta points to a secure internal web server running strictly inside the UW Medicine intranet.

## Host Prerequisites

Before deploying the pipeline container stacks, ensure your clinical workstation or Jetson edge node matches the hardware baseline:

1. **NVIDIA Compute Architecture**: Driver version 550.x or newer with **CUDA Toolkit 12.2+** integrated.
2. **Access Permissions**: Local `udev` rules mapped to permit containerized USB access to the FLIR vendor ID.
3. **Containerization**: Native Docker runtime setup paired with the **NVIDIA Container Toolkit**.

```bash
# Add FLIR ONE Pro hardware communication mapping to host udev rules
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=09cb, ATTR{idProduct}=1996, MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-flir.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Rapid Clinical Deployment

### 1. Build & Spin Up the Edge Node Containers

The framework includes dedicated optimization paths for both enterprise desktop setups and mobile Jetson carts.

```bash
# Clone the repository structure
git clone https://github.com
cd NVIDIA-Accelerated-FLIR-ONE-Pro-UWMed

# Build and run the local container stack via Docker Compose
docker compose up --build -d
```

### 2. Verify Hardware Pipeline Connection

```bash
# Tail live container logs to verify raw radiometric frame ingestion loop
docker exec -it flir_nvidia_worker tail -f /var/log/thermal_pipeline.log
```

## HIPAA Compliance & Data Security Protocol

To maintain strict alignment with **UW Medicine Security Regulations** and **HIPAA Safe Harbor Laws**, this pipeline operates under rigid data isolation rules:
* **Zero PHI Retention**: The acquisition layer blocks text inputs for patient identifiers. All files are sequentially indexed utilizing automated UUID hashes.
* **VRAM Volumetric Anonymization**: Visible spectrum components mapped through the MSX alignment engine undergo automatic spatial blurring across high-risk facial features on the GPU before saving.
* **Network Isolation**: Edge components bind exclusively to internal standard enterprise networks (`10.0.0.0/8`). Cloud transmission of raw files is locked behind a TLS 1.3 encryption wrapper.

## Clinical Production Disclaimer
The **FLIR ONE Pro** is classified as a prosumer thermal device. Telethermographic systems are regulated by the FDA as Class I devices under **21 CFR 884.2980**. This pipeline is engineered exclusively for **adjunctive clinical trial support, laboratory tracking, and institutional research**. It is strictly unauthorized and uncleared for use as a standalone diagnostic diagnostic tool.
