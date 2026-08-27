from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Urban Traffic Signal Digital Twin",
    page_icon="🚦",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


# =========================================================
# HELPERS
# =========================================================
@st.cache_data
def load_csv(filename):
    path = RESULTS / filename

    if not path.exists():
        return None

    return pd.read_csv(path)


def show_image(filename, caption=None):
    path = FIGURES / filename

    if path.exists():
        st.image(
            str(path),
            caption=caption,
            use_container_width=True,
        )


# =========================================================
# LOAD FINAL RESULTS
# =========================================================
comparison = load_csv(
    "controller_comparison.csv"
)

fixed_ts = load_csv(
    "fixed_time_timeseries.csv"
)

actuated_ts = load_csv(
    "actuated_timeseries.csv"
)

adaptive_ts = load_csv(
    "adaptive_timeseries.csv"
)

rl_ts = load_csv(
    "rl_v2_timeseries.csv"
)


# =========================================================
# HEADER
# =========================================================
st.title(
    "🚦 Urban Traffic Signal Digital Twin"
)

st.subheader(
    "Adaptive and Reinforcement Learning-Based Signal Control Using SUMO"
)

st.markdown(
    """
This project develops a **SUMO-based urban traffic signal digital twin**
for a three-intersection corridor and compares four traffic-control strategies:

- 🚦 Fixed-Time Control
- ⚡ Actuated Control
- 🔁 Rule-Based Adaptive Control
- 🤖 PPO Reinforcement Learning Control

The controllers are evaluated using the same traffic demand and network conditions.
"""
)


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title(
    "Navigation"
)

page = st.sidebar.radio(
    "Select section",
    [
        "Project Overview",
        "Controller Comparison",
        "Traffic Performance",
        "Time-Series Analysis",
        "Research Questions",
        "Key Findings",
    ],
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Network Setup"
)

st.sidebar.write(
    "Intersections: **3**"
)

st.sidebar.write(
    "Lanes: **2 per direction**"
)

st.sidebar.write(
    "Simulation demand period: **3600 s**"
)

st.sidebar.write(
    "RL controller: **PPO**"
)


# =========================================================
# PROJECT OVERVIEW
# =========================================================
if page == "Project Overview":

    st.header(
        "Project Overview"
    )

    st.markdown(
        """
### Objective

The objective of this project is to evaluate whether increasingly intelligent
traffic signal control strategies can improve corridor-level traffic performance
under the same traffic demand.

The four controllers are:

**Fixed-Time Control**  
Uses predetermined green and yellow durations.

**Actuated Control**  
Adjusts signal operation according to detected traffic demand.

**Rule-Based Adaptive Control**  
Uses real-time queue measurements through TraCI and dynamically favors the
direction with the larger queue.

**PPO Reinforcement Learning**  
Uses a centralized reinforcement-learning agent to control all three
intersections simultaneously.

---

### Traffic Network

The simulated corridor consists of:

- **3 signalized intersections**
- **2 lanes per direction**
- east-west arterial traffic
- north-south cross-street traffic
- 3600-second traffic demand
- identical demand for all controllers

---

### Analysis Workflow
"""
    )

    st.code(
        """
SUMO Urban Traffic Network
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
Streamlit Dashboard
        """,
        language=None,
    )

    if comparison is not None:

        st.subheader(
            "Final Experiment Size"
        )

        completed = comparison[
            "completed_vehicles"
        ].iloc[0]

        st.metric(
            "Completed Vehicles per Controller",
            f"{int(completed):,}",
        )


