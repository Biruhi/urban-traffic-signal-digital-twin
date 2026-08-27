import os
import sys

import gymnasium as gym
import numpy as np
from gymnasium import spaces


# =========================================================
# PROJECT ROOT
# =========================================================
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# =========================================================
# SUMO / TraCI SETUP
# =========================================================
if "SUMO_HOME" not in os.environ:
    raise EnvironmentError(
        "SUMO_HOME is not set. Please configure SUMO_HOME first."
    )

SUMO_TOOLS = os.path.join(
    os.environ["SUMO_HOME"],
    "tools"
)

if SUMO_TOOLS not in sys.path:
    sys.path.append(SUMO_TOOLS)

import traci


# =========================================================
# RL TRAFFIC SIGNAL ENVIRONMENT
# =========================================================
class TrafficSignalEnv(gym.Env):
    """
    Centralized reinforcement-learning environment for
    three signalized intersections:

        J1
        J2
        J3

    ACTIONS
    -------
    For each intersection:

        0 = request East-West green
        1 = request North-South green

    Therefore:

        action = [J1, J2, J3]

    Example:

        [0, 1, 0]

    means:

        J1 -> East-West
        J2 -> North-South
        J3 -> East-West


    OBSERVATIONS
    ------------
    For each intersection:

        1. normalized East-West queue
        2. normalized North-South queue
        3. current signal direction

    Three intersections × three variables = 9 observations.
    """

    metadata = {
        "render_modes": []
    }

    # =====================================================
    # INITIALIZATION
    # =====================================================
    def __init__(
        self,
        sumo_config=os.path.join(
            PROJECT_ROOT,
            "sumo",
            "simulation.sumocfg"
        ),
        max_simulation_time=4500,
        decision_interval=5,
        min_green=10,
        yellow_time=3,
        tripinfo_output=None,
    ):
        super().__init__()

        # -------------------------------------------------
        # Configuration
        # -------------------------------------------------
        self.sumo_config = sumo_config

        self.max_simulation_time = (
            max_simulation_time
        )

        self.decision_interval = (
            decision_interval
        )

        self.min_green = min_green

        self.yellow_time = yellow_time

        self.tripinfo_output = (
            tripinfo_output
        )

        # -------------------------------------------------
        # Traffic lights
        # -------------------------------------------------
        self.tls_ids = [
            "J1",
            "J2",
            "J3",
        ]

        # -------------------------------------------------
        # Signal phases
        #
        # Phase 0 = East-West green
        # Phase 1 = East-West yellow
        # Phase 2 = North-South green
        # Phase 3 = North-South yellow
        # -------------------------------------------------
        self.EW_GREEN = 0
        self.EW_YELLOW = 1

        self.NS_GREEN = 2
        self.NS_YELLOW = 3

        # -------------------------------------------------
        # ACTION SPACE
        # -------------------------------------------------
        self.action_space = (
            spaces.MultiDiscrete(
                [2, 2, 2]
            )
        )

        # -------------------------------------------------
        # OBSERVATION SPACE
        # -------------------------------------------------
        self.observation_space = (
            spaces.Box(
                low=0.0,
                high=1.0,
                shape=(9,),
                dtype=np.float32,
            )
        )

        # -------------------------------------------------
        # Runtime storage
        # -------------------------------------------------
        self.lane_groups = {}

        self.last_green_change = {
            tls_id: 0.0
            for tls_id in self.tls_ids
        }

        self.running = False

    # =====================================================
    # START SUMO
    # =====================================================
    def _start_sumo(self):

        if self.running:

            try:
                traci.close()

            except Exception:
                pass

        sumo_cmd = [
            "sumo",
            "-c",
            self.sumo_config,
            "--no-step-log",
            "true",
            "--no-warnings",
            "true",
            "--waiting-time-memory",
            "5000",
        ]

        if self.tripinfo_output is not None:

            sumo_cmd.extend(
                [
                    "--tripinfo-output",
                    self.tripinfo_output,
                ]
            )

        traci.start(
            sumo_cmd
        )

        self.running = True

        # -------------------------------------------------
        # Automatically identify EW and NS lanes
        # -------------------------------------------------
        self.lane_groups = {}

        for tls_id in self.tls_ids:

            ew_lanes, ns_lanes = (
                self._classify_lanes(
                    tls_id
                )
            )

            self.lane_groups[tls_id] = {
                "EW": ew_lanes,
                "NS": ns_lanes,
            }

        # -------------------------------------------------
        # Initialize signal timing
        # -------------------------------------------------
        current_time = (
            traci.simulation.getTime()
        )

        self.last_green_change = {
            tls_id: current_time
            for tls_id in self.tls_ids
        }

    # =====================================================
    # GET INCOMING LANES
    # =====================================================
    def _get_incoming_lanes(
        self,
        tls_id
    ):

        controlled_links = (
            traci.trafficlight
            .getControlledLinks(
                tls_id
            )
        )

        lanes = set()

        for group in controlled_links:

            for connection in group:

                if connection:

                    incoming_lane = (
                        connection[0]
                    )

                    lanes.add(
                        incoming_lane
                    )

        return list(lanes)

    # =====================================================
    # CLASSIFY LANES
    # =====================================================
    def _classify_lanes(
        self,
        tls_id
    ):
        """
        Classifies incoming lanes as:

            East-West
            North-South

        based on lane geometry.
        """

        lanes = (
            self._get_incoming_lanes(
                tls_id
            )
        )

        ew_lanes = []
        ns_lanes = []

        for lane_id in lanes:

            shape = (
                traci.lane.getShape(
                    lane_id
                )
            )

            if len(shape) < 2:
                continue

            x1, y1 = shape[0]
            x2, y2 = shape[-1]

            dx = abs(
                x2 - x1
            )

            dy = abs(
                y2 - y1
            )

            if dx >= dy:

                ew_lanes.append(
                    lane_id
                )

            else:

                ns_lanes.append(
                    lane_id
                )

        return (
            ew_lanes,
            ns_lanes
        )

    # =====================================================
    # QUEUE LENGTH
    # =====================================================
    def _queue(
        self,
        lane_ids
    ):
        """
        Counts stopped vehicles on selected lanes.

        Vehicle considered queued if:

            speed < 0.1 m/s
        """

        queue_count = 0

        for lane_id in lane_ids:

            vehicle_ids = (
                traci.lane
                .getLastStepVehicleIDs(
                    lane_id
                )
            )

            for veh_id in vehicle_ids:

                speed = (
                    traci.vehicle.getSpeed(
                        veh_id
                    )
                )

                if speed < 0.1:

                    queue_count += 1

        return queue_count

    # =====================================================
    # TOTAL WAITING TIME
    # =====================================================
    def _total_waiting_time(
        self
    ):

        total_waiting = 0.0

        for veh_id in (
            traci.vehicle.getIDList()
        ):

            total_waiting += (
                traci.vehicle
                .getWaitingTime(
                    veh_id
                )
            )

        return total_waiting

    # =====================================================
    # OBSERVATION
    # =====================================================
    def _get_observation(
        self
    ):

        observations = []

        queue_scale = 30.0

        for tls_id in self.tls_ids:

            ew_queue = self._queue(
                self.lane_groups[
                    tls_id
                ]["EW"]
            )

            ns_queue = self._queue(
                self.lane_groups[
                    tls_id
                ]["NS"]
            )

            phase = (
                traci.trafficlight
                .getPhase(
                    tls_id
                )
            )

            if phase in [
                self.EW_GREEN,
                self.EW_YELLOW,
            ]:

                direction = 0.0

            else:

                direction = 1.0

            normalized_ew = min(
                ew_queue
                / queue_scale,
                1.0,
            )

            normalized_ns = min(
                ns_queue
                / queue_scale,
                1.0,
            )

            observations.extend(
                [
                    normalized_ew,
                    normalized_ns,
                    direction,
                ]
            )

        return np.array(
            observations,
            dtype=np.float32,
        )

    # =====================================================
    # APPLY RL ACTIONS
    # =====================================================
    def _apply_actions(
        self,
        actions
    ):

        current_time = (
            traci.simulation.getTime()
        )

        switching = {}

        for i, tls_id in enumerate(
            self.tls_ids
        ):

            requested_direction = int(
                actions[i]
            )

            current_phase = (
                traci.trafficlight
                .getPhase(
                    tls_id
                )
            )

            if current_phase in [
                self.EW_GREEN,
                self.EW_YELLOW,
            ]:

                current_direction = 0

            else:

                current_direction = 1

            green_elapsed = (
                current_time
                - self.last_green_change[
                    tls_id
                ]
            )

            can_switch = (
                green_elapsed
                >= self.min_green
            )

            should_switch = (
                requested_direction
                != current_direction
                and can_switch
            )

            switching[tls_id] = (
                should_switch,
                requested_direction,
            )

        # -------------------------------------------------
        # Begin yellow transitions
        # -------------------------------------------------
        any_switch = False

        for tls_id, (
            should_switch,
            requested_direction,
        ) in switching.items():

            if not should_switch:
                continue

            any_switch = True

            current_phase = (
                traci.trafficlight
                .getPhase(
                    tls_id
                )
            )

            if (
                current_phase
                == self.EW_GREEN
            ):

                traci.trafficlight.setPhase(
                    tls_id,
                    self.EW_YELLOW,
                )

            elif (
                current_phase
                == self.NS_GREEN
            ):

                traci.trafficlight.setPhase(
                    tls_id,
                    self.NS_YELLOW,
                )

        # -------------------------------------------------
        # Simulate yellow interval
        # -------------------------------------------------
        simulated_seconds = 0

        if any_switch:

            for _ in range(
                self.yellow_time
            ):

                if (
                    traci.simulation
                    .getMinExpectedNumber()
                    <= 0
                ):
                    break

                traci.simulationStep()

                simulated_seconds += 1

        # -------------------------------------------------
        # Activate requested greens
        # -------------------------------------------------
        new_time = (
            traci.simulation.getTime()
        )

        for tls_id, (
            should_switch,
            requested_direction,
        ) in switching.items():

            if not should_switch:
                continue

            if requested_direction == 0:

                traci.trafficlight.setPhase(
                    tls_id,
                    self.EW_GREEN,
                )

            else:

                traci.trafficlight.setPhase(
                    tls_id,
                    self.NS_GREEN,
                )

            self.last_green_change[
                tls_id
            ] = new_time

        # -------------------------------------------------
        # Complete remaining decision interval
        # -------------------------------------------------
        remaining = max(
            0,
            self.decision_interval
            - simulated_seconds,
        )

        for _ in range(
            remaining
        ):

            if (
                traci.simulation
                .getMinExpectedNumber()
                <= 0
            ):
                break

            traci.simulationStep()

    # =====================================================
    # REWARD FUNCTION
    # =====================================================
    def _calculate_reward(
        self
    ):
        """
        PPO is rewarded for reducing:

            1. queue length
            2. waiting time
            3. vehicle accumulation

        Larger congestion produces a more negative reward.
        """

        total_queue = 0

        for tls_id in self.tls_ids:

            total_queue += self._queue(
                self.lane_groups[
                    tls_id
                ]["EW"]
            )

            total_queue += self._queue(
                self.lane_groups[
                    tls_id
                ]["NS"]
            )

        total_waiting = (
            self._total_waiting_time()
        )

        total_vehicles = len(
            traci.vehicle.getIDList()
        )

        queue_penalty = (
            2.0
            * total_queue
        )

        waiting_penalty = (
            0.02
            * total_waiting
        )

        congestion_penalty = (
            0.2
            * total_vehicles
        )

        reward = -(
            queue_penalty
            + waiting_penalty
            + congestion_penalty
        )

        return float(
            reward
        )

    # =====================================================
    # RESET
    # =====================================================
    def reset(
        self,
        seed=None,
        options=None,
    ):

        super().reset(
            seed=seed
        )

        self._start_sumo()

        observation = (
            self._get_observation()
        )

        info = {
            "simulation_time":
                traci.simulation.getTime(),

            "remaining_vehicles":
                traci.simulation
                .getMinExpectedNumber(),
        }

        return (
            observation,
            info
        )

    # =====================================================
    # STEP
    # =====================================================
    def step(
        self,
        action
    ):

        self._apply_actions(
            action
        )

        observation = (
            self._get_observation()
        )

        reward = (
            self._calculate_reward()
        )

        simulation_time = (
            traci.simulation.getTime()
        )

        remaining_vehicles = (
            traci.simulation
            .getMinExpectedNumber()
        )

        terminated = (
            remaining_vehicles <= 0
        )

        truncated = (
            simulation_time
            >= self.max_simulation_time
        )

        info = {
            "simulation_time":
                simulation_time,

            "remaining_vehicles":
                remaining_vehicles,
        }

        return (
            observation,
            reward,
            terminated,
            truncated,
            info,
        )

    # =====================================================
    # CLOSE
    # =====================================================
    def close(
        self
    ):

        if self.running:

            try:

                traci.close()

            except Exception:

                pass

            self.running = False