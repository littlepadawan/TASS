import subprocess  # TODO: Maybe dont import entire subprocess module
import os  # TODO: Maybe dont import entire os module
import output_management
from configuration_setup import Configuration


def compile_turbospectrum(config: Configuration):
    """
    Compile Turbospectrum using the specified compiler
    """

    # Change the current working directory to where the Makefile is located
    original_directory = os.getcwd()
    os.chdir(config.path_turbospectrum_compiled)

    try:
        # Run make command to compile Turbospectrum
        result = subprocess.run(["make"], check=True, text=True, capture_output=True)
        print(f"Compilation of Turbospectrum successful")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling Turbospectrum: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        os.chdir(original_directory)


def compile_interpolator(config: Configuration):
    # TODO: OK to assume using Turbospectrums interpolator?
    # TODO: How to do it with another interpolator?
    # TODO: Look at the command for compiling in interpolator readme, there is no makefile
    pass


def generate_interpolated_model_atmosphere(
    config: Configuration, input_parameters: dict
):
    """
    Interpolate a model atmosphere
    """
    # TODO: Check if model atmosphere already exists
    # TODO: If it does not, interpolate it.
    #   TODO: 8 MARCS files are needed (look in readme)
    #   TODO: Multiple of paths need to be changed in script


def create_babsma(config: Configuration):
    """
    Create the babsma file
    """
    babsma_content = f"""\
        'LAMBDA_MIN:'   '{config.wavelength_min}'
        'LAMBDA_MAX:'   '{config.wavelength_max}'
        'LAMBDA_STEP:'  '{config.wavelength_step}'
        'MODELINPUT:'   '{config.path_model_atmospheres}'
        'MARCS-FILE:'   '.true.'
        'MODELOPAC:'    '{config.path_output_directory}/opac'
        'METALLICITY:'  '{config.metallicity}'
    """


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
    output_management.set_up_output_directory(config)
    generate_spectra(config)
