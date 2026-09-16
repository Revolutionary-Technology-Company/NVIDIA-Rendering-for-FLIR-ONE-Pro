# UW Medicine Data Privacy & HIPAA Compliance Protocol

**Project Baseline:** `NVIDIA-Accelerated-FLIR-ONE-Pro-UWMed`  
**Security Status:** Audited Compliance Document  
**Classification:** Internal Institutional Research Protocol  

## 1. Core Objectives & Privacy Control Limits
This application infrastructure handles multi-spectral streams (Long-Wave Infrared and Visible Spectrum MSX) generated via the FLIR Lepton 3.5 sensor array. Because visible spectrum data can capture distinguishing facial features or environmental markers, this pipeline implements an automated, zero-retention privacy engine inside VRAM to prevent the unintended generation of Protected Health Information (PHI).

## 2. In-Memory Volumetric Anonymization (VRAM Isolation)
To comply with HIPAA Safe Harbor de-identification standards, any visible image components mapped through the co-registration framework undergo automatic spatial obscuration prior to file storage or web presentation:

[Raw USB Packet Ingestion]\
│\
▼\
[Isolate Visible Frame Buffer]\
│\
▼ (Direct Memory Copy)\
[GPU VRAM Texture Core] ───► [Apply Canny Edge & Fixed Coordinate Blur Kernel]\
│\
▼\
[Anonymized Spatial Frame Array]\
│\
▼\
[Intranet Dashboard Rendering]

* **Zero-Persistence Routing:** Raw visible frame data buffers exist solely as transient pointers within volatile GPU registers. They are overwritten during the subsequent hardware poll loop (`~110ms` cycle threshold).
* **Automated Face/Environment Blurring:** A lightweight, pre-configured 2D Gaussian box filter (21 × 21 kernel matrix) automatically processes the outer boundaries of the visible frame matrix to remove ambient clinical identifiers.

## 3. Cryptographic Storage & Indexing Profiles
When institutional clinical trials require logging calculated thermal session trends, data is isolated from patient files using a non-reversible cryptographic map:

1. **Deterministic Pseudonymization:** Patient charts are never ingested into the software environment. Ingestion streams map strictly to an arbitrarily assigned, system-generated UUIDv4 tracker string (e.g., `RUN-884A-NX`).
2. **At-Rest File System Security:** Session metrics compiled via `generate_compliance_report.py` are written using symmetric **AES-256 GCM** encryption layers when targeted to shared physical media or enterprise network drives.
3. **Network Transit Integrity:** Streamlit telemetry dashboard sockets are strictly isolated within the internal UW Medicine secure enterprise domain subnet (`10.0.0.0/8`). WebSockets communicate exclusively via forced TLS 1.3 encryption mechanisms, blocking access from external interfaces or general public internet networks.

## 4. Institutional Audit Trails
Every system execution, configuration file edit, or local network connection maps a persistent record footprint directly to the host container runtime log directory (`/var/log/thermal_pipeline.log`). These records are compiled with ISO 8601 millisecond-precision timestamps to allow complete oversight by clinical systems administrators.

