# 🚦 Urban Traffic Signal Digital Twin with Adaptive and Reinforcement Learning Control

🌐 **[Open the Interactive Streamlit Dashboard](https://urban-traffic-signal-digital-twin.streamlit.app/)**

> A SUMO-based urban traffic signal digital twin comparing Fixed-Time, Actuated, Rule-Based Adaptive, and PPO Reinforcement Learning control across a three-intersection corridor.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SUMO](https://img.shields.io/badge/Simulation-SUMO-green)
![Reinforcement Learning](https://img.shields.io/badge/RL-PPO-orange)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen)

---

## 🌐 Interactive Dashboard

The complete project outputs can be explored through the live Streamlit dashboard:

### 👉 [Launch the Interactive Dashboard](https://urban-traffic-signal-digital-twin.streamlit.app/)

The dashboard provides interactive access to:

* Controller performance comparison
* Mean travel time
* Mean waiting time
* Mean time loss
* Mean trip speed
* Mean and maximum queues
* Stops per vehicle
* Queue evolution over time
* Speed evolution over time
* Research questions and findings

---

# 📌 Project Overview

This project develops a **SUMO-based urban traffic signal digital twin** for a corridor containing three connected signalized intersections.

The project compares four traffic signal control strategies:

1. 🚦 **Fixed-Time Control**
2. ⚡ **Actuated Control**
3. 🔁 **Rule-Based Adaptive Control**
4. 🤖 **PPO Reinforcement Learning Control**

The objective is to evaluate whether increasingly intelligent signal control strategies can improve corridor traffic performance under identical traffic demand conditions.

---

# 🎯 Project Objectives

The project aims to:

1. Develop a three-intersection urban traffic corridor in SUMO.
2. Model bidirectional traffic using two lanes per direction.
3. Establish a Fixed-Time traffic signal baseline.
4. Implement SUMO Actuated traffic signal control.
5. Develop a queue-responsive adaptive signal controller using TraCI.
6. Develop a centralized PPO Reinforcement Learning controller.
7. Evaluate all controllers using identical traffic demand.
8. Compare traffic performance using exact SUMO TripInfo outputs.
9. Visualize the final results through an interactive Streamlit dashboard.

---

# ❓ Research Questions

### RQ1

**How does Fixed-Time traffic signal control perform under the simulated corridor traffic demand?**

### RQ2

**Does Actuated Control improve traffic performance relative to Fixed-Time Control?**

### RQ3

**Can Rule-Based Adaptive Control further reduce traffic congestion?**

### RQ4

**Can PPO Reinforcement Learning outperform conventional and adaptive traffic signal control?**

---

# 🛣️ Traffic Network

The simulated network consists of:

* **3 connected signalized intersections**
* **2 lanes per direction**
* East-West arterial movements
* North-South cross-street movements
* A 3600-second traffic demand period
* Identical demand for all four controllers

The corridor structure is approximately:

```text
        N1          N2          N3
         |           |           |
         |           |           |
W ------ J1 -------- J2 -------- J3 ------ E
         |           |           |
         |           |           |
        S1          S2          S3
```

---

# 🚘 Traffic Demand

The traffic demand includes:

* **West → East:** 900 veh/h
* **East → West:** 700 veh/h
* **North → South:** 300 veh/h at each intersection
* **South → North:** 300 veh/h at each intersection

The same demand is used for all controllers to ensure a fair comparison.

---

# 🔬 Methodology

The complete workflow is:

```text
SUMO Urban Corridor
        ↓
Traffic Demand
        ↓
Fixed-Time Baseline
        ↓
Actuated Control
        ↓
Rule-Based Adaptive Control
        ↓
PPO Reinforcement Learning
        ↓
SUMO TripInfo Evaluation
        ↓
Controller KPI Comparison
        ↓
Figures and Streamlit Dashboard
```

---

# 🚦 Controller 1: Fixed-Time Control

The Fixed-Time controller uses predetermined signal timings.

The baseline signal cycle is:

```text
East-West Green       40 s
East-West Yellow       3 s
North-South Green     25 s
North-South Yellow     3 s
```

Total cycle length:

```text
71 seconds
```

This controller provides the conventional baseline against which the more responsive controllers are evaluated.

---

# ⚡ Controller 2: Actuated Control

The Actuated controller uses SUMO's traffic-responsive signal control.

Green durations can adjust according to traffic demand while respecting minimum and maximum green constraints.

This allows the controller to respond to traffic conditions instead of relying only on fixed timing.

---

# 🔁 Controller 3: Rule-Based Adaptive Control

The Rule-Based Adaptive controller is implemented using **Python and TraCI**.

For each intersection, the controller observes:

* East-West queue
* North-South queue

The basic decision logic is:

```text
If East-West queue > North-South queue:
    favor East-West green

If North-South queue > East-West queue:
    favor North-South green
```

The controller also respects:

* minimum green time
* maximum green time
* yellow transition time

This provides an interpretable adaptive benchmark before reinforcement learning.

---

# 🤖 Controller 4: PPO Reinforcement Learning

The final controller uses **Proximal Policy Optimization (PPO)** implemented with Stable-Baselines3.

A centralized agent controls all three intersections:

```text
J1
J2
J3
```

simultaneously.

## Observation Space

For each intersection, the PPO agent observes:

* normalized East-West queue
* normalized North-South queue
* current signal direction

With three intersections:

```text
3 intersections × 3 variables = 9 observations
```

## Action Space

For each intersection:

```text
0 = request East-West green
1 = request North-South green
```

Example:

```text
[0, 1, 0]
```

means:

```text
J1 → East-West
J2 → North-South
J3 → East-West
```

## Reward Function

The PPO reward penalizes:

* queue accumulation
* vehicle waiting time
* vehicles accumulating in the network

Conceptually:

```text
Reward =
    - Queue Penalty
    - Waiting-Time Penalty
    - Network Congestion Penalty
```

The final PPO V2 model was trained for approximately:

```text
150,000 timesteps
```

and saved as:

```text
models/ppo_traffic_signal_v2.zip
```

---

# 📊 Performance Indicators

All four controllers are evaluated using the same network and traffic demand.

The final performance indicators include:

* Completed vehicles
* Mean travel time
* Mean waiting time
* Mean time loss
* Mean stops per vehicle
* Mean trip speed
* Mean network queue
* Maximum network queue
* Network clearance time

Exact per-vehicle measures are obtained using **SUMO TripInfo output**.

---

# 🏆 Final Controller Results

| KPI                    | Fixed-Time | Actuated | Rule-Based Adaptive |     PPO RL |
| ---------------------- | ---------: | -------: | ------------------: | ---------: |
| Completed vehicles     |       3401 |     3401 |                3401 |   **3401** |
| Mean travel time (s)   |     27.840 |   27.597 |              29.243 | **24.455** |
| Mean waiting time (s)  |     12.461 |    9.473 |               8.963 |  **7.263** |
| Mean time loss (s)     |     18.961 |   18.724 |              20.368 | **15.581** |
| Mean stops/vehicle     |  **0.599** |    0.893 |               1.169 |      0.788 |
| Mean trip speed (km/h) |     14.998 |   15.129 |              14.278 | **17.073** |
| Mean queue (veh)       |     12.134 |    9.788 |               9.327 |  **6.971** |
| Maximum queue (veh)    |         31 |       29 |                  26 |     **19** |

---

# ✅ Answers to the Research Questions

## RQ1 — How does Fixed-Time Control perform?

Fixed-Time Control successfully serves all **3401 vehicles**, but it produces the largest average queue and maximum queue among the evaluated controllers.

It provides a stable conventional baseline but is less responsive to changing traffic conditions.

---

## RQ2 — Does Actuated Control improve performance?

**Yes, partially.**

Compared with Fixed-Time Control, Actuated Control reduces:

* mean waiting time
* mean queue
* maximum queue

and slightly improves:

* travel time
* mean trip speed

However, the number of stops per vehicle increases.

---

## RQ3 — Does Rule-Based Adaptive Control further improve traffic operations?

The Rule-Based Adaptive controller performs well in queue reduction.

Compared with Fixed-Time Control, it produces:

* lower mean queue
* lower maximum queue
* lower waiting time

However, it also produces:

* higher travel time
* higher time loss
* more stops per vehicle

This demonstrates that **minimizing queue length alone does not guarantee the best overall traffic performance**.

---

## RQ4 — Can PPO Reinforcement Learning outperform the other controllers?

**Yes, for most major traffic-performance indicators.**

The PPO RL controller achieves the best:

* mean travel time
* mean waiting time
* mean time loss
* mean trip speed
* mean queue
* maximum queue

Fixed-Time Control remains best only for the number of stops per vehicle.

---

# 📈 PPO Improvement over Actuated Control

Compared with Actuated Control, PPO RL achieves approximately:

* **11.4% lower mean travel time**
* **23.3% lower mean waiting time**
* **16.8% lower mean time loss**
* **12.8% higher mean trip speed**
* **28.8% lower mean queue**
* **34.5% lower maximum queue**

These results indicate that the learned PPO control policy provides a stronger overall balance across several competing traffic-performance objectives.

---

# 💡 Key Findings

✅ All controllers successfully served the full traffic demand.

✅ Actuated Control reduced congestion relative to Fixed-Time Control.

✅ Rule-Based Adaptive Control reduced queues but worsened several other efficiency measures.

✅ PPO Reinforcement Learning produced the strongest overall traffic performance.

✅ PPO achieved the lowest travel time, waiting time, time loss, average queue, and maximum queue.

✅ PPO achieved the highest mean trip speed.

⚠️ Fixed-Time Control still produced the lowest number of stops per vehicle.

💡 The results show that effective traffic signal control requires balancing several traffic objectives rather than optimizing only one measure.

---

# 📊 Generated Figures

The project automatically generates:

```text
figures/
├── 01_mean_travel_time.png
├── 02_mean_waiting_time.png
├── 03_mean_time_loss.png
├── 04_mean_stops.png
├── 05_mean_trip_speed.png
├── 06_mean_queue.png
├── 07_max_queue.png
├── 08_clearance_time.png
├── 09_queue_over_time.png
└── 10_speed_over_time.png
```

The figures compare all four controllers and visualize both final KPIs and traffic evolution over time.

---

# 🌐 Interactive Streamlit Dashboard

The project includes a live interactive Streamlit dashboard.

### 🚀 [Open the Live Dashboard](https://urban-traffic-signal-digital-twin.streamlit.app/)

The dashboard allows users to:

* compare controller KPIs
* select performance indicators interactively
* inspect traffic-performance figures
* compare traffic conditions over time
* examine queue evolution
* examine speed evolution
* review research questions and findings

To run the dashboard locally:

```bash
streamlit run app.py
```

---

# 📁 Repository Structure

```text
urban-traffic-signal-digital-twin/
│
├── README.md
├── requirements.txt
├── app.py
├── run_all.py
├── run_baseline.py
├── run_actuated.py
├── run_adaptive.py
├── run_rl_tripinfo.py
│
├── rl/
│   └── traffic_signal_env.py
│
├── training/
│   └── train_rl.py
│
├── evaluation/
│   ├── kpi_utils.py
│   ├── generate_figures.py
│   └── summarize_tripinfo.py
│
├── models/
│   └── ppo_traffic_signal_v2.zip
│
├── sumo/
│   ├── network.net.xml
│   ├── network_actuated.net.xml
│   ├── routes.rou.xml
│   ├── simulation.sumocfg
│   └── simulation_actuated.sumocfg
│
├── results/
│
└── figures/
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Biruhi/urban-traffic-signal-digital-twin.git
```

Enter the project directory:

```bash
cd urban-traffic-signal-digital-twin
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

# 🚦 SUMO Requirement

SUMO must be installed separately to rerun the simulations.

The `SUMO_HOME` environment variable must also be configured.

The deployed Streamlit dashboard does **not** require SUMO because it reads the saved project results and figures.

---

# ▶️ Run the Complete Project

The trained PPO model is already included, so PPO does **not** need to be retrained every time.

Run:

```bash
python run_all.py
```

This executes:

```text
Fixed-Time Control
        ↓
Actuated Control
        ↓
Rule-Based Adaptive Control
        ↓
PPO RL Evaluation
        ↓
Final Comparison Table
        ↓
Final Figures
```

---

# 🧠 Retrain PPO

Retraining is optional.

To intentionally train a new PPO model:

```bash
python training/train_rl.py
```

The trained model is saved as:

```text
models/ppo_traffic_signal_v2.zip
```

---

# 🌐 Run the Dashboard Locally

```bash
streamlit run app.py
```

The dashboard normally opens at:

```text
http://localhost:8501
```

The hosted version is available at:

### 👉 https://urban-traffic-signal-digital-twin.streamlit.app/

---

# 📦 Python Requirements

The main Python packages are:

```text
numpy
pandas
matplotlib
gymnasium
stable-baselines3
torch
streamlit
```

---

# 🛠️ Technologies

* Python
* SUMO
* TraCI
* Gymnasium
* Stable-Baselines3
* PPO Reinforcement Learning
* Pandas
* NumPy
* Matplotlib
* Streamlit

---

# 🎓 Project Relevance

This project demonstrates the integration of:

**Traffic Signal Control**
↓
**Microscopic Traffic Simulation**
↓
**Real-Time Traffic State Monitoring**
↓
**Adaptive Traffic Control**
↓
**Reinforcement Learning**
↓
**Traffic Digital Twin**
↓
**Interactive Decision-Support Visualization**

It provides a practical demonstration of how artificial intelligence can be integrated with microscopic traffic simulation for intelligent urban traffic management.

---

# 🔭 Future Improvements

Potential extensions include:

* Multi-agent reinforcement learning
* Larger urban traffic networks
* Dynamic and stochastic traffic demand
* Incident scenarios
* Pedestrian phases
* Transit signal priority
* Emergency vehicle priority
* Connected-vehicle information
* Emission and fuel-consumption objectives
* Multi-objective reinforcement learning
* Real-world detector-data calibration
* Transferability testing across different networks

---

# 📌 Main Takeaway

> **PPO Reinforcement Learning provided the strongest overall traffic performance among the evaluated traffic signal controllers by reducing travel time, waiting time, time loss, and queue formation while increasing corridor travel speed.**

---

## 🌐 Live Project

### 🚦 [Explore the Interactive Streamlit Dashboard](https://urban-traffic-signal-digital-twin.streamlit.app/)

---

## 👤 Author

**Biruhi Tesfaye Abeje**

Transportation Engineering | Traffic Simulation | Intelligent Transportation Systems | Machine Learning | Reinforcement Learning
