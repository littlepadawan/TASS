import concurrent.futures
import copy
from os import chdir, getcwd
from subprocess import PIPE, run

from pandas import DataFrame
from source.configuration_setup import Configuration
from source.turbospectrum_integration.configuration import (
    TurbospectrumConfiguration,
    create_babsma,
    create_bsyn,
)
from source.turbospectrum_integration.interpolation import (
    generate_interpolated_model_atmosphere,
    needs_interpolation,
)


def run_babsma(ts_config: TurbospectrumConfiguration, config: Configuration):
    """
    Run the babsma script.

    Args:
        ts_config (TurbospectrumConfiguration): The TurboSpectrum configuration object
        config (Configuration): The Configuration object

    Raises:
        Exception: If an error occurs while running babsma
    """
    # Create the path to the log file
    log_file_path = (
        f"{config.path_output_directory}/temp/{ts_config.file_name}_babsma.log"
    )

    # Construct the path to the babsma executable
    babsma_executable = f"{config.path_turbospectrum_compiled}/babsma_lu"
    cwd = getcwd()

    # Change to directory where babsma is expected to run
    chdir(config.path_turbospectrum)

    try:
        with open(ts_config.path_babsma, "r") as file:
            result = run(
                [babsma_executable],
                stdin=file,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            with open(log_file_path, "w") as log_file:
                log_file.write("Standard Output:\n")
                log_file.write(result.stdout)
                log_file.write("\n\nStandard Error:\n")
                log_file.write(result.stderr)
    except Exception as e:
        print(f"Error running babsma: {e}")
        raise e
    finally:
        chdir(cwd)


def run_bsyn(ts_config: TurbospectrumConfiguration, config: Configuration):
    """
    Run the bsyn script.

    Args:
        ts_config (TurbospectrumConfiguration): The TurboSpectrum configuration object
        config (Configuration): The Configuration object

    Raises:
        Exception: If an error occurs while running bsyn
    """
    # Create the path to the log file
    log_file_path = (
        f"{config.path_output_directory}/temp/{ts_config.file_name}_bsyn.log"
    )

    # Construct the path to the bsyn executable
    bsyn_executable = f"{config.path_turbospectrum_compiled}/bsyn_lu"
    cwd = getcwd()
    # Change to directory where basyn is expected to run
    chdir(config.path_turbospectrum)

    try:
        with open(ts_config.path_bsyn, "r") as file:
            result = run(
                [bsyn_executable],
                stdin=file,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            with open(log_file_path, "w") as log_file:
                log_file.write("Standard Output:\n")
                log_file.write(result.stdout)
                log_file.write("\n\nStandard Error:\n")
                log_file.write(result.stderr)
    except Exception as e:
        print(f"Error running bsyn: {e}")
        raise e
    finally:
        chdir(cwd)


def generate_one_spectrum(
    config: Configuration, stellar_parameters: dict, model_atmospheres: DataFrame
):
    """
    Generate a spectrum for a given set of stellar parameters.

    Args:
        config (Configuration): The Configuration object
        stellar_parameters (dict): The stellar parameters for which to generate the spectrum
        model_atmospheres (list): The list of model atmospheres available

    Raises:
        ValueError: If more than one matching model atmosphere is found
    """

    # Setup Turbospectrum configuration for this set of stellar parameters
    ts_config = TurbospectrumConfiguration(config, stellar_parameters)

    # Check if the model atmosphere needs to be interpolated
    interpolate, matching_models = needs_interpolation(
        stellar_parameters, ts_config.alpha, model_atmospheres
    )

    if interpolate:
        try:
            # Generate interpolated model atmosphere
            ts_config.path_model_atmosphere, error_message = (
                generate_interpolated_model_atmosphere(
                    stellar_parameters, ts_config.alpha, config, model_atmospheres
                )
            )
            if ts_config.path_model_atmosphere is None:
                print(
                    f"It was not possible to interpolate a model atmosphere for the following stellar parameters: {stellar_parameters}"
                )
                print(error_message)

                return
        except Exception as e:
            print(
                f"Error generating interpolated model atmosphere for stellar parameters: {stellar_parameters}.\n{e}"
            )
            return
            # raise e # Raising an error here will stop the execution of the program
    elif len(matching_models) == 1:
        # A matching MARCS model was found, use it
        ts_config.path_model_atmosphere = matching_models[0]
    else:
        # More than one matching model was found, we dont't know which one to use
        raise ValueError("More than one matching model found")

    # Set flag for interpolated model atmosphere
    ts_config.interpolated_model_atmosphere = interpolate

    create_babsma(config, ts_config, stellar_parameters)
    run_babsma(ts_config, config)
    create_bsyn(config, ts_config, stellar_parameters)
    run_bsyn(ts_config, config)


def generate_all_spectra(
    config: Configuration, model_atmospheres: DataFrame, stellar_parameters: list
):
    """
    Generate spectra for all sets of stellar parameters.

    Args:
        config (Configuration): The Configuration object
        model_atmospheres (DataFrame): The DataFrame containing the model atmospheres
        stellar_parameters (list): The list of stellar parameters for which to generate spectra
    """
    # for parameter_set in stellar_parameters:
    #     generate_one_spectrum(config, parameter_set, model_atmospheres)

    def worker(parameter_set):
        config_copy = copy.deepcopy(config)
        generate_one_spectrum(config_copy, parameter_set, model_atmospheres)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(worker, parameter_set)
            for parameter_set in stellar_parameters
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error generating spectrum: {e}")
                # raise e
