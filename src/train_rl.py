import os
import sys

from stable_baselines3 import PPO

from traffic_signal_env import TrafficSignalEnv


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


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "ppo_traffic_signal_v2"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ---------------------------------------------------------
# Create RL environment
# ---------------------------------------------------------

env = TrafficSignalEnv(
    max_simulation_time=4500,
    decision_interval=5,
    min_green=10,
    yellow_time=3,
)


# ---------------------------------------------------------
# PPO model
# ---------------------------------------------------------

model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
)


# ---------------------------------------------------------
# Train
# ---------------------------------------------------------

TOTAL_TIMESTEPS = 150_000

print()
print("=" * 60)
print("TRAINING PPO TRAFFIC SIGNAL CONTROLLER")
print("=" * 60)

print(
    f"\nTotal training timesteps: "
    f"{TOTAL_TIMESTEPS:,}"
)

print(
    f"\nModel will be saved to:\n"
    f"{MODEL_PATH}.zip"
)

print()


model.learn(
    total_timesteps=TOTAL_TIMESTEPS
)


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

model.save(
    MODEL_PATH
)


# ---------------------------------------------------------
# Close environment
# ---------------------------------------------------------

env.close()


# ---------------------------------------------------------
# Finished
# ---------------------------------------------------------

print()
print("=" * 60)
print("PPO TRAINING COMPLETED")
print("=" * 60)

print(
    f"\nSaved model:\n"
    f"{MODEL_PATH}.zip"
)

print()