import random
import sys

import numpy as np
from rtree import index
from source.configuration_setup import Configuration

REQUIRED_PARAMETERS = ["teff", "logg", "z", "mg", "ca"]
MIN_PARAMETER_DELTA = {
    "teff": 5,
    "logg": 0.05,
    "z": 0.001,
    "mg": 0.001,
    "ca": 0.001,
}
MAX_PARAMETER_DISTANCE = {
    "teff": 100,
    "logg": 0.5,
    "z": 0.01,
}  # TODO: Add abundances
# TODO: Min-max in configuration file?
# TODO: Max does not apply to random, and not to evenly either i think...


def _check_required_parameters(parameters: list):
    """
    Check that all required parameters are present in the input parameters
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
    Read input parameters from input file
    """
    with open(config.path_input_parameters, "r", newline="") as file:
        # Read the header to get column names
        header = file.readline().strip().split()

        # Check that all required parameters are present in the file
        try:
            _check_required_parameters(header)
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

            # Create a dictionary with the header as keys and the values from this line
            stellar_parameters = dict(zip(header, values))

            # Add the dictionary to the list of all stellar parameters
            all_stellar_parameters.append(stellar_parameters)

    return all_stellar_parameters


def generate_random_parameters_no_distance_check(config: Configuration):
    """
    Generate random stellar parameters
    """
    # TODO: How to handle min step size?
    # TODO: Consider fixed size allocation (1000 ok, 10 000 maybe not)
    all_stellar_parameters = set()

    while len(all_stellar_parameters) < config.num_spectra:
        teff = random.randint(config.teff_min, config.teff_max)
        logg = random.uniform(config.logg_min, config.logg_max)
        z = random.uniform(config.z_max, config.z_max)
        mg = random.uniform(config.mg_min, config.mg_max)
        ca = random.uniform(config.ca_min, config.ca_max)

        logg = round(logg, 2)
        z = round(z, 3)
        mg = round(mg, 3)  # TODO: Correct number of decimals?
        ca = round(ca, 3)

        all_stellar_parameters.add(
            (teff, logg, z)
        )  # If this combination already exists in all_stellar_parameters, it will not be added again

    return all_stellar_parameters


def _within_min_delta(new_parameter, existing, min_delta):
    """
    Check if the candidate values are within the minimum delta of the parameter value
    """
    return abs(new_parameter - existing) < min_delta


def _validate_new_set(teff, logg, z, mg, ca, parameters):
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
        list: List of tuples containing the generated stellar parameters
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
        list: List of tuples containing the generated stellar parameters
    """
    # TODO: Change this function to just loop given sets
    dimensions = 3  # TODO: Remove hard coding
    intervals = round(config.num_spectra ** (1 / dimensions))

    # Adjust intervals to get the exact number of spectra
    while intervals**dimensions < config.num_spectra:
        intervals += 1

    # Generate evenly spaced values
    parameter_ranges = {
        "teff": np.linspace(config.teff_min, config.teff_max, intervals),
        "logg": np.linspace(config.logg_min, config.logg_max, intervals),
        "z": np.linspace(config.z_min, config.z_max, intervals),
    }

    # Use meshgrid to get all combinations
    grid = np.meshgrid(*parameter_ranges.values())

    parameter_sets = np.stack(grid, axis=-1).reshape(-1, dimensions)
    parameter_sets = [
        (round(teff, 0), round(logg, 2), round(z, 3))
        for teff, logg, z in parameter_sets[: config.num_spectra]
    ]
    return parameter_sets


def generate_parameters(config: Configuration):
    """
    Generate stellar parameters based on the configuration

    Args:
        config (Configuration): Configuration object

    Returns:
        list: List of tuples containing the generated stellar parameters
    """
    if config.read_stellar_parameters_from_file:
        return read_parameters_from_file(config)
    elif config.random_parameters:
        return generate_random_parameters(config)
    else:
        return generate_evenly_spaced_parameters(config)

    # TODO: Write to a file?
