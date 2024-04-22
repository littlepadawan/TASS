from input.configuration import Configuration
from datetime import datetime
import os  # TODO: Is entire os module needed?


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


def generate_spectrum(config: Configuration, input_parameters: dict):
    """
    Generates a spectrum for a set of input parameters.
    """
    # TODO: Generate babsma
    # TODO: Run babsma

    # TODO: Generate bsyn
    # TODO: Run bsyn


def generate_spectra(config: Configuration):
    """ """
    set_up_output_directory(config)

    # TODO: Read input parameters from input file
    with open(config.path_input_parameters, "r", newline="") as file:
        # Read the header
        header = file.readline().strip().split()

        # TODO: Check that all required columns are present in input parameters (what are they?)

        # Read the content
        for line in file:
            # Split the line into a list of values
            values = line.strip().split()

            # Create a dictionary with the header as keys and the values from this line
            input_parameters = dict(zip(header, values))
            print(input_parameters)

            # Generate spectrum for this set of input parameters
            generate_spectrum(config, input_parameters)


if __name__ == "__main__":
    config = Configuration()
    generate_spectra(config)
