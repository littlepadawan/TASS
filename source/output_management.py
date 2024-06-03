from datetime import datetime
from os import makedirs
from shutil import copyfile, rmtree

from source.configuration_setup import Configuration


def set_up_output_directory(config: Configuration):
    """
    Create the output directory and a subdirectory for temp files

    Args:
        config (Configuration): Configuration object contining the path to the output directory to be created
    """
    # Get current date and time as YYYYMMDD_HHMM
    now = datetime.now().strftime("%Y-%m-%d_%H%M")

    # Create the path to the output directory
    config.path_output_directory = f"{config.path_output_directory}/{now}"

    # Create the directory + subdirectory for temp files
    makedirs(config.path_output_directory)
    makedirs(f"{config.path_output_directory}/temp")


def copy_config_file(config: Configuration):
    """
    Copy the configuration file to the output directory

    Args:
        config (Configuration): Configuration object containing the path to the configuration file and the output directory
    """
    copyfile(config.path_config, f"{config.path_output_directory}/config.cfg")


def generate_parameter_file(
    config: Configuration,
    successful_parameters: list,
    no_files_found_for_interpolation: list,
    multiple_files_found_for_interpolation: list,
):
    """
    Create a file containing the stellar parameters for which spectra were generated

    OBS: This function is not used
    Args:
        config (Configuration): Configuration object containing the path to the output directory
        successful_parameters (list): List of dictionaries containing the successful parameter sets
        no_files_found_for_interpolation (list): List of dictionaries containing the parameter sets for which no files were found for interpolation
        multiple_files_found_for_interpolation (list): List of dictionaries containing the parameter sets for which multiple files were found for interpolation
    """
    # Create a file in the output directory
    with open(f"{config.path_output_directory}/stellar_parameters.txt", "w") as file:

        if no_files_found_for_interpolation:
            file.write("----------------------------------------\n")
            file.write("No spectrum generated because files\n")
            file.write("needed for interpolation were not found:\n")
            file.write("----------------------------------------\n")

            for parameter_set in no_files_found_for_interpolation:
                file.write(f"{parameter_set}\n")

        if multiple_files_found_for_interpolation:
            file.write("\n\n----------------------------------------\n")
            file.write("No spectrum generated because multiple\n")
            file.write("matching model atmospheres were found\n")
            file.write("for interpolation:\n")
            file.write("----------------------------------------\n")

            for parameter_set in multiple_files_found_for_interpolation:
                file.write(f"{parameter_set}\n")

        file.write("\n\n----------------------------------------\n")
        file.write("Spectra generated:\n")
        file.write("----------------------------------------\n")
        # Write successful parameters
        for parameter_set in successful_parameters:
            file.write(f"{parameter_set}\n")


def remove_temp_files(config: Configuration):
    # Remove the temp directory
    rmtree(f"{config.path_output_directory}/temp")
