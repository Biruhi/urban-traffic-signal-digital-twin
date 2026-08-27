import os
import sys
import csv

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if "SUMO_HOME" not in os.environ:
    sys.exit("Please set SUMO_HOME.")

SUMO_TOOLS = os.path.join(
    os.environ["SUMO_HOME"],
    "tools"
)

if SUMO_TOOLS not in sys.path:
    sys.path.append(SUMO_TOOLS)

import traci

from evaluation.kpi_utils import summarize_tripinfo


SUMO_CONFIG = os.path.join(
    "sumo",
    "simulation_actuated.sumocfg"
)

TRIPINFO_FILE = os.path.join(
    "results",
    "actuated_tripinfo.xml"
)

TIMESERIES_FILE = os.path.join(
    "results",
    "actuated_timeseries.csv"
)

SUMMARY_FILE = os.path.join(
    "results",
    "actuated_summary.csv"
)

os.makedirs("results", exist_ok=True)


traci.start(
    [
        "sumo",
        "-c",
        SUMO_CONFIG,
        "--no-step-log",
        "true",
        "--waiting-time-memory",
        "5000",
        "--tripinfo-output",
        TRIPINFO_FILE,
    ]
)


time_series = []

queue_sum = 0
queue_steps = 0
max_queue = 0


while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    sim_time = traci.simulation.getTime()

    vehicle_ids = traci.vehicle.getIDList()

    n_vehicles = len(vehicle_ids)

    total_speed = 0.0
    total_waiting = 0.0
    total_time_loss = 0.0
    stopped_vehicles = 0

    for veh_id in vehicle_ids:

        speed = traci.vehicle.getSpeed(
            veh_id
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
            stopped_vehicles += 1

    mean_speed = (
        total_speed / n_vehicles
        if n_vehicles > 0
        else 0
    )

    queue_sum += stopped_vehicles
    queue_steps += 1

    max_queue = max(
        max_queue,
        stopped_vehicles
    )

    time_series.append(
        [
            sim_time,
            n_vehicles,
            mean_speed * 3.6,
            total_waiting,
            total_time_loss,
            stopped_vehicles,
        ]
    )


traci.close()


with open(
    TIMESERIES_FILE,
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "time_s",
            "vehicles_in_network",
            "mean_speed_km_h",
            "total_waiting_time_s",
            "total_time_loss_s",
            "stopped_vehicles",
        ]
    )

    writer.writerows(time_series)


mean_queue = (
    queue_sum / queue_steps
    if queue_steps > 0
    else 0
)


summary = summarize_tripinfo(
    TRIPINFO_FILE,
    "Actuated",
    SUMMARY_FILE,
    mean_queue,
    max_queue,
)


print()
print("ACTUATED SIMULATION COMPLETED")
print()

for key, value in summary.items():
    print(f"{key}: {value}")