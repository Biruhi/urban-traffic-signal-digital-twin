import os
import csv
import traci

from kpi_utils import summarize_tripinfo


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SUMO_CONFIG = os.path.join(
    PROJECT_ROOT,
    "sumo",
    "simulation_actuated.sumocfg"
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)

TRIPINFO_FILE = os.path.join(
    RESULTS_DIR,
    "actuated_tripinfo.xml"
)

TIMESERIES_FILE = os.path.join(
    RESULTS_DIR,
    "actuated_timeseries.csv"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "actuated_summary.csv"
)


# --------------------------------------------------
# SUMO BINARY
# --------------------------------------------------

SUMO_BINARY = "sumo"


# --------------------------------------------------
# START SIMULATION
# --------------------------------------------------

sumo_command = [
    SUMO_BINARY,
    "-c",
    SUMO_CONFIG,
    "--tripinfo-output",
    TRIPINFO_FILE,
    "--no-step-log",
    "true"
]

print("\nStarting Actuated Control simulation...")

traci.start(sumo_command)


# --------------------------------------------------
# SIMULATION
# --------------------------------------------------

time_series = []

max_queue = 0
queue_sum = 0
queue_samples = 0

while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    simulation_time = traci.simulation.getTime()

    vehicle_ids = traci.vehicle.getIDList()

    total_speed = 0.0
    total_waiting = 0.0
    total_time_loss = 0.0
    stopped_vehicles = 0

    for vehicle_id in vehicle_ids:

        speed = traci.vehicle.getSpeed(vehicle_id)

        total_speed += speed

        total_waiting += traci.vehicle.getWaitingTime(
            vehicle_id
        )

        total_time_loss += traci.vehicle.getTimeLoss(
            vehicle_id
        )

        if speed < 0.1:
            stopped_vehicles += 1

    number_of_vehicles = len(vehicle_ids)

    if number_of_vehicles > 0:

        mean_speed_m_s = (
            total_speed / number_of_vehicles
        )

        mean_speed_km_h = (
            mean_speed_m_s * 3.6
        )

        mean_waiting = (
            total_waiting / number_of_vehicles
        )

        mean_time_loss = (
            total_time_loss / number_of_vehicles
        )

    else:

        mean_speed_km_h = 0.0
        mean_waiting = 0.0
        mean_time_loss = 0.0

    current_queue = stopped_vehicles

    queue_sum += current_queue
    queue_samples += 1

    if current_queue > max_queue:
        max_queue = current_queue

    time_series.append(
        {
            "time_s": simulation_time,
            "vehicles_in_network": number_of_vehicles,
            "mean_speed_km_h": mean_speed_km_h,
            "mean_waiting_time_s": mean_waiting,
            "mean_time_loss_s": mean_time_loss,
            "stopped_vehicles": stopped_vehicles
        }
    )


# --------------------------------------------------
# CLOSE SUMO
# --------------------------------------------------

traci.close()


# --------------------------------------------------
# SAVE TIME SERIES
# --------------------------------------------------

with open(
    TIMESERIES_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "time_s",
        "vehicles_in_network",
        "mean_speed_km_h",
        "mean_waiting_time_s",
        "mean_time_loss_s",
        "stopped_vehicles"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(time_series)


# --------------------------------------------------
# QUEUE SUMMARY
# --------------------------------------------------

if queue_samples > 0:
    mean_queue = queue_sum / queue_samples
else:
    mean_queue = 0.0


# --------------------------------------------------
# TRIPINFO SUMMARY
# --------------------------------------------------

summary = summarize_tripinfo(
    tripinfo_file=TRIPINFO_FILE,
    controller_name="Actuated Control",
    output_csv=SUMMARY_FILE,
    mean_queue=mean_queue,
    max_queue=max_queue
)


# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print("\n" + "=" * 60)
print("ACTUATED CONTROL COMPLETED")
print("=" * 60)

print(
    f"Completed vehicles: "
    f"{summary['completed_vehicles']}"
)

print(
    f"Mean travel time: "
    f"{summary['mean_travel_time_s']:.3f} s"
)

print(
    f"Mean waiting time: "
    f"{summary['mean_waiting_time_s']:.3f} s"
)

print(
    f"Mean time loss: "
    f"{summary['mean_time_loss_s']:.3f} s"
)

print(
    f"Mean stops/vehicle: "
    f"{summary['mean_stops_per_vehicle']:.3f}"
)

print(
    f"Mean trip speed: "
    f"{summary['mean_trip_speed_km_h']:.3f} km/h"
)

print(
    f"Mean queue: "
    f"{summary['mean_queue_vehicles']:.3f}"
)

print(
    f"Maximum queue: "
    f"{summary['max_queue_vehicles']}"
)

print(
    f"Clearance time: "
    f"{summary['clearance_time_s']:.1f} s"
)

print("\nSaved:")
print(TIMESERIES_FILE)
print(SUMMARY_FILE)
print(TRIPINFO_FILE)