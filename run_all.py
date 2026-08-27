import os
import sys
import subprocess

# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "models",
    "ppo_traffic_signal_v2.zip"
)

# --------------------------------------------------
# CHECK PPO MODEL
# --------------------------------------------------

if not os.path.exists(MODEL_FILE):
    print("\nERROR: PPO model not found.")
    print(f"Expected model location:\n{MODEL_FILE}")
    print("\nTrain the model first using:")
    print("python src/train_rl.py")
    sys.exit(1)

# --------------------------------------------------
# SCRIPTS TO RUN
# --------------------------------------------------

scripts = [
    os.path.join("src", "run_baseline.py"),
    os.path.join("src", "run_actuated.py"),
    os.path.join("src", "run_adaptive.py"),
    os.path.join("src", "run_rl_tripinfo.py"),
    os.path.join("src", "generate_figures.py"),
]

# --------------------------------------------------
# RUN EACH SCRIPT
# --------------------------------------------------

print("\n" + "=" * 70)
print("URBAN TRAFFIC SIGNAL DIGITAL TWIN")
print("RUNNING COMPLETE EVALUATION WORKFLOW")
print("=" * 70)

for script in scripts:

    script_path = os.path.join(PROJECT_ROOT, script)

    print("\n" + "-" * 70)
    print(f"Running: {script}")
    print("-" * 70)

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print("\n" + "=" * 70)
        print(f"ERROR: {script} failed.")
        print("Workflow stopped.")
        print("=" * 70)
        sys.exit(result.returncode)

    print(f"\nCompleted: {script}")

# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print("\n" + "=" * 70)
print("ALL CONTROLLERS COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nCompleted workflow:")

print("""
1. Fixed-Time Control
2. Actuated Control
3. Rule-Based Adaptive Control
4. PPO Reinforcement Learning Evaluation
5. Controller Comparison
6. Figure Generation
""")

print("Results folder:")
print(os.path.join(PROJECT_ROOT, "results"))

print("\nFigures folder:")
print(os.path.join(PROJECT_ROOT, "figures"))

print("\nDone.")