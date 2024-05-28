import os
import random
import sys

import numpy as np
from source.configuration_setup import Configuration

REQUIRED_PARAMETERS = ["teff", "logg", "z", "mg", "ca"]
MIN_PARAMETER_DELTA = {
    "teff": 5,
    "logg": 0.05,
    "z": 0.001,
    "mg": 0.001,
    "ca": 0.001,
}

# TODO: This should be removed once loopsq
MAX_PARAMETER_DISTANCE = {
    "teff": 100,
    "logg": 0.5,
    "z": 0.01,
}


def _check_required_parameters(parameters: list):
    """
    Check that all required parameters specified in REQUIRED_PARAMETERS are present in the parameters.

    Args:
        parameters (list): List of parameters to check

    Raises:
        ValueError: If any of the required parameters are missing
    """
    missing_parameters = [
        parameter for parameter in REQUIRED_PARAMETERS if parameter not in parameters
    ]
    if missing_parameters:
        raise ValueError(
            f"Missing required stellar parameters in input parameters: {', '.join(missing_parameters)}",
        )


def read_parameters_from_file(config: Configuration):
    """
    Read stellar parameters from input file

    Args:
        config (Configuration): Configuration object
    Returns:
        list: List of dictionaries containing the stellar parameters
    """
    with open(config.path_input_parameters, "r", newline="") as file:
        # Read the header to get column names
        header = file.readline().strip().split()

        # Check that all required parameters are present in the file
        try:
            _check_required_parameters(header)
            print("All required parameters are present in the input file")
        except ValueError as e:
            print(e)
            sys.exit(
                1
            )  # We don't want to continue if the required parameters are missing

        all_stellar_parameters = []

        # Read file content
        for line in file:
            # Split the line into a list of values
            values = line.strip().split()

            float_values = [float(value) for value in values]

            # Create a dictionary with the header as keys and the values from this line
            stellar_parameters = dict(zip(header, float_values))

            # Add the dictionary to the list of all stellar parameters
            all_stellar_parameters.append(stellar_parameters)

        # Convert teff values to integers
        for parameter_set in all_stellar_parameters:
            parameter_set["teff"] = int(parameter_set["teff"])

    return all_stellar_parameters


def _within_min_delta(new_parameter, existing, min_delta):
    """
    Check if the value of new_parameter is within the minimum delta of existing.

    Returns:
        bool: True if the value of new_parameter is within the minimum delta of existing, False otherwise
    """
    return abs(new_parameter - existing) < min_delta


def _validate_new_set(
    teff: int, logg: float, z: float, mg: float, ca: float, parameters: dict
):
    """
    Check if a new set of stellar parameters is valid, i.e. if it is outside the minimum distance of any existing set.

    Args:
        teff (int): Effective temperature
        logg (float): Surface gravity
        z (float): Metallicity
        mg (float): Abundance of magnesium
        ca (float): Abundance of calcium
        parameters (dict): A dictionary containing lists of existing parameters

    Returns:
        bool: True if the new set is valid, False otherwise
    """
    # Get all parameter sets who's teff value are within the minimum distance from teff
    teff_collisions = [
        i
        for i, existing_teff in enumerate(parameters["teff"])
        if _within_min_delta(teff, existing_teff, MIN_PARAMETER_DELTA["teff"])
    ]

    # In the subset of parameter sets that have "the same" teff value as the candidate set,
    # check if any of them have logg values within the minimum distance from logg
    teff_logg_collisions = [
        i
        for i in teff_collisions
        if _within_min_delta(logg, parameters["logg"][i], MIN_PARAMETER_DELTA["logg"])
    ]

    # In the subset of parameter sets that have "the same" teff and logg values as the candidate set,
    # check if any of them have z values within the minimum distance from z
    teff_logg_z_collisions = [
        i
        for i in teff_logg_collisions
        if _within_min_delta(z, parameters["z"][i], MIN_PARAMETER_DELTA["z"])
    ]

    # In the subset of parameter sets that have "the same" teff, logg and z values as the candidate set,
    # check if any of them have mg values within the minimum distance from mg
    teff_logg_z_mg_collisions = [
        i
        for i in teff_logg_z_collisions
        if _within_min_delta(mg, parameters["mg"][i], MIN_PARAMETER_DELTA["mg"])
    ]

    # In the subset of parameter sets that have "the same" teff, logg, z and mg values as the candidate set,
    # check if any of them have ca values within the minimum distance from ca
    for i in teff_logg_z_mg_collisions:
        if _within_min_delta(ca, parameters["ca"][i], MIN_PARAMETER_DELTA["ca"]):
            # There was a collision in all parameters, meaning there exists a set with "the same" parameters
            return False

    # No full set collision found, or no collision at all
    return True


def generate_random_parameters(config: Configuration):
    """
    Generate random stellar parameters

    Args:
        config (Configuration): Configuration object containing ranges and step sizes for the parameters to be generated

    Returns:
        list: List of dictionaries containing the generated stellar parameters
    """
    teff_range = (config.teff_min, config.teff_max)
    logg_range = (config.logg_min, config.logg_max)
    z_range = (config.z_min, config.z_max)
    mg_range = (config.mg_min, config.mg_max)
    ca_range = (config.ca_min, config.ca_max)

    # Storage for parameters and links between them (index)
    parameters = {"teff": [], "logg": [], "z": [], "ca": [], "mg": []}

    # Storage for generated sets
    completed_sets = []

    while len(completed_sets) < config.num_spectra:
        teff = random.randint(*teff_range)
        logg = round(random.uniform(*logg_range), 2)
        z = round(random.uniform(*z_range), 3)
        mg = round(random.uniform(*mg_range), 3)
        ca = round(random.uniform(*ca_range), 3)

        if _validate_new_set(teff, logg, z, mg, ca, parameters):
            parameters["teff"].append(teff)
            parameters["logg"].append(logg)
            parameters["z"].append(z)
            parameters["mg"].append(mg)
            parameters["ca"].append(ca)
            completed_sets.append(
                {"teff": teff, "logg": logg, "z": z, "mg": mg, "ca": ca}
            )

    return completed_sets


def generate_evenly_spaced_parameters(config: Configuration):
    """
    Generate evenly spaced stellar parameters

    Args:
        config (Configuration): Configuration object containing ranges and step sizes for the parameters to be generated

    Returns:
        list: List of dictionaries containing the generated stellar parameters
    """
    # Generate evenly spaced values for each parameter
    teff_values = np.round(
        np.linspace(config.teff_min, config.teff_max, config.num_points_teff)
    )
    logg_values = np.round(
        np.linspace(config.logg_min, config.logg_max, config.num_points_logg), 2
    )
    z_values = np.round(np.linspace(config.z_min, config.z_max, config.num_points_z), 3)
    mg_values = np.round(
        np.linspace(config.mg_min, config.mg_max, config.num_points_mg), 3
    )
    ca_values = np.round(
        np.linspace(config.ca_min, config.ca_max, config.num_points_ca), 3
    )

    # Generate all combinations of the parameter values
    parameter_sets = []
    for t in teff_values:
        for logg in logg_values:
            for z in z_values:
                for mg in mg_values:
                    for ca in ca_values:
                        parameter_sets.append(
                            {
                                "teff": t,
                                "logg": round(logg, 2),
                                "z": round(z, 3),
                                "mg": round(mg, 3),
                                "ca": round(ca, 3),
                            }
                        )
    return parameter_sets


def generate_parameters(config: Configuration):
    """
    Generate stellar parameters based on the settings in configuration.

    Based on what the user specified in the configuation file, this function will either read stellar parameters from a file,
    generate random stellar parameters or generate evenly spaced stellar parameters.
    Args:
        config (Configuration): Configuration object

    Returns:
        list: List of tuples containing the generated stellar parameters
    """
    print("Im being called")
    print("Read stellar parameter from file ", config.read_stellar_parameters_from_file)
    parameters = []
    # TODO: Write to a file?
    if config.read_stellar_parameters_from_file:
        print("Reading stellar parameters from file")
        parameters = read_parameters_from_file(config)
    elif config.random_parameters:
        print("Generating random stellar parameters")
        parameters = generate_random_parameters(config)
    else:
        print("Generating evenly spaced stellar parameters")
        parameters = generate_evenly_spaced_parameters(config)

    # Write parameters to a file in the output directory
    output_file = os.path.join(config.path_output_directory, "generated_parameters.txt")
    with open(output_file, "w") as file:
        # Write the header
        headers = parameters[0].keys()
        file.write(" ".join(headers) + "\n")
        # Write the parameters
        for param in parameters:
            file.write(" ".join(str(param[key]) for key in headers) + "\n")

    return parameters
