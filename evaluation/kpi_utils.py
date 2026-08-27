import os
import csv
import xml.etree.ElementTree as ET


def summarize_tripinfo(
    tripinfo_file,
    controller_name,
    output_csv,
    mean_queue,
    max_queue,
):
    """
    Read SUMO tripinfo XML and calculate exact
    per-vehicle performance indicators.
    """

    tree = ET.parse(tripinfo_file)
    root = tree.getroot()

    records = []

    for trip in root.findall("tripinfo"):

        records.append(
            {
                "id": trip.get("id"),
                "depart": float(trip.get("depart", 0)),
                "arrival": float(trip.get("arrival", 0)),
                "duration": float(trip.get("duration", 0)),
                "waitingTime": float(
                    trip.get("waitingTime", 0)
                ),
                "timeLoss": float(
                    trip.get("timeLoss", 0)
                ),
                "waitingCount": int(
                    trip.get("waitingCount", 0)
                ),
                "routeLength": float(
                    trip.get("routeLength", 0)
                ),
            }
        )

    n = len(records)

    if n == 0:
        raise RuntimeError(
            f"No completed trips found in {tripinfo_file}"
        )

    mean_travel_time = (
        sum(r["duration"] for r in records) / n
    )

    mean_waiting_time = (
        sum(r["waitingTime"] for r in records) / n
    )

    mean_time_loss = (
        sum(r["timeLoss"] for r in records) / n
    )

    mean_stops = (
        sum(r["waitingCount"] for r in records) / n
    )

    total_distance_km = (
        sum(r["routeLength"] for r in records)
        / 1000
    )

    total_travel_hours = (
        sum(r["duration"] for r in records)
        / 3600
    )

    mean_trip_speed = (
        total_distance_km / total_travel_hours
        if total_travel_hours > 0
        else 0
    )

    clearance_time = max(
        r["arrival"] for r in records
    )

    summary = {
        "controller": controller_name,
        "completed_vehicles": n,
        "mean_travel_time_s": round(
            mean_travel_time, 3
        ),
        "mean_waiting_time_s": round(
            mean_waiting_time, 3
        ),
        "mean_time_loss_s": round(
            mean_time_loss, 3
        ),
        "mean_stops_per_vehicle": round(
            mean_stops, 3
        ),
        "mean_trip_speed_km_h": round(
            mean_trip_speed, 3
        ),
        "mean_queue_vehicles": round(
            mean_queue, 3
        ),
        "max_queue_vehicles": max_queue,
        "clearance_time_s": round(
            clearance_time, 3
        ),
    }

    os.makedirs(
        os.path.dirname(output_csv),
        exist_ok=True
    )

    with open(
        output_csv,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=summary.keys()
        )

        writer.writeheader()
        writer.writerow(summary)

    return summary