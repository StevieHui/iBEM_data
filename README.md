# IBEM_data: A Multi-modal Indoor Environment Dataset for Public Buildings

This is the final, comprehensive English version of your `README.md`. I have integrated the detailed case study table into the **Dataset Overview** and ensured the **Potential Applications** section feels like an open-ended "sandbox" for users.

---

**IBEM_data** is a high-resolution, multi-modal dataset for indoor environmental research, collected via the **IBEMbot** (Intelligent Building Environment Mobile-sensing System) developed by the **School of Architecture, Tsinghua University**.

By utilizing mobile robotics, this dataset provides a unique "walk-through" perspective on indoor environments, bridging the gap between building science, mobile robotics, and occupant-centric research.

---

## 📊 Dataset Overview

The dataset covers over **50,000 $m^2$** across various climate zones and functional public spaces. The following table provides details on the core cases currently included or scheduled for release:

| Case Study (Task Area) | Building Function | Spatial Area | Duration | Climate Zone |
| :--- | :--- | :--- | :--- | :--- |
| **Daxing Airport (Terminal 1F)** | Transportation | 2,200 $m^2$ | 21 Days | Cold |
| **Daxing Airport (Terminal 4F)** | Transportation | 27,000 $m^2$ | 21 Days | Cold |
| **Dahecun Museum** | Exhibition | 11,000 $m^2$ | 16 Days | Cold |
| **CABR Innovation Center** | Office | 1,600 $m^2$ | 11 Days | Cold |
| **Digital City Hall (Haikou)** | Exhibition/Office | 1,600 $m^2$ | 5 Days | Hot-Summer/Warm-Winter |
| **Student Service Center** | Study/Self-study | 1,500 $m^2$ | 5 Days | Cold |
| **THU Arch. Exhibition Hall** | Mixed-use | 500 $m^2$ | 5 Days | Cold |
| **THU Multi-function Hall** | Education | 130 $m^2$ | 2 Days | Cold |

---

## 💡 Potential Applications

This dataset is designed as an open-ended sandbox. The following examples demonstrate how the raw data can be utilized, but we encourage users to explore their own methodologies:

### 1. Spatial-Temporal Field Reconstruction

Using the synchronized `trajectory.csv` and `environment.csv`, users can explore various spatial interpolation algorithms to visualize continuous environmental fields.

* **Algorithm Agnostic:** While we have utilized **RBF (Radial Basis Function)** interpolation, the density of the data allows for Kriging, Gaussian Process Regression, or Neural Field approaches.
* **Example:** Visualizing $CO_2$ hotspots or temperature gradients across a 27,000 $m^2$ airport terminal.
* **Visualization:** (See `assets/field_reconstruction_sample.png` for a sample reconstruction map).

### 2. Occupant Comfort & Health Assessment

Link environmental variables with visual-based occupancy metadata to conduct advanced IEQ (Indoor Environmental Quality) evaluations:

* Map spatial-temporal **PMV/PPD** (Predicted Mean Vote) distributions.
* Analyze the correlation between occupant density and air quality decay in real-time.

### 3. Robotic Perception & Path Planning

The high-precision SLAM trajectories and multi-sensor fusion offer a playground for researchers in **Environment-aware Robotics**, such as optimizing autonomous patrol paths based on environmental fluctuations.

---

## 📂 Directory Structure

The repository follows a strict spatial-temporal organization. Data is partitioned into "Rounds" to represent specific patrol cycles.

```text
IBEM_data/
├── assets/                  # High-resolution field maps and comfort analysis samples
├── codes/                   # Python scripts for data cleaning and round-based processing
├── data/
│   ├── Case01_Daxing/       # Beijing Daxing International Airport
│   │   ├── 20240120_Round01/ # Organized by Date and Patrol Round
│   │   │   ├── environment.csv  # Multi-parameter sensor data (10s interval)
│   │   │   └── trajectory.csv   # Robot pose (x, y, theta)
│   │   └── ...
│   └── Case02_Dahe/         # Zhengzhou Dahecun Museum
│       ├── 20240315_Round01/
│       └── ...
├── .gitignore               # Configured to exclude raw images/videos
└── README.md
```

---

## 🔒 Privacy & Data Access Policy

To comply with **Privacy Protection Regulations** and **Property Management Agreements**, raw image data (RGB and Thermal) is **not** hosted in this public repository.

* **Public Data:** Includes all environmental readings, robot trajectories, processing codes, and metadata.
* **Restricted Data (Images):** If your research requires raw visual data for validation, please contact the team.

### How to Request Access

1. **Contact:** Chen Yihui (陈熠辉), School of Architecture, Tsinghua University.
2. **Email:** [Your Email Address]
3. **Note:** Please provide your affiliation and a brief description of your research intent. Redistribution of raw imagery is strictly prohibited.

---

## 📖 Citation

If you use **IBEM_data** in your research, please cite our work:

```bibtex
@misc{ibemdata2026,
  title={IBEM_data: A Multi-modal Mobile-Sensing Dataset for Public Building Environments},
  author={Yuan, Mufeng and Chen, Yihui},
  institution={Tsinghua University},
  year={2026},
  url={https://github.com/StevieHui/iBEM_data}
}
```
