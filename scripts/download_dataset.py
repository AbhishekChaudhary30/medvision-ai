import argparse
import logging
import os
from pathlib import Path
import subprocess
import zipfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def download_kaggle_dataset(dataset_name: str, output_dir: Path):
    """
    Downloads a Kaggle dataset or competition data.
    Requires KAGGLE_USERNAME and KAGGLE_KEY environment variables to be set,
    or the ~/.kaggle/kaggle.json file to exist.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Kaggle CLI command
    if dataset_name.startswith("c/"):
        comp_name = dataset_name[2:]
        cmd = ["kaggle", "competitions", "download", "-c", comp_name, "-p", str(output_dir)]
        zip_path = output_dir / f"{comp_name}.zip"
    else:
        cmd = ["kaggle", "datasets", "download", "-d", dataset_name, "-p", str(output_dir)]
        zip_name = dataset_name.split("/")[-1]
        zip_path = output_dir / f"{zip_name}.zip"

    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download dataset. Ensure Kaggle credentials are set. Error: {e}")
        return
        
    if zip_path.exists():
        logger.info(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        logger.info("Extraction complete. Cleaning up zip file...")
        zip_path.unlink()
    else:
        logger.warning(f"Expected zip file {zip_path} not found. Check if the download succeeded and is unzipped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download medical imaging dataset from Kaggle")
    parser.add_argument(
        "--dataset", 
        type=str, 
        default="c/rsna-pneumonia-detection-challenge", 
        help="Kaggle dataset ID (e.g. c/rsna-pneumonia-detection-challenge)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data/raw", 
        help="Output directory for the dataset"
    )
    
    args = parser.parse_args()
    
    # Automatically load .env if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
        
    download_kaggle_dataset(args.dataset, Path(args.output_dir))
