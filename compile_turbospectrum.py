import subprocess  # TODO: Maybe dont import entire subprocess module
import os  # TODO: Maybe dont import entire os module
from input.configuration import Configuration


# TODO: Where to place this file?
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
