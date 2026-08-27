import os
import sys
import csv


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SRC_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if SRC_DIR not in sys.path:
    sys.path.insert(
        0,
        SRC_DIR
    )


# ---------------------------------------------------------
# SUMO setup
# ---------------------------------------------------------

if "SUMO_HOME" not in os.environ:
    sys.exit(
        "Please set SUMO_HOME."
    )


SUMO_TOOLS = os.path.join(
    os.environ["SUMO_HOME"],
    "tools"
)

if SUMO_TOOLS not in sys.path:
    sys.path.append(
        SUMO_TOOLS
    )


import traci

from stable_baselines3 import PPO
from traffic_signal_env import TrafficSignalEnv
from kpi_utils import summarize_tripinfo


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "ppo_traffic_signal_v2"
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

TRIPINFO_FILE = os.path.join(
    RESULTS_DIR,
    "rl_v2_tripinfo.xml"
)

TIMESERIES_FILE = os.path.join(
    RESULTS_DIR,
    "rl_v2_timeseries.csv"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "rl_v2_summary.csv"
)

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

env = TrafficSignalEnv(
    max_simulation_time=6000,
    decision_interval=5,
    min_green=10,
    yellow_time=3,
    tripinfo_output=TRIPINFO_FILE,
)


# ---------------------------------------------------------
# Load trained PPO model
# ---------------------------------------------------------

model = PPO.load(
    MODEL_PATH
)


observation, info = env.reset()


# ---------------------------------------------------------
# KPI storage
# ---------------------------------------------------------

time_series = []

queue_sum = 0
queue_steps = 0
max_queue = 0

done = False


# ---------------------------------------------------------
# Run PPO controller
# ---------------------------------------------------------

while not done:

    action, _ = model.predict(
        observation,
        deterministic=True
    )

    observation, reward, terminated, truncated, info = (
        env.step(
            action
        )
    )

    sim_time = (
        traci.simulation.getTime()
    )

    vehicle_ids = (
        traci.vehicle.getIDList()
    )

    n_vehicles = len(
        vehicle_ids
    )

    total_speed = 0.0
    total_waiting = 0.0
    total_time_loss = 0.0
    stopped = 0

    for veh_id in vehicle_ids:

        speed = (
            traci.vehicle.getSpeed(
                veh_id
            )
        )

        total_speed += speed

        total_waiting += (
            traci.vehicle.getWaitingTime(
                veh_id
            )
        )

        total_time_loss += (
            traci.vehicle.getTimeLoss(
                veh_id
            )
        )

        if speed < 0.1:
            stopped += 1

    mean_speed = (
        total_speed / n_vehicles
        if n_vehicles > 0
        else 0.0
    )

    queue_sum += stopped
    queue_steps += 1

    max_queue = max(
        max_queue,
        stopped
    )

    time_series.append(
        [
            sim_time,
            n_vehicles,
            mean_speed * 3.6,
            total_waiting,
            total_time_loss,
            stopped,
            reward,
            int(action[0]),
            int(action[1]),
            int(action[2]),
        ]
    )

    remaining = (
        traci.simulation.getMinExpectedNumber()
    )

    if remaining <= 0:
        done = True

    elif sim_time >= 6000:

        print(
            "WARNING: RL evaluation reached "
            "the 6000 s safety limit."
        )

        done = True


# ---------------------------------------------------------
# Close environment
# ---------------------------------------------------------

env.close()


# ---------------------------------------------------------
# Save time series
# ---------------------------------------------------------

with open(
    TIMESERIES_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(
        f
    )

    writer.writerow(
        [
            "time_s",
            "vehicles_in_network",
            "mean_speed_km_h",
            "total_waiting_time_s",
            "total_time_loss_s",
            "stopped_vehicles",
            "reward",
            "action_J1",
            "action_J2",
            "action_J3",
        ]
    )

    writer.writerows(
        time_series
    )


# ---------------------------------------------------------
# Queue summary
# ---------------------------------------------------------

mean_queue = (
    queue_sum / queue_steps
    if queue_steps > 0
    else 0.0
)


# ---------------------------------------------------------
# Exact SUMO TripInfo summary
# ---------------------------------------------------------

summary = summarize_tripinfo(
    TRIPINFO_FILE,
    "PPO Reinforcement Learning",
    SUMMARY_FILE,
    mean_queue,
    max_queue,
)


# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------

print()
print(
    "PPO RL EVALUATION COMPLETED"
)
print()

for key, value in summary.items():

    print(
        f"{key}: {value}"
    )