import sys
from configuration_setup import Configuration

REQUIRED_PARAMETERS = ["teff", "logg", "fe/h"]  # TODO: Add abundances


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


def generate_random_parameters():
    pass


def generate_uniform_parameters():
    pass


def generate_parameters():
    pass
