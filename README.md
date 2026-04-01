# MobilEnv: A Multi-modal Indoor Environment Dataset for Public Buildings

---

**MobilEnv** is a high-resolution, multi-modal dataset for indoor environmental research, collected via the **IBEMbot** (Intelligent Building Environment Mobile-sensing System) developed by the **Key Laboratory of Eco-Planning & Green Building, School of Architecture, Tsinghua University**.

<p align="center">
  <img src="assets/system.png" width="90%" alt="System Overview" />
  <br />
  <em>Figure 1: Intelligent robotic system for indoor environment monitoring.</em>
</p>

By utilizing mobile robotics, this dataset provides a unique "walk-through" perspective on indoor environments, bridging the gap between building science, mobile robotics, and occupant-centric research.

---

## 📊 Dataset Overview

The dataset covers over **50,000 $m^2$** across various climate zones and functional public spaces. The following table provides details on the core cases currently included or scheduled for release:

| Case Study (Task Area) | Building Function | Location | Spatial Area | Duration | Climate Zone |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Daxing Airport (Terminal 1F)** | Transportation | Beijing, China | 2,200 $m^2$ | 21 Days | Cold |
| **Daxing Airport (Terminal 4F)** | Transportation | Beijing, China | 27,000 $m^2$ | 21 Days | Cold |
| **Dahecun Museum** | Exhibition | Zhengzhou, China | 11,000 $m^2$ | 16 Days | Cold |
| **CABR Innovation Center** | Office | Beijing, China | 1,600 $m^2$ | 11 Days | Cold |
| **Digital City Hall** | Exhibition/Office | Haikou, China | 1,600 $m^2$ | 5 Days | Hot-Summer/Warm-Winter |
| **Student Service Center** | Study/Self-study | Beijing, China | 1,500 $m^2$ | 5 Days | Cold |
| **THU Arch. Exhibition Hall** | Mixed-use | Beijing, China | 500 $m^2$ | 5 Days | Cold |
| **THU Multi-function Hall** | Education | Beijing, China | 130 $m^2$ | 2 Days | Cold |
| **Alibaba Group A8 Building** | Office | Hangzhou, China | 320 $m^2$ | 2 Days | Hot-Summer/Cold-Winter |

---

## 💡 Potential Applications

This dataset serves as a multi-modal sandbox integrating building physics with mobile robotics to support the following high-level intelligent tasks:

### 1. Advanced Environmental Perception

* **Indoor Environmental Field Reconstruction\*:** Utilizing sparse mobile sensing data to reconstruct continuous spatial fields (e.g., $CO_2$, PM2.5, Temp) via **IDW, Kriging, Gaussian Processes (GP), or Convolutional Networks (CN)**.
* **IEQ & Occupant Comfort Evaluation\*:** Fusing environmental fields with visual/thermal imagery for **Target Detection and Classification** to assess Predicted Mean Vote (PMV/PPD).
* **Environmental Diagnosis & Expert Systems\*:** Identifying building performance issues (e.g., envelope insulation leaks or HVAC terminal malfunctions) through **Semantic Mapping** and thermal imaging analysis.
* **Multimodal Forecasting:** Predicting future environmental states and field evolutions using temporal-spatial models like **LSTM, GNN, or Graph-based Gaussian Processes**.

<p align="center">
  <img src="assets/reconstruction.gif" width="100%" alt="Field Reconstruction" />
  <br />
  <em>Figure 2: Dynamic Environmental Field Reconstruction of Dahecun Museum.</em>
</p>

### 2. Autonomous Sensing & Decision Making

* **Active Sampling & Path Planning\*:** Developing algorithms that allow robots to autonomously locate areas with high environmental gradients for prioritized sampling using **A*, Dijkstra, or Semantic Navigation**.
* **Mobile-Stationary Collaborative Sensing\*:** Coordinating fixed sensors (high temporal resolution) and mobile robots (high spatial coverage) to capture comprehensive environmental features based on physical baseline tasks.
* **Building Environment Question Answering (QA):** Leveraging **Vision-Language Models (VLMs)** and **LLMs** to interact with the dataset, enabling natural language queries regarding building operational status.

<p align="center">
  <img src="assets/comfort.png" width="80%" alt="Thermal Comfort" />
  <br />
  <em>Figure 3: Visual-based human perception and thermal comfort assessment.</em>
</p>

### 3. Smart Building Operation & Interaction

* **Demand-Oriented HVAC Optimization\*:** Driving energy-efficient "on-demand" HVAC control strategies by mapping environmental loads and real-time occupant behavior.
* **Occupant-Environment Interaction:** Mining physical correlation models between group behaviors and environmental parameter decay to support occupant-centric building design.
* **Environmental Event Response:** Utilizing mobile sensing for rapid localization and decision-making during sudden events like pollutant leaks or equipment failures.

<p align="center">
  <img src="assets/control.png" width="90%" alt="Thermal Comfort" />
  <br />
  <em>Figure 4: Multi‑Source Sensing Framework for Intelligent Precise IEQ Evaluation and HVAC Control.</em>
