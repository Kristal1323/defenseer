import subprocess
import sys

def main():
    """
    Entry point for launching the DefenSeer Streamlit UI.
    This simply forwards execution to Streamlit, ensuring the app/ui.py file is used.
    """
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app/ui.py"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Could not launch Streamlit UI.")
        sys.exit(1)

if __name__ == "__main__":
    main()
