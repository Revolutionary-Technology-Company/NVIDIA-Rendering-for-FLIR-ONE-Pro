# 📐 FLIR ONE Pro Optical Core & Parallax Alignment Specification

## 1. Physical Sensor Specifications
The FLIR ONE Pro incorporates two distinct physical imaging arrays positioned adjacent to one another on a unified printed circuit board structure:
* **Thermal Longwave Core:** FLIR Lepton 3.5 Microbolometer (160x120 raw pixel geometry, 57° HFOV).
* **Visible Spectrum Core:** RGB Camera Core (1440x1080 raw pixel geometry, 50° HFOV).

Because the physical distance between the centers of these two lenses is exactly **12.0 mm (Horizontal Offset Basis)**, a spatial phenomenon known as *optical parallax* occurs. This requires active digital core registration when analyzing target distances closer than infinity.

12.0 mm Center Offset\
┌───────┐ ┌───────┐\
│ RGB │◄─────►│THERMAL│\
│ Lens │ │ Lepton│\
└───────┘ └───────┘\
│ │\
│ Optical Axis │ Optical Axis\
▼ ▼\
└───────┬───────┘\
│\
▼ Matrix Convergence Map (Target Plane at 1.0m)


## 2. Dynamic Spatial Co-Registration & Warping Parameters
To display thermal data layered directly over structural edges, the software must shift the coordinates of the thermal array to align with the higher-resolution RGB frame.

When configuring the pipeline tracking system for diagnostic imaging research carts, verify that target calibration properties match the matrix limits mapped below within `configs/flir_one_pro_calib.json`:

| Configuration Parameter Key | Hardcoded Baseline Matrix Target | Engineering Calibration Purpose |
| :--- | :--- | :--- |
| `nominal_distance_meters` | `1.0` | Calibrated focal distance from the patient interface. |
| `horizontal_pixel_shift` | `+14` | Pixel column index correction to adjust for the 12mm offset. |
| `vertical_pixel_shift` | `-2` | Minor pitch axis adjustments to correct for frame mount variances. |
| `scaling_factor_ratio` | `1.142` | Expansion ratio to scale the thermal matrix onto the RGB plane. |

## 3. Microbolometer Thermal Stabilization Protocol
The FLIR Lepton 3.5 sensor utilizes an internal mechanical shutter mechanism to run an automated calibration pass known as a **Flat Field Correction (FFC)**.
* **FFC Purpose:** This process resets the baseline response for every pixel on the sensor grid, correcting for local sensor heating and preventing pixel drift across the thermal image.
* **Operational Execution:** FFC loops engage automatically upon system boot-up, and rerun roughly every 3 to 5 minutes. During an active FFC pass, the data stream freezes for exactly `800 milliseconds`. 
* **Pipeline Management:** The ingestion worker script `flir_stream_ingest.py` treats these frames as expected tracking pauses rather than dropped packets, preserving calculation continuity across the active session loop.
