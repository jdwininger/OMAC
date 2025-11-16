"""
Quickstart script for OMAC - One 'Mazing ActionFigure Catalog

Sets up the Python virtual environment, installs dependencies, and launches the application.
"""
import os
import sys
import subprocess

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(WORKSPACE, ".venv")
REQUIREMENTS = os.path.join(WORKSPACE, "requirements.txt")
MAIN_SCRIPT = os.path.join(WORKSPACE, "main.py")


def run(cmd, check=True):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode


def create_venv():
    if not os.path.isdir(VENV_DIR):
        print("Creating virtual environment...")
        run([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print("Virtual environment already exists.")


def install_requirements():
    pip_path = os.path.join(VENV_DIR, "bin", "pip") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "pip.exe")
    print("Installing dependencies from requirements.txt...")
    run([pip_path, "install", "--upgrade", "pip"])
    run([pip_path, "install", "-r", REQUIREMENTS])


def launch_app():
    python_path = os.path.join(VENV_DIR, "bin", "python") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "python.exe")
    print("Launching OMAC application...")
    run([python_path, MAIN_SCRIPT], check=False)


def main():
    create_venv()
    install_requirements()
    launch_app()


if __name__ == "__main__":
    main()
