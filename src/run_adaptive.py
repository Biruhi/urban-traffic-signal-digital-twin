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

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
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

from kpi_utils import summarize_tripinfo


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

SUMO_CONFIG = os.path.join(
    PROJECT_ROOT,
    "sumo",
    "simulation.sumocfg"
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

TRIPINFO_FILE = os.path.join(
    RESULTS_DIR,
    "adaptive_tripinfo.xml"
)

TIMESERIES_FILE = os.path.join(
    RESULTS_DIR,
    "adaptive_timeseries.csv"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "adaptive_summary.csv"
)


TLS_IDS = [
    "J1",
    "J2",
    "J3",
]


MIN_GREEN = 10
MAX_GREEN = 45

EW_GREEN = 0
EW_YELLOW = 1
NS_GREEN = 2
NS_YELLOW = 3


os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def get_incoming_lanes(tls_id):

    controlled_links = (
        traci.trafficlight.getControlledLinks(
            tls_id
        )
    )

    lanes = set()

    for group in controlled_links:

        for connection in group:

            if connection:
                lanes.add(
                    connection[0]
                )

    return list(lanes)


def classify_lanes(tls_id):

    ew_lanes = []
    ns_lanes = []

    for lane_id in get_incoming_lanes(
        tls_id
    ):

        shape = traci.lane.getShape(
            lane_id
        )

        if len(shape) < 2:
            continue

        x1, y1 = shape[0]
        x2, y2 = shape[-1]

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx >= dy:
            ew_lanes.append(
                lane_id
            )
        else:
            ns_lanes.append(
                lane_id
            )

    return ew_lanes, ns_lanes


def count_queue(lane_ids):

    queue = 0

    for lane_id in lane_ids:

        vehicle_ids = (
            traci.lane.getLastStepVehicleIDs(
                lane_id
            )
        )

        for veh_id in vehicle_ids:

            if (
                traci.vehicle.getSpeed(
                    veh_id
                )
                < 0.1
            ):
                queue += 1

    return queue


# ---------------------------------------------------------
# Start SUMO
# ---------------------------------------------------------

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


lane_groups = {}

for tls_id in TLS_IDS:

    ew, ns = classify_lanes(
        tls_id
    )

    lane_groups[tls_id] = {
        "EW": ew,
        "NS": ns,
    }


phase_start_time = {
    tls_id: 0.0
    for tls_id in TLS_IDS
}


time_series = []

queue_sum = 0
queue_steps = 0
max_queue = 0


# ---------------------------------------------------------
# Simulation
# ---------------------------------------------------------

while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    sim_time = (
        traci.simulation.getTime()
    )

    # -----------------------------------------------------
    # Adaptive signal controller
    # -----------------------------------------------------

    for tls_id in TLS_IDS:

        phase = (
            traci.trafficlight.getPhase(
                tls_id
            )
        )

        ew_queue = count_queue(
            lane_groups[tls_id]["EW"]
        )

        ns_queue = count_queue(
            lane_groups[tls_id]["NS"]
        )

        elapsed = (
            sim_time
            - phase_start_time[tls_id]
        )

        if phase == EW_GREEN:

            if elapsed >= MAX_GREEN:

                traci.trafficlight.setPhase(
                    tls_id,
                    EW_YELLOW
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

            elif (
                elapsed >= MIN_GREEN
                and ns_queue > ew_queue
            ):

                traci.trafficlight.setPhase(
                    tls_id,
                    EW_YELLOW
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

        elif phase == EW_YELLOW:

            if elapsed >= 3:

                traci.trafficlight.setPhase(
                    tls_id,
                    NS_GREEN
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

        elif phase == NS_GREEN:

            if elapsed >= MAX_GREEN:

                traci.trafficlight.setPhase(
                    tls_id,
                    NS_YELLOW
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

            elif (
                elapsed >= MIN_GREEN
                and ew_queue > ns_queue
            ):

                traci.trafficlight.setPhase(
                    tls_id,
                    NS_YELLOW
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

        elif phase == NS_YELLOW:

            if elapsed >= 3:

                traci.trafficlight.setPhase(
                    tls_id,
                    EW_GREEN
                )

                phase_start_time[tls_id] = (
                    sim_time
                )

    # -----------------------------------------------------
    # Network performance
    # -----------------------------------------------------

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
        else 0
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
        ]
    )


traci.close()


# ---------------------------------------------------------
# Save time series
# ---------------------------------------------------------

with open(
    TIMESERIES_FILE,
    "w",
    newline=""
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
        ]
    )

    writer.writerows(
        time_series
    )


mean_queue = (
    queue_sum / queue_steps
    if queue_steps > 0
    else 0
)


summary = summarize_tripinfo(
    TRIPINFO_FILE,
    "Rule-Based Adaptive",
    SUMMARY_FILE,
    mean_queue,
    max_queue,
)


print()
print(
    "RULE-BASED ADAPTIVE SIMULATION COMPLETED"
)
print()

for key, value in summary.items():
    print(
        f"{key}: {value}"
    )