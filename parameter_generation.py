import random
import sys

import numpy as np
from configuration_setup import Configuration
from rtree import index

REQUIRED_PARAMETERS = ["teff", "logg", "z"]  # TODO: Add abundances
MIN_PARAMETER_DELTA = {
    "teff": 5,
    "logg": 0.05,
    "z": 0.001,
}  # TODO: Add abundances
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
    # TODO: How to handle step requirements? Tree?
    # TODO: Consider fixed size allocation (1000 ok, 10 000 maybe not)
    all_stellar_parameters = set()

    while len(all_stellar_parameters) < config.num_spectra:
        teff = random.randint(config.teff_min, config.teff_max)
        logg = random.uniform(config.logg_min, config.logg_max)
        z = random.uniform(config.z_max, config.z_max)
        # TODO: Add abundances

        logg = round(logg, 2)
        z = round(z, 3)

        all_stellar_parameters.add(
            (teff, logg, z)
        )  # If this combination already exists in all_stellar_parameters, it will not be added again

    return all_stellar_parameters


def _within_min_delta(new_parameter, existing, min_delta):
    """
    Check if the candidate values are within the minimum delta of the parameter value
    """
    return abs(new_parameter - existing) < min_delta


def _validate_new_set(teff, logg, z, parameters):
    teff_collisions = [
        i
        for i, existing_teff in enumerate(parameters["teff"])
        if _within_min_delta(teff, existing_teff, MIN_PARAMETER_DELTA["teff"])
    ]

    for index in teff_collisions:

        logg_collision = (
            abs(parameters["logg"][index] - logg) < MIN_PARAMETER_DELTA["logg"]
        )
        # print(f"Checking index {index}: Logg Collision: {logg_collision}")
        if logg_collision:
            z_collision = abs(parameters["z"][index] - z) < MIN_PARAMETER_DELTA["z"]
            # print(
            #     f"Checking index {index}: Logg Collision: {logg_collision}, z Collision: {z_collision})"
            # )
            if z_collision:
                return False
    # No full set collision found, or no collision at all
    return True


def generate_random_parameters(config: Configuration):
    """
    Generate random stellar parameters
    """
    teff_range = (config.teff_min, config.teff_max)
    logg_range = (config.logg_min, config.logg_max)
    z_range = (config.z_min, config.z_max)

    # Storage for parameters and links between them (index)
    parameters = {"teff": [], "logg": [], "z": []}

    # Storage for generated sets
    completed_sets = []

    while len(completed_sets) < config.num_spectra:
        teff = random.randint(*teff_range)
        logg = round(random.uniform(*logg_range), 2)
        z = round(random.uniform(*z_range), 3)

        if _validate_new_set(teff, logg, z, parameters):
            parameters["teff"].append(teff)
            parameters["logg"].append(logg)
            parameters["z"].append(z)
            completed_sets.append((teff, logg, z))

    return completed_sets


def generate_evenly_spaced_parameters(config: Configuration):
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
    if config.read_stellar_parameters_from_file:
        return read_parameters_from_file(config)
    elif config.random_parameters:
        return generate_random_parameters(config)
    else:
        return generate_evenly_spaced_parameters(config)