# =========================================================
# CONTROLLER COMPARISON
# =========================================================
elif page == "Controller Comparison":

    st.header(
        "Final Controller Comparison"
    )

    if comparison is None:

        st.error(
            "results/controller_comparison.csv was not found."
        )

    else:

        display = comparison.copy()

        st.dataframe(
            display.round(3),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(
            "Select KPI"
        )

        metric_map = {
            "Mean Travel Time (s)":
                "mean_travel_time_s",

            "Mean Waiting Time (s)":
                "mean_waiting_time_s",

            "Mean Time Loss (s)":
                "mean_time_loss_s",

            "Mean Stops per Vehicle":
                "mean_stops_per_vehicle",

            "Mean Trip Speed (km/h)":
                "mean_trip_speed_km_h",

            "Mean Queue (vehicles)":
                "mean_queue_vehicles",

            "Maximum Queue (vehicles)":
                "max_queue_vehicles",

            "Clearance Time (s)":
                "clearance_time_s",
        }

        selected_metric = st.selectbox(
            "Performance indicator",
            list(metric_map.keys()),
        )

        column = metric_map[
            selected_metric
        ]

        chart_data = (
            comparison[
                [
                    "controller",
                    column,
                ]
            ]
            .set_index(
                "controller"
            )
        )

        st.bar_chart(
            chart_data
        )


# =========================================================
# TRAFFIC PERFORMANCE
# =========================================================
elif page == "Traffic Performance":

    st.header(
        "Traffic Performance Results"
    )

    if comparison is None:

        st.error(
            "Final comparison file not found."
        )

    else:

        rl = comparison[
            comparison["controller"].str.contains(
                "PPO",
                case=False,
                na=False,
            )
        ]

        if not rl.empty:

            rl = rl.iloc[0]

            c1, c2, c3, c4 = st.columns(
                4
            )

            c1.metric(
                "PPO Travel Time",
                f"{rl['mean_travel_time_s']:.2f} s",
            )

            c2.metric(
                "PPO Waiting Time",
                f"{rl['mean_waiting_time_s']:.2f} s",
            )

            c3.metric(
                "PPO Mean Speed",
                f"{rl['mean_trip_speed_km_h']:.2f} km/h",
            )

            c4.metric(
                "PPO Mean Queue",
                f"{rl['mean_queue_vehicles']:.2f} veh",
            )

        st.markdown(
            """
### Final results

The PPO reinforcement-learning controller produced the strongest
overall performance across most traffic-efficiency indicators.

It achieved:

- **24.46 s mean travel time**
- **7.26 s mean waiting time**
- **15.58 s mean time loss**
- **17.07 km/h mean trip speed**
- **6.97 vehicles mean queue**
- **19 vehicles maximum queue**

However, Fixed-Time Control produced the lowest number of stops per vehicle.
"""
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            show_image(
                "01_mean_travel_time.png",
                "Mean travel time",
            )

            show_image(
                "03_mean_time_loss.png",
                "Mean time loss",
            )

            show_image(
                "05_mean_trip_speed.png",
                "Mean trip speed",
            )

            show_image(
                "07_max_queue.png",
                "Maximum queue",
            )

        with col2:

            show_image(
                "02_mean_waiting_time.png",
                "Mean waiting time",
            )

            show_image(
                "04_mean_stops.png",
                "Mean stops per vehicle",
            )

            show_image(
                "06_mean_queue.png",
                "Mean network queue",
            )

            show_image(
                "08_clearance_time.png",
                "Network clearance time",
            )


# =========================================================
# TIME SERIES
# =========================================================
elif page == "Time-Series Analysis":

    st.header(
        "Traffic Conditions Over Time"
    )

    available = {}

    if fixed_ts is not None:
        available[
            "Fixed Time"
        ] = fixed_ts

    if actuated_ts is not None:
        available[
            "Actuated"
        ] = actuated_ts

    if adaptive_ts is not None:
        available[
            "Rule-Based Adaptive"
        ] = adaptive_ts

    if rl_ts is not None:
        available[
            "PPO Reinforcement Learning"
        ] = rl_ts

    if not available:

        st.error(
            "No time-series files were found."
        )

    else:

        controllers = st.multiselect(
            "Select controllers",
            list(
                available.keys()
            ),
            default=list(
                available.keys()
            ),
        )

        variable = st.selectbox(
            "Select traffic variable",
            [
                "Mean Speed",
                "Stopped Vehicles",
                "Vehicles in Network",
                "Total Waiting Time",
                "Total Time Loss",
            ],
        )

        variable_map = {
            "Mean Speed":
                "mean_speed_km_h",

            "Stopped Vehicles":
                "stopped_vehicles",

            "Vehicles in Network":
                "vehicles_in_network",

            "Total Waiting Time":
                "total_waiting_time_s",

            "Total Time Loss":
                "total_time_loss_s",
        }

        column = variable_map[
            variable
        ]

        chart_frames = []

        for controller in controllers:

            df = available[
                controller
            ]

            if column not in df.columns:
                continue

            temp = df[
                [
                    "time_s",
                    column,
                ]
            ].copy()

            temp = temp.rename(
                columns={
                    column:
                        controller
                }
            )

            temp = temp.set_index(
                "time_s"
            )

            chart_frames.append(
                temp
            )

        if chart_frames:

            chart = pd.concat(
                chart_frames,
                axis=1,
            )

            st.line_chart(
                chart
            )

        st.subheader(
            "Saved Comparison Figures"
        )

        show_image(
            "09_queue_over_time.png",
            "Queue evolution over time",
        )

        show_image(
            "10_speed_over_time.png",
            "Mean speed over time",
        )


# =========================================================
# RESEARCH QUESTIONS
# =========================================================
elif page == "Research Questions":

    st.header(
        "Research Questions"
    )

    st.markdown(
        """
### RQ1
**How does fixed-time traffic signal control perform under the simulated corridor demand?**

The fixed-time controller provides a stable baseline, but it produces relatively
high average and maximum queues compared with the more responsive controllers.

---

### RQ2
**Does actuated control improve traffic performance relative to fixed-time control?**

**Yes, partially.** Actuated control reduces average waiting time, average queue,
and maximum queue and slightly improves travel time and mean trip speed.

---

### RQ3
**Does rule-based adaptive control further reduce congestion?**

The rule-based adaptive controller reduces queue-related measures, particularly
maximum queue, but increases travel time and the number of stops. This demonstrates
that reducing queues alone does not necessarily optimize total traffic performance.

---

### RQ4
**Can reinforcement learning outperform conventional and rule-based signal control?**

**Yes.** The PPO reinforcement-learning controller achieves the best result for
most major operational indicators, including:

- travel time
- waiting time
- time loss
- mean trip speed
- average queue
- maximum queue

Fixed-Time Control remains best only for the number of stops per vehicle.
"""
    )


# =========================================================
# KEY FINDINGS
# =========================================================
elif page == "Key Findings":

    st.header(
        "Key Findings"
    )

    st.markdown(
        """
### 🤖 PPO RL produced the strongest overall traffic performance

The trained PPO controller achieved:

- **12.2% lower travel time than Actuated Control**
- **23.3% lower waiting time than Actuated Control**
- **16.8% lower time loss than Actuated Control**
- **12.8% higher mean trip speed than Actuated Control**
- **28.8% lower mean queue than Actuated Control**
- **34.5% lower maximum queue than Actuated Control**

### ⚡ Actuated control improved the conventional baseline

Compared with Fixed-Time Control, actuated operation reduced waiting and queue
formation while maintaining similar travel time and speed.

### 🔁 Queue minimization alone is not sufficient

The Rule-Based Adaptive controller reduced queues but increased travel time,
time loss, and stops.

This shows that a traffic controller should balance several competing objectives
rather than optimizing only queue length.

### 🚦 Main conclusion

**Reinforcement learning provided the best overall balance of corridor traffic
performance under the evaluated traffic conditions.**
"""
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "---"
)

st.caption(
    "SUMO-based urban traffic signal digital twin using "
    "Fixed-Time, Actuated, Rule-Based Adaptive, and PPO "
    "Reinforcement Learning control."
)