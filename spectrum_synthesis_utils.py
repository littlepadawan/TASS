import subprocess  # TODO: Maybe dont import entire subprocess module
import os  # TODO: Maybe dont import entire os module
from input.configuration import Configuration


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


def compute_model_atmosphere(config: Configuration, input_parameters: dict):
    """
    Compute a model atmosphere
    """
    # TODO: Check if model atmosphere already exists
    # TODO: If it does not, interpolate it.
    #   TODO: 8 MARCS files are needed (look in readme)
    #   TODO: ALot of paths need to be changed in script


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
