import os
import sys
import subprocess


PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "models",
    "ppo_traffic_signal_v2.zip"
)


# ---------------------------------------------------------
# Check trained PPO model
# ---------------------------------------------------------
if not os.path.exists(MODEL_FILE):

    print()
    print("ERROR: PPO V2 model not found.")
    print()
    print(
        "Expected file:"
    )
    print(
        MODEL_FILE
    )
    print()
    print(
        "Run this first:"
    )
    print(
        "python training/train_rl.py"
    )

    sys.exit(1)


scripts = [
    "run_baseline.py",
    "run_actuated.py",
    "run_adaptive.py",
    "run_rl_tripinfo.py",
    os.path.join(
        "evaluation",
        "generate_figures.py"
    ),
]


for script in scripts:

    print()
    print("=" * 65)
    print(f"RUNNING: {script}")
    print("=" * 65)

    result = subprocess.run(
        [
            sys.executable,
            script
        ],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:

        print()
        print("=" * 65)
        print(
            f"ERROR WHILE RUNNING: {script}"
        )
        print("=" * 65)

        sys.exit(
            result.returncode
        )


print()
print("=" * 65)
print("ALL PROJECT ANALYSES COMPLETED SUCCESSFULLY")
print("=" * 65)
print()
print("Check:")
print("  results/")
print("  figures/")