# Stewart Platform — Python Inverse Kinematics

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.19%2B-013243?logo=numpy)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.3%2B-11557c)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A **real-time interactive simulator** of a Stewart Platform with full 6-DOF inverse kinematics, built entirely in Python. Supports both **linear actuators** and **rotational servo** drive systems.

> Move sliders — watch the platform respond instantly in 3D.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [License](#license)

---

## Overview

A **Stewart Platform** (hexapod) is a parallel manipulator with six degrees of freedom — three translational (X, Y, Z) and three rotational (Roll, Pitch, Yaw). It is widely used in:

- Flight simulators and motion platforms
- Industrial precision positioning
- Camera stabilization systems
- Medical and rehabilitation robotics

This project provides a clean Python implementation of the inverse kinematics for both actuator types, plus an interactive Matplotlib GUI to explore the solution space in real time.

---

## Features

- **Real-time 3D visualization** — platform geometry updates instantly as you move sliders
- **Linear actuator IK** — compute all 6 leg lengths from a desired pose
- **Rotational servo IK** — compute all 6 servo angles with horn-and-rod geometry
- **Top-down 2D view** — XY projection of base and moving platform
- **Live bar chart** — actuator lengths or servo angles per leg
- **One-click reset** — return to neutral home position
- **Zero external GUI dependencies** — runs with standard `numpy` + `matplotlib`

---

## Requirements

| Package    | Version |
|------------|---------|
| Python     | ≥ 3.8   |
| NumPy      | ≥ 1.19  |
| Matplotlib | ≥ 3.3   |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Stewart_Py.git
cd Stewart_Py

# 2. (Optional) Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install numpy matplotlib
```

---

## Quick Start

```bash
python app.py
```

A window will open with the interactive simulator. Use the six sliders to control the platform pose.

---

## Usage

### Interactive Application

```
┌─────────────────────────┬──────────────────────────┐
│                         │  Top-down view (XY)      │
│   3D Platform View      │                          │
│                         ├──────────────────────────┤
│   Green  = Base         │  Actuator lengths (mm)   │
│   Blue   = Platform     │  per leg — live chart    │
│   Colors = Actuators    │                          │
└─────────────────────────┴──────────────────────────┘
   [ Tx ] [ Ty ] [ Tz ]      [ Roll ] [ Pitch ] [ Yaw ]
                      [ Reset ]
```

| Control | Range | Description |
|---|---|---|
| **Tx / Ty / Tz** | ±20 mm | Platform translation along X, Y, Z axes |
| **Roll** | ±20° | Rotation around X axis |
| **Pitch** | ±20° | Rotation around Y axis |
| **Yaw** | ±20° | Rotation around Z axis |
| **Reset** | — | Return all sliders to zero |

### Using the Library in Your Code

#### Linear Actuators

```python
import numpy as np
from src.stewart_controller import Stewart_Platform_Linear

platform = Stewart_Platform_Linear(
    r_B=66,          # base circle radius (mm)
    r_P=50,          # platform circle radius (mm)
    gamma_B=0.2269,  # base anchor half-angle (rad)
    gamma_P=0.82,    # platform anchor half-angle (rad)
    home_z=132,      # neutral height (mm)
    ref_rotation=0   # reference rotation around Z (rad)
)

# Compute leg lengths for a desired pose
leg_lengths = platform.calculate(
    trans=np.array([10, 0, 5]),       # translation [tx, ty, tz] mm
    rotation=np.array([0.1, 0.2, 0]) # rotation [roll, pitch, yaw] rad
)

print(leg_lengths)  # [L1, L2, L3, L4, L5, L6] in mm
```

#### Rotational Servos

```python
from src.stewart_controller import Stewart_Platform

platform = Stewart_Platform(
    r_B=66,           # base radius (mm)
    r_P=50,           # platform radius (mm)
    lhl=30,           # servo horn length (mm)
    ldl=130,          # rod length (mm)
    gamma_B=0.2269,
    gamma_P=0.82,
    ref_rotation=5 * np.pi / 6
)

servo_angles = platform.calculate(
    trans=np.array([0, 0, 0]),
    rotation=np.array([0, 0.2, 0])
)

print(servo_angles)  # [α1..α6] in radians
```

---

## API Reference

### `Stewart_Platform_Linear`

```
Stewart_Platform_Linear(r_B, r_P, gamma_B, gamma_P, home_z, ref_rotation=0)
```

| Parameter | Type | Description |
|---|---|---|
| `r_B` | float | Radius of the base anchor circle (mm) |
| `r_P` | float | Radius of the platform anchor circle (mm) |
| `gamma_B` | float | Half-angle between anchor pairs on the base (rad) |
| `gamma_P` | float | Half-angle between anchor pairs on the platform (rad) |
| `home_z` | float | Platform height at neutral position (mm) |
| `ref_rotation` | float | Reference rotation of the whole assembly around Z (rad) |

#### `calculate(trans, rotation) → np.ndarray`

| Parameter | Type | Description |
|---|---|---|
| `trans` | array-like [3] | Translation vector `[tx, ty, tz]` in mm |
| `rotation` | array-like [3] | Rotation vector `[roll, pitch, yaw]` in radians |
| **returns** | ndarray [6] | Leg lengths in mm |

**State attributes set after `calculate()`:**

| Attribute | Shape | Description |
|---|---|---|
| `platform.B` | (3, 6) | Base anchor positions (global frame) |
| `platform.L` | (3, 6) | Platform anchor positions (global frame) |
| `platform.l` | (3, 6) | Leg vectors (from B to L) |
| `platform.lll` | (6,) | Leg lengths (same as return value) |

---

### `Stewart_Platform`

```
Stewart_Platform(r_B, r_P, lhl, ldl, gamma_B, gamma_P, ref_rotation)
```

| Parameter | Type | Description |
|---|---|---|
| `lhl` | float | Servo horn length \|h\| (mm) |
| `ldl` | float | Rod length \|d\| (mm) |
| *(others)* | | Same as `Stewart_Platform_Linear` |

#### `calculate(trans, rotation) → np.ndarray`

Returns servo angles `[α1..α6]` in **radians**.

Additional state attribute:

| Attribute | Shape | Description |
|---|---|---|
| `platform.H` | (3, 6) | Horn tip positions — spherical joint between horn and rod |
| `platform.angles` | (6,) | Servo angles in radians |

---

## Project Structure

```
Stewart_Py-main/
│
├── app.py                    # Interactive GUI application (entry point)
│
├── src/
│   └── stewart_controller.py # Inverse kinematics library
│       ├── Stewart_Platform         # Rotational servo actuators
│       └── Stewart_Platform_Linear  # Linear actuators
│
└── LICENSE
```

---

## How It Works

### Coordinate System

```
        Z
        │
        │   Platform (blue)
        │  ╱─────────────╲
        │ ╱   actuators   ╲
        │╱─────────────────╲
        └──────────────────── X
       ╱
      Y
     Base (green)
```

### Inverse Kinematics — Linear Actuators

Given desired translation **T** and rotation matrix **R**, the leg vector for leg *i* is:

```
lᵢ = T + H + R·Pᵢ − Bᵢ
```

Where:
- **H** — neutral home position `[0, 0, home_z]`
- **Pᵢ** — platform anchor in platform-local frame
- **Bᵢ** — base anchor in world frame

The required actuator length is simply the Euclidean norm:

```
|lᵢ| = ‖lᵢ‖₂
```

### Inverse Kinematics — Rotational Servos

Each servo rotates a horn of length |h| at an azimuth angle βₖ. The servo elevation angle αₖ is solved analytically:

```
αₖ = arcsin(g / √(e² + f²)) − arctan2(f, e)
```

Where auxiliary quantities `g`, `e`, `f` depend only on leg geometry and are computed without iteration.

---

## License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.

---

*Based on the inverse kinematics formulation by [Robert Eisele](https://www.xarg.org/paper/inverse-kinematics-of-a-stewart-platform/) and [hbartle's MATLAB implementation](https://github.com/hbartle/Stewart_Platform/).*