</p>

---

## 📂 Directory Structure

The repository follows a strict spatial-temporal organization. Data is partitioned into "Rounds" to represent specific patrol cycles.

```text
MobilEnv/
├── 📂 assets/                         # Documentation assets (Protocols, diagrams, icons)
├── 📄 README.md                       # Main project documentation & workflow guide
├── 📄 .gitignore                      # Version control exclusion rules
│
├── 📂 data_dahe/ ──────────────────── # CASE 1: DAHECUN MUSEUM (ZHENGZHOU)
│   ├── 📂 light_csv/                  # Datasets with dedicated illuminance (Lux) points
│   │   ├── 📂 Environmental Field/    # 🛠️ Spatial field generation module
│   │   │   ├── 📜 field_gen_official.py
│   │   │   └── 📜 field_gen_test.py
│   │   ├── 📜 01_raw_data_sorting.py  # Data pre-processing & cleaning
│   │   ├── 📜 02_auto_lap_segment.py  # Automated round segmentation
│   │   └── 📊 test_dahe_light_calibrated.csv
│   ├── 📂 nolight_csv/                # Datasets excluding dedicated illuminance points
│   │   ├── 📜 01_raw_data_sorting.py
│   │   ├── 📜 02_auto_lap_segment.py
│   │   └── 📊 test_dahe_nolight_calibrated.csv
│   ├── 📂 photos/                     # [IGNORED] Raw imagery storage
│   └── 📂 raw_csv/                    # Original source files for Dahe Case
│       ├── 📊 point_label.csv         # Global coordinates of sensing points (Ground Truth)
│       └── 📊 test_dahe_formal.csv    # Main integrated raw dataset
│
├── 📂 data_daxing/ ────────────────── # CASE 2: DAXING AIRPORT (BEIJING)
│   ├── 📂 Environmental Field_LAPS/   # 🌐 GLOBAL FIELD HUB
│   │   └── 📦 (e.g., 1212_1.npz, ...) # Interpolated LAPS fields organized by rounds
│   ├── 📂 Environmental Field_REGIONS/ # 🎯 ZONAL PROCESSING & FINAL ASSETS
│   │   ├── 📂 extracted_regions/      # Segmented regional field data (P1–P10)
│   │   ├── 📂 photos/                 # Multi-modal visual dataset
│   │   │   ├── 🖼️ RGB/                # 1,130 segmented RGB images (Complete set)
│   │   │   └── 🌡️ Thermal/            # 1,010 thermal images [12/18 Sensor Fault: -120]
│   │   ├── 📜 rename_photos.py        # Workflow: Batch nomenclature standardization
│   │   ├── 📜 Shapely.py              # Logic: Point-in-polygon spatial filtering
│   │   └── 📜 split_env_fields.py     # Logic: Cropping global fields into P1-P10 zones
│   ├── 📂 raw_csv/                    # Primary sensor time-series (CSV)
│   └── 📂 raw_photos/                 # [IGNORED] Full-resolution original backups
│
└── 📂 data_daxing_adaptive/ ───────── # CASE 3: ADAPTIVE SENSING (HYBRID PATROL)
    ├── 📂 data_processed_adaptive/    # Cleaned time-series by flight/patrol session
    │   ├── 📊 0103-10.csv             # Data: Session 10 on Jan 3rd
    │   ├── 📊 0103-12.csv             # Data: Session 12 on Jan 3rd
    │   └── ...                        [Sessions 0103 to 0105 omitted]
    └── 📂 raw_csv/                    # Raw adaptive patrol rounds
        ├── 📂 20250102_1_Stationary/  # Baseline: Stationary sensing session
        │   ├── 🖼️ RGB/
        │   └── 🌡️ Thermal/
        ├── 📂 20250102_2_Mobile/      # Variable: Mobile patrol session
        └── ...                        [40+ sequential patrol folders archived]
```

---

## 🔒 Privacy & Data Access Policy

To comply with **Privacy Protection Regulations** and **Property Management Agreements**, raw image data (RGB and Thermal) is **not** hosted in this public repository.

* **Public Data:** Includes all environmental readings, robot trajectories, processing codes, and metadata.
* **Restricted Data (Images):** If your research requires raw visual data for validation, please contact the team.

### How to Request Access

1. **Contact:** Yuan Mufeng, School of Architecture, Tsinghua University.
2. **Email:** [yuanmf21@mails.tsinghua.edu.cn]
3. **Note:** Please provide your affiliation and a brief description of your research intent. Redistribution of raw imagery is strictly prohibited.

---

## 📖 Citation

If you use **MobilEnv** in your research, please cite our work:

```bibtex
@misc{MobilEnv2026,
  title={MobilEnv: A Multi-modal Mobile-Sensing Dataset for Public Building Environments},
  author={Yuan, Mufeng and Chen, Yihui},
  institution={Tsinghua University},
  year={2026},
  url={https://github.com/StevieHui/iBEM_data}
}
```
