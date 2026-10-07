import subprocess
import sys

def run_pipeline():
    """
    Download the latest IESO demand data,
    then update the processed dataset.
    """

    download_result = subprocess.run([sys.executable, "scripts/01_download_ieso_demand.py"], capture_output=True, text=True)

    if download_result.returncode != 0:
        print(f"Error downloading data: {download_result.stderr}")
        sys.exit(1)

    update_result = subprocess.run([sys.executable, "scripts/02_check_new_rows.py"], capture_output=True, text=True)

    if update_result.returncode != 0:
        print("Error updating dataset.")
        print("Return code:", update_result.returncode)
        print("Output:", update_result.stdout.strip())
        print("Error:", update_result.stderr.strip())
        sys.exit(1)

    print(update_result.stdout.strip())
    print("Pipeline execution completed successfully.")


run_pipeline()