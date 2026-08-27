import os
import sys

# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from rl.traffic_signal_env import TrafficSignalEnv


def main():

    # -----------------------------------------------------
    # Environment
    # -----------------------------------------------------
    env = TrafficSignalEnv(
        max_simulation_time=4500,
        decision_interval=5,
        min_green=10,
        yellow_time=3,
    )

    env = Monitor(env)

    # -----------------------------------------------------
    # PPO model
    # -----------------------------------------------------
    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        seed=42,
    )

    # -----------------------------------------------------
    # Training
    # -----------------------------------------------------
    model.learn(
        total_timesteps=150000,
        progress_bar=True,
    )

    # -----------------------------------------------------
    # Save V2 model
    # -----------------------------------------------------
    model_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "ppo_traffic_signal_v2",
    )

    os.makedirs(
        os.path.dirname(model_path),
        exist_ok=True,
    )

    model.save(model_path)

    env.close()

    print()
    print("PPO V2 training completed.")
    print(
        "Model saved to: "
        "models/ppo_traffic_signal_v2.zip"
    )


if __name__ == "__main__":
    main()