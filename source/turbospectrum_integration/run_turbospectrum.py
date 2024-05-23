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
    except Exception as e:
        print(f"Error running bsyn: {e}")
        raise e
    finally:
        chdir(cwd)


def generate_one_spectrum(
    config: Configuration, stellar_parameters: dict, model_atmospheres: list
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
    # TODO: Isnt model_atmospheres a DataFrame?

    # Setup Turbospectrum configuration for this set of stellar parameters
    ts_config = TurbospectrumConfiguration(config, stellar_parameters)

    # Check if the model atmosphere needs to be interpolated
    interpolate, matching_models = needs_interpolation(
        stellar_parameters, model_atmospheres
    )

    # TODO: Improve this part
    if interpolate:
        # Generate interpolated model atmosphere
        # TODO: If generate_interpolated_model_atmosphere can return errors, this is not a good solution
        ts_config.path_model_atmosphere = generate_interpolated_model_atmosphere(
            stellar_parameters, config
        )
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
    for parameter_set in stellar_parameters:
        generate_one_spectrum(config, parameter_set, model_atmospheres)
        # TODO: If successful, add the parameters to a list of successful parameters
        # TODO: If unsuccessful, add the parameters to a list of unsuccessful parameters (split by reasons)
