<div align="center">

# 🛰️ Wi-Fi CSI 3D Indoor Localization

**Privacy-Preserving, Device-Free Human Tracking using Channel State Information**

[![Platform](https://img.shields.io/badge/Platform-ESP32--C6_Super_Mini-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32-c6)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Wi-Fi](https://img.shields.io/badge/Standard-IEEE_802.11ax_(Wi--Fi_6)-00AEF0?style=for-the-badge&logo=wifi&logoColor=white)]()
[![License](https://img.shields.io/badge/License-GPLv3-blue?style=for-the-badge)](LICENSE)

*A real-time 3D indoor human localization system that tracks people using only Wi-Fi signals — no cameras, no wearables, no cloud.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Results](#-key-results)
- [System Architecture](#-system-architecture)
- [Hardware](#%EF%B8%8F-hardware)
- [Algorithm Pipeline](#-algorithm-pipeline)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Digital Twin Simulation](#-digital-twin-simulation)
- [Node Placement Strategy](#-node-placement-strategy)
- [Use Cases](#-use-cases)
- [Future Scope](#-future-scope)
- [References](#-references)
- [Authors](#-authors)

---

## 🔍 Overview

Indoor localization is a critical enabler for smart environments, yet existing solutions suffer from fundamental limitations:

| Approach | Limitation |
| :--- | :--- |
| **Camera Systems** | Privacy-invasive; legally restricted (GDPR) in hospitals, bathrooms, residences |
| **Bluetooth/UWB Tags** | Requires the tracked person to carry a device — unsuitable for dementia care, intruder detection |
| **PIR Sensors** | Binary presence only — no spatial coordinate information |
| **GPS** | Functionally ineffective indoors due to signal attenuation |

**This project takes a fundamentally different approach.** It repurposes the Wi-Fi Channel State Information (CSI) — fine-grained physical-layer data already present in every IEEE 802.11ax packet — to detect, quantify, and geometrically triangulate human-induced multipath interference across four spatially distributed ESP32-C6 receiver nodes. The result is a real-time 3D coordinate estimate `(X, Y, Z)` of a person's position, without requiring any hardware on the person and without capturing any visual or biometric data.

> **How it works in one sentence:** When a human body moves through a room, it disturbs the Wi-Fi waves between the router and the sensors. This system measures *how* each of 64 radio frequencies is disturbed at each sensor, and uses the pattern of disturbances to calculate exactly where the person is standing — in three dimensions.

---

## 📊 Key Results

| Metric | Value |
| :--- | :--- |
| **Localization Accuracy (RMSE)** | 0.5 – 0.89 m |
| **Update Rate** | 10 – 15 Hz |
| **Z-axis Height Discrimination** | ~0.35 m (sitting vs. standing) |
| **False Positive Rate (empty room)** | < 3% |
| **Battery Runtime per Node** | 8.5 – 11 hours |
| **End-to-End Latency** | < 150 ms |
| **Total Hardware Cost (4 nodes)** | < ₹2,500 (~$30 USD) |

---

## 🏗 System Architecture

The system is organized into three layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARDWARE SENSING LAYER                       │
│                                                                 │
│   ┌──────────┐    802.11ax     ┌──────────┐  ┌──────────┐     │
│   │  Generic  │───Beacon/CSI──▶│  Node 1  │  │  Node 2  │     │
│   │  Router   │───Beacon/CSI──▶│ (High)   │  │  (Low)   │     │
│   │ (2.4 GHz) │───Beacon/CSI──▶│  Node 3  │  │  Node 4  │     │
│   └──────────┘───Beacon/CSI──▶│  (Low)   │  │ (High)   │     │
│                                └─────┬────┘  └─────┬────┘     │
│                                      │             │           │
└──────────────────────────────────────┼─────────────┼───────────┘
                                       │  UDP:5001   │
┌──────────────────────────────────────┼─────────────┼───────────┐
│               SIGNAL PROCESSING LAYER│             │           │
│                                      ▼             ▼           │
│                           ┌─────────────────────────┐          │
│                           │   multi_node_collector   │          │
│                           │   (UDP Packet Listener)  │          │
│                           └────────────┬────────────┘          │
│                                        │                       │
│                           ┌────────────▼────────────┐          │
│                           │      tracker_3d.py       │          │
│                           │  ┌─────┐ ┌─────┐ ┌───┐  │          │
│                           │  │ MVS │→│ WCT │→│EMA│  │          │
│                           │  └─────┘ └─────┘ └───┘  │          │
│                           └────────────┬────────────┘          │
└────────────────────────────────────────┼───────────────────────┘
                                         │
┌────────────────────────────────────────┼───────────────────────┐
│                VISUALIZATION LAYER     │                       │
│                           ┌────────────▼────────────┐          │
│                           │    visualizer_3d.py      │          │
│                           │  Matplotlib 3D Renderer  │          │
│                           │  Real-time Neon Radar UI │          │
│                           └─────────────────────────┘          │
└────────────────────────────────────────────────────────────────┘
```

### Power Chain (Per Node)

```
18650 Li-ion Cell ──▶ TP4056 Charger ──▶ MT3608 Boost (→5.0V) ──▶ ESP32-C6
   (3.7V, 2500mAh)     (CC/CV, DW01A       (Calibrated via          (VIN pin)
                         protection)         potentiometer)
```

> ⚠️ **Critical Safety Note:** The MT3608 output **must** be calibrated to exactly 5.0V with a multimeter *before* connecting to the ESP32-C6. Factory default output can be 12–20V, which will permanently destroy the microcontroller.

---

## 🛠️ Hardware

### List of Materials (Per Node)

| Component | Model | Qty | 
| :--- | :--- | :---: | 
| Microcontroller | ESP32-C6 Super Mini (RISC-V, Wi-Fi 6) | 1 |
| Battery | 18650 Li-ion Cell, 3.7V 2500mAh | 1 | 
| Charger | TP4056 USB-C Module with DW01A protection | 1 | 
| Boost Converter | MT3608 DC-DC Step-Up (2V→5V, 1.2MHz) | 1 |
| Wiring | 22 AWG silicone wire, solder | — | 



### ESP32-C6 Super Mini Specifications

| Parameter | Value |
| :--- | :--- |
| CPU | 32-bit RISC-V, single core @ 160 MHz |
| Wi-Fi | IEEE 802.11ax (Wi-Fi 6), 2.4 GHz |
| CSI Support | 64 subcarriers, amplitude + phase per packet |
| Flash / SRAM | 4 MB / 512 KB |
| Board Size | 22.5 mm × 18 mm |
| Operating Voltage | 3.0V – 3.6V (3.3V nominal) |
| Active Current | ~250 mA peak during Wi-Fi Tx |

---

## 🧠 Algorithm Pipeline

The localization engine implements a three-stage signal processing pipeline:

### Stage 1 — Mean Variance Smoothing (MVS)

Detects human-induced disturbances in the Wi-Fi channel. For each incoming packet containing 64 OFDM subcarrier amplitudes `[S₁, S₂, ..., S₆₄]`:

```
Var = (1/64) × Σᵢ (Sᵢ − S̄)²
```

The variance is computed over a sliding window of 10 packets and compared against an empty-room baseline. A human body in the Fresnel zone causes a statistically significant spike in this metric — unlike RSSI, which is affected by static environmental changes (doors closing, furniture movement), variance only responds to *moving* reflectors.

### Stage 2 — Weighted Centroid Triangulation (3D-WCT)

Converts per-node variance values into a 3D coordinate estimate. The system treats each node as a gravitational attractor whose "pull" is proportional to the squared variance:

```
wᵢ = Varᵢ² / Σⱼ Varⱼ²          (Quadratic weighting)

P_estimated = Σᵢ (wᵢ × Posᵢ)    (Weighted centroid)
```

**Why quadratic weighting?** Squaring the variance creates a non-linear response that aggressively suppresses distant-node noise contributions and sharpens spatial resolution around the dominant (nearest) node. This was empirically validated to outperform both linear (`v¹`) and cubic (`v³`) weighting.

### Stage 3 — Exponential Moving Average (EMA)

Smooths the raw position estimate to eliminate packet-level jitter:

```
P_final = α × P_new + (1 − α) × P_previous,   α = 0.2
```

At `α = 0.2`, the filter has a time constant of approximately `4 × (1/update_rate)` seconds, comfortably tracking human walking speeds of 0.5–1.5 m/s while suppressing instantaneous noise spikes.

---

## 📁 Project Structure

```
espectre/
├── 3d-tracking/                     # Core localization engine
│   ├── tracker_3d.py                # 3D-WCT + EMA algorithm implementation
│   ├── visualizer_3d.py             # Real-time 3D Neon Radar UI (Matplotlib)
│   ├── multi_node_collector.py      # UDP packet listener (4-node sync)
│   ├── data_inspector.py            # CSI variance analysis & plotting
│   ├── generate_synthetic_data.py   # Digital Twin biometric motion generator
│   ├── generate_accuracy_report.py  # RMSE / MAE validation against ground truth
│   ├── generate_report_graph.py     # Publication-quality figure generator
│   ├── generate_spatial_blueprint.py
│   ├── geometry_config.json         # Room dimensions + node coordinates
│   └── debug_udp.py                 # Low-level UDP diagnostics
│
├── micro-espectre/                  # ESP32 firmware (Micro-ESPectre)
│   ├── src/
│   │   ├── main.py                  # Boot sequence, Wi-Fi, MQTT, UDP stream
│   │   ├── config.py                # Configuration loader
│   │   ├── config_local.py.example  # Template for local Wi-Fi/IP settings
│   │   └── mqtt/
│   │       └── handler.py           # MQTT connectivity handler
│   ├── main.py                      # Firmware entrypoint
│   ├── requirements.txt
│   └── README.md
│
├── README.md            # ← You are here
├── requirements.txt     # Python dependencies
├── .gitignore
└── LICENSE
```

---

## 🚀 Setup Guide

This guide walks through the complete setup — from buying parts to seeing your first 3D tracking output.

### Prerequisites

- **Python 3.10+** (with pip)
- **Thonny IDE** or **esptool.py** (for flashing firmware to ESP32)
- **Soldering iron** (for power circuit assembly)
- **Multimeter** (for voltage calibration — critical for safety)
- **Wi-Fi router** operating on the **2.4 GHz band**

### Step 1 — Clone & Install

```bash
git clone https://github.com/59pixels/ghost-track.git
cd ghost-track
pip install -r requirements.txt
```

### Step 2 — Hardware Assembly (Per Node)

Wire each node's power circuit in this exact order:

```
18650 Battery ──▶ TP4056 (B+/B-) ──▶ MT3608 (VIN+/VIN-) ──▶ ESP32-C6 (5V/GND)
```

> ⚠️ **CRITICAL:** Before connecting the ESP32, use a multimeter to adjust the MT3608 potentiometer until the output reads **exactly 5.0V**. The factory default can be 12–20V, which will **permanently destroy** the ESP32.

### Step 3 — Flash Firmware

1. Connect each ESP32-C6 via USB-C to your laptop.
2. Open **Thonny** (or use `esptool.py`) and upload the contents of `micro-espectre/src/` to the device.
3. Create a `config_local.py` on each device with your Wi-Fi credentials:

```python
# micro-espectre/src/config_local.py (DO NOT commit this file)
# The elements should be in this specific order or else it throws unnecessary errors 
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourWiFiPassword"
MQTT_TOPIC = "home/espectre/node1"      # Change per node (node1, node2, etc.) {Does not matter as the MQTT Broker is not used} 
MQTT_CLIENT_ID = "micro-espectre-1"     # Change per node {Does not matter as the MQTT Broker is not used}
STREAM_DEST_IP = "192.168.1.100"        # Your laptop's local IP address
```

A template is provided at `micro-espectre/src/config_local.py.example`.

### Step 4 — Configure Room Geometry

Measure your room and edit `3d-tracking/geometry_config.json`:

```json
{
    "room": {
        "length_m": 2.78,
        "width_m": 3.61,
        "height_m": 2.88
    },
    "nodes": [
        { "id": 1, "ip": "192.168.1.15", "pos": [0.1, 0.1, 2.7], "role": "anchor_high" },
        { "id": 2, "ip": "192.168.1.16", "pos": [2.6, 0.1, 0.3], "role": "anchor_low" },
        { "id": 3, "ip": "192.168.1.18", "pos": [0.1, 3.5, 0.3], "role": "anchor_low" },
        { "id": 4, "ip": "192.168.1.19", "pos": [2.6, 3.5, 2.7], "role": "anchor_high" }
    ]
}
```

- Update `ip` fields to match the IPs your router assigns to each ESP32.
- Update `pos` fields `[x, y, z]` in metres — measured from the door corner `(0, 0, 0)`.
- Set `role` to `anchor_high` for ceiling-mounted nodes, `anchor_low` for floor-mounted.

### Step 5 — Mount the Nodes

Place the 4 nodes in a **Zig-Zag** pattern (see [Node Placement Strategy](#-node-placement-strategy) below). Use velcro strips or adhesive putty. Keep the PCB antenna clear of walls and metal.

### Step 6 — Run the System

```bash
# === OPTION A: Live Mode (hardware required) ===
# Terminal 1 — Start the UDP packet collector
python 3d-tracking/multi_node_collector.py

# Terminal 2 — Launch the 3D Radar Visualizer
python 3d-tracking/visualizer_3d.py


# === OPTION B: Simulation Mode (no hardware needed) ===
# Generate synthetic human walking data
python 3d-tracking/generate_synthetic_data.py

# Launch the visualizer (auto-detects synthetic data)
python 3d-tracking/visualizer_3d.py
```

### Step 7 — Validate Accuracy

```bash
# Generate RMSE/MAE accuracy report with ground truth comparison
python 3d-tracking/generate_accuracy_report.py
```

---

## 🧬 Digital Twin Simulation

A parallel simulation framework was developed to validate all algorithms independently of hardware availability. The Digital Twin generates synthetic CSI data that models:

- **Waypoint-based navigation** — virtual human walks between points of interest in the room
- **Sigmoid velocity curves** — realistic acceleration/deceleration at waypoints
- **Body sway noise** — Gaussian micro-jitter on X/Y axes (σ = 0.02m)
- **Walking cadence** — 1.8 Hz vertical oscillation on Z-axis matching human gait
- **Inverse-square signal model** — CSI variance scales as `18.0 / (distance + 0.4)²`

```bash
# Generate synthetic walking data
python 3d-tracking/generate_synthetic_data.py

# Validate algorithm accuracy against ground truth
python 3d-tracking/generate_accuracy_report.py
# Output: RMSE = 0.89m, MAE = 0.72m
```

---

## 📐 Node Placement Strategy

The four nodes are arranged in a **Zig-Zag Tetrahedron** configuration — alternating between ceiling-level and floor-level placement at opposite corners:

```
         Back Wall (3.61m)
    ┌─────────────────────────┐
    │ ● Node 1 (HIGH, 2.7m)  │  ○ Node 2 (LOW, 0.3m) │
    │   Back-Left Ceiling     │    Back-Right Floor     │
    │                         │                         │
    │        ╲               ╱│                         │
    │         ╲   SENSING   ╱ │                         │
    │          ╲  VOLUME   ╱  │     2.78m               │
    │           ╲         ╱   │                         │
    │            ╲       ╱    │                         │
    │                         │                         │
    │ ○ Node 3 (LOW, 0.3m)   │  ● Node 4 (HIGH, 2.7m) │
    │   Front-Left Floor      │    Front-Right Ceiling  │
    └─────────────────────────┘
          Front Wall (DOOR)
          Origin (0, 0, 0)

    ● = HIGH placement (ceiling, ~2.7m) — tracks head/shoulder motion
    ○ = LOW placement (floor, ~0.3m)    — tracks gait & fall events
```

**Why this layout?** By placing nodes at alternating heights, the Fresnel zones between pairs of nodes cross-hatch the room volume at multiple angles. This creates a true 3D sensing mesh with no planar blind spots — essential for distinguishing sitting vs. standing (`Z-axis`), which a flat 2D array cannot achieve.

---

## 🌍 Use Cases

| Domain | Application | Key Mechanism |
| :--- | :--- | :--- |
| **Healthcare** | Elderly fall detection | Z-axis height drop detection in privacy-sensitive areas (bathrooms, bedrooms) |
| **Smart Home** | Adaptive HVAC & lighting | Zone-specific environmental control based on precise occupant location |
| **Security** | Volumetric intrusion detection | Full trajectory mapping of intruders without line-of-sight cameras |
| **Fitness** | Automated rep counting | Z-axis oscillation frequency analysis for pushups, squats, jumping jacks |
| **Retail** | Customer dwell-time analytics | Spatial zone heatmaps for store layout optimization |

---

## 🔮 Future Scope

- **Multi-Target Tracking via Deep Learning** — CNN + LSTM to decompose composite CSI signatures from multiple simultaneous occupants
- **Full Activity Recognition** — FFT-based frequency domain feature extraction to classify walking, running, falling, and exercises from Z-axis time series
- **Multi-Room Localization** — Extending the node mesh across adjacent rooms with cross-room trajectory handoff
- **On-Device Edge Inference** — Migrating MVS and lightweight tracking to ESP32-C6 using TensorFlow Lite Micro, eliminating the central server
- **Transfer Learning** — Rapid fine-tuning of a base model for new environments using minimal calibration data
- **Smart Home Integration** — MQTT bridge to Home Assistant, Apple HomeKit, and Google Home ecosystems

---

## 📚 References

1. Adib, F. & Katabi, D. (2013). *See Through Walls with Wi-Fi!* ACM SIGCOMM.
2. Kotaru, M. et al. (2015). *SpotFi: Decimeter Level Localization Using WiFi.* ACM SIGCOMM.
3. Wang, X. et al. (2017). *DeepFi: Deep Learning for Indoor Fingerprinting.* Neurocomputing.
4. Ma, Y. et al. (2019). *SignFi: Sign Language Recognition Using WiFi.* ACM IMWUT.
5. Li, X. et al. (2016). *IndoTrack: Device-Free Indoor Human Tracking with CSI.* ACM UbiComp.

---

## Contributors
Ratnaraj Chakraborty
Sunandan Datta

---

</div>
