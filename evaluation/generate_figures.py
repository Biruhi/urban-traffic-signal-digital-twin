import os
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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
# LOAD FINAL CONTROLLER SUMMARIES
# =========================================================
summary_files = [
    "fixed_time_summary.csv",
    "actuated_summary.csv",
    "adaptive_summary.csv",
    "rl_v2_summary.csv",
]


frames = []

for filename in summary_files:

    path = os.path.join(
        RESULTS_DIR,
        filename
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Missing summary file: {path}"
        )

    frames.append(
        pd.read_csv(path)
    )


summary = pd.concat(
    frames,
    ignore_index=True
)


# ---------------------------------------------------------
# Save combined comparison table
# ---------------------------------------------------------
comparison_file = os.path.join(
    RESULTS_DIR,
    "controller_comparison.csv"
)

summary.to_csv(
    comparison_file,
    index=False
)


# =========================================================
# BAR PLOT HELPER
# =========================================================
def make_bar(
    column,
    ylabel,
    title,
    filename,
):

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        summary["controller"],
        summary[column]
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        title
    )

    plt.xticks(
        rotation=15,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            filename
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# =========================================================
# FINAL KPI FIGURES
# =========================================================

make_bar(
    "mean_travel_time_s",
    "Mean Travel Time (s)",
    "Mean Travel Time by Controller",
    "01_mean_travel_time.png",
)

make_bar(
    "mean_waiting_time_s",
    "Mean Waiting Time (s)",
    "Mean Waiting Time by Controller",
    "02_mean_waiting_time.png",
)

make_bar(
    "mean_time_loss_s",
    "Mean Time Loss (s)",
    "Mean Time Loss by Controller",
    "03_mean_time_loss.png",
)

make_bar(
    "mean_stops_per_vehicle",
    "Stops per Vehicle",
    "Mean Stops per Vehicle",
    "04_mean_stops.png",
)

make_bar(
    "mean_trip_speed_km_h",
    "Mean Trip Speed (km/h)",
    "Mean Trip Speed by Controller",
    "05_mean_trip_speed.png",
)

make_bar(
    "mean_queue_vehicles",
    "Stopped Vehicles",
    "Mean Network Queue",
    "06_mean_queue.png",
)

make_bar(
    "max_queue_vehicles",
    "Stopped Vehicles",
    "Maximum Network Queue",
    "07_max_queue.png",
)

make_bar(
    "clearance_time_s",
    "Simulation Time (s)",
    "Network Clearance Time",
    "08_clearance_time.png",
)


# =========================================================
# TIME-SERIES COMPARISON
# =========================================================

timeseries_files = {
    "Fixed Time":
        "fixed_time_timeseries.csv",

    "Actuated":
        "actuated_timeseries.csv",

    "Rule-Based Adaptive":
        "adaptive_timeseries.csv",

    "PPO RL":
        "rl_v2_timeseries.csv",
}


# ---------------------------------------------------------
# Queue evolution
# ---------------------------------------------------------
plt.figure(
    figsize=(11, 5)
)

for controller, filename in (
    timeseries_files.items()
):

    path = os.path.join(
        RESULTS_DIR,
        filename
    )

    if not os.path.exists(path):
        continue

    df = pd.read_csv(
        path
    )

    plt.plot(
        df["time_s"],
        df["stopped_vehicles"],
        label=controller,
        alpha=0.8
    )


plt.xlabel(
    "Simulation Time (s)"
)

plt.ylabel(
    "Stopped Vehicles"
)

plt.title(
    "Network Queue Evolution"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "09_queue_over_time.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ---------------------------------------------------------
# Mean speed evolution
# ---------------------------------------------------------
plt.figure(
    figsize=(11, 5)
)

for controller, filename in (
    timeseries_files.items()
):

    path = os.path.join(
        RESULTS_DIR,
        filename
    )

    if not os.path.exists(path):
        continue

    df = pd.read_csv(
        path
    )

    plt.plot(
        df["time_s"],
        df["mean_speed_km_h"],
        label=controller,
        alpha=0.8
    )


plt.xlabel(
    "Simulation Time (s)"
)

plt.ylabel(
    "Mean Speed (km/h)"
)

plt.title(
    "Network Mean Speed Over Time"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "10_speed_over_time.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print()
print("FINAL CONTROLLER COMPARISON CREATED")
print()
print(
    f"Comparison table: "
    f"{comparison_file}"
)
print(
    f"Figures directory: "
    f"{FIGURES_DIR}"
)