import os
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

FIGURES_DIR = os.path.join(
    PROJECT_ROOT,
    "figures"
)

os.makedirs(
    FIGURES_DIR,
    exist_ok=True
)


# =========================================================
# INPUT FILES
# =========================================================

SUMMARY_FILES = [
    os.path.join(
        RESULTS_DIR,
        "fixed_time_summary.csv"
    ),
    os.path.join(
        RESULTS_DIR,
        "actuated_summary.csv"
    ),
    os.path.join(
        RESULTS_DIR,
        "adaptive_summary.csv"
    ),
    os.path.join(
        RESULTS_DIR,
        "rl_v2_summary.csv"
    ),
]

TIMESERIES_FILES = {
    "Fixed-Time Control": os.path.join(
        RESULTS_DIR,
        "fixed_time_timeseries.csv"
    ),

    "Actuated Control": os.path.join(
        RESULTS_DIR,
        "actuated_timeseries.csv"
    ),

    "Rule-Based Adaptive": os.path.join(
        RESULTS_DIR,
        "adaptive_timeseries.csv"
    ),

    "PPO Reinforcement Learning": os.path.join(
        RESULTS_DIR,
        "rl_v2_timeseries.csv"
    ),
}


# =========================================================
# CHECK REQUIRED FILES
# =========================================================

for file_path in SUMMARY_FILES:

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Missing summary file:\n{file_path}"
        )


for controller, file_path in TIMESERIES_FILES.items():

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Missing time-series file for "
            f"{controller}:\n{file_path}"
        )


# =========================================================
# LOAD SUMMARY RESULTS
# =========================================================

summary_frames = []

for file_path in SUMMARY_FILES:

    df = pd.read_csv(
        file_path
    )

    summary_frames.append(
        df
    )


comparison = pd.concat(
    summary_frames,
    ignore_index=True
)


# =========================================================
# SAVE COMBINED COMPARISON TABLE
# =========================================================

COMPARISON_FILE = os.path.join(
    RESULTS_DIR,
    "controller_comparison.csv"
)

comparison.to_csv(
    COMPARISON_FILE,
    index=False
)


# =========================================================
# CONTROLLER ORDER
# =========================================================

controller_order = [
    "Fixed-Time Control",
    "Actuated Control",
    "Rule-Based Adaptive",
    "PPO Reinforcement Learning",
]


comparison["controller"] = pd.Categorical(
    comparison["controller"],
    categories=controller_order,
    ordered=True
)

comparison = comparison.sort_values(
    "controller"
).reset_index(
    drop=True
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def save_bar_chart(
    dataframe,
    column,
    ylabel,
    title,
    output_name
):

    plt.figure(
        figsize=(9, 6)
    )

    plt.bar(
        dataframe["controller"],
        dataframe[column]
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        title
    )

    plt.xticks(
        rotation=20,
        ha="right"
    )

    plt.tight_layout()

    output_path = os.path.join(
        FIGURES_DIR,
        output_name
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_path}"
    )


# =========================================================
# BAR CHARTS
# =========================================================

save_bar_chart(
    comparison,
    "mean_travel_time_s",
    "Mean Travel Time (s)",
    "Mean Travel Time by Controller",
    "01_mean_travel_time.png"
)


save_bar_chart(
    comparison,
    "mean_waiting_time_s",
    "Mean Waiting Time (s)",
    "Mean Waiting Time by Controller",
    "02_mean_waiting_time.png"
)


save_bar_chart(
    comparison,
    "mean_time_loss_s",
    "Mean Time Loss (s)",
    "Mean Time Loss by Controller",
    "03_mean_time_loss.png"
)


save_bar_chart(
    comparison,
    "mean_stops_per_vehicle",
    "Mean Stops per Vehicle",
    "Mean Stops per Vehicle by Controller",
    "04_mean_stops.png"
)


save_bar_chart(
    comparison,
    "mean_trip_speed_km_h",
    "Mean Trip Speed (km/h)",
    "Mean Trip Speed by Controller",
    "05_mean_trip_speed.png"
)


save_bar_chart(
    comparison,
    "mean_queue_vehicles",
    "Mean Queue (vehicles)",
    "Mean Queue by Controller",
    "06_mean_queue.png"
)


save_bar_chart(
    comparison,
    "max_queue_vehicles",
    "Maximum Queue (vehicles)",
    "Maximum Queue by Controller",
    "07_max_queue.png"
)


save_bar_chart(
    comparison,
    "clearance_time_s",
    "Clearance Time (s)",
    "Network Clearance Time by Controller",
    "08_clearance_time.png"
)


# =========================================================
# QUEUE OVER TIME
# =========================================================

plt.figure(
    figsize=(10, 6)
)

for controller, file_path in TIMESERIES_FILES.items():

    df = pd.read_csv(
        file_path
    )

    plt.plot(
        df["time_s"],
        df["stopped_vehicles"],
        label=controller
    )


plt.xlabel(
    "Simulation Time (s)"
)

plt.ylabel(
    "Stopped Vehicles"
)

plt.title(
    "Queue Evolution Over Time"
)

plt.legend()

plt.tight_layout()

QUEUE_FIGURE = os.path.join(
    FIGURES_DIR,
    "09_queue_over_time.png"
)

plt.savefig(
    QUEUE_FIGURE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {QUEUE_FIGURE}"
)


# =========================================================
# SPEED OVER TIME
# =========================================================

plt.figure(
    figsize=(10, 6)
)

for controller, file_path in TIMESERIES_FILES.items():

    df = pd.read_csv(
        file_path
    )

    plt.plot(
        df["time_s"],
        df["mean_speed_km_h"],
        label=controller
    )


plt.xlabel(
    "Simulation Time (s)"
)

plt.ylabel(
    "Mean Speed (km/h)"
)

plt.title(
    "Mean Network Speed Over Time"
)

plt.legend()

plt.tight_layout()

SPEED_FIGURE = os.path.join(
    FIGURES_DIR,
    "10_speed_over_time.png"
)

plt.savefig(
    SPEED_FIGURE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {SPEED_FIGURE}"
)


# =========================================================
# FINISHED
# =========================================================

print()
print("=" * 60)
print("FIGURE GENERATION COMPLETED")
print("=" * 60)

print(
    f"\nController comparison saved to:\n"
    f"{COMPARISON_FILE}"
)

print(
    f"\nFigures saved to:\n"
    f"{FIGURES_DIR}"
)