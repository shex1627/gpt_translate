import subprocess
import time
import argparse
import logging

def configure_logging(level):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=log_format)

def run_script(script_path, interval, python_exe: str="/opt/shichenh/miniconda3/envs/gpt_translate/bin/python"):
    logging.info(f"Running script {script_path}")
    try:
        subprocess.run([python_exe, script_path])
    except Exception as e:
        logging.error(f"Failed to run script {script_path}: {e}")
    

def restart_service(service_names):
    for service in service_names:
        logging.info(f"Restarting user service {service}")
        try:
            subprocess.run(["systemctl", "--user", "restart", service])
        except Exception as e:
            logging.error(f"Failed to restart service {service}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run another Python script at regular intervals.")
    parser.add_argument("script_path", type=str, help="Path to the Python script to be run.")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between script runs. Default is 60 seconds.")
    parser.add_argument("--log_level", type=str, default="INFO", help="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is INFO.")
    parser.add_argument("--services", nargs='+', help="List of user services to restart.")

    args = parser.parse_args()

    configure_logging(args.log_level)
    
    while True:
        if args.services:
            restart_service(args.services)
        
        run_script(args.script_path, args.interval)
        logging.info(f"Sleeping for {args.interval} seconds")
        time.sleep(args.interval)
