import datetime
from configuration_setup import Configuration
import os  # TODO: Is the entire os module needed?


def set_up_output_directory(config: Configuration):
    """
    Generates up the output directory for the generated spectra.
    """
    # Get current date and time as YYYYMMDD_HH:MM
    now = datetime.now().strftime("%Y-%m-%d@%H:%M")

    # Create the path to the output directory
    config.path_output_directory = f"{config.path_output_directory}/{now}"

    # Create the directory
    os.makedirs(config.path_output_directory)
    os.makedirs(f"{config.path_output_directory}/opac")
