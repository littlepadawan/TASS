from os import chdir, getcwd
from subprocess import CalledProcessError, run

from configuration_setup import Configuration


def compile_turbospectrum(config: Configuration):
    """
    Compile Turbospectrum using the Makefile located in Turbospectrum's directory.

    Args:
        config (Configuration): The Configuration object containing paths to the Turbospectrum directory.

    Raises:
        subprocess.CalledProcessError: If the compilation of Turbospectrum fails.
    """

    cwd = getcwd()
    # Change the current working directory to where the Turbospectrum's Makefile is located
    chdir(
        config.path_turbospectrum_compiled
    )  # TODO: Change so the function takes this as string instead of entire config object

    try:
        # Run make command to compile Turbospectrum
        result = run(["make"], check=True, text=True, capture_output=True)
        # print(f"Compilation of Turbospectrum successful") # ? Remove print?
    except CalledProcessError as e:
        print(f"Error compiling Turbospectrum: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        chdir(cwd)


def compile_interpolator(config: Configuration):
    """
    Compile the interpolator.

    The interpolator used is the one provided by Turbospectrum.
    The command used to compile the interpolator is specified
    in the Turbospectrum documentation (readme file of the interpolator):
    `<compilator> -o interpol_modeles interpol_modeles.f`

    Where compilator can be either gfortrand or ifort.

    Args:
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Raises:
        subprocess.CalledProcessError: If the compilation of the interpolator fails.
    """

    cwd = getcwd()
    # Change the current working directory to where the interpolator is located
    chdir(
        config.path_interpolator
    )  # TODO: Change so the function takes this as string instead of entire config object

    # Command from readme: gfortran -o interpol_modeles interpol_modeles.f
    command = [config.compiler, "-o", "interpol_modeles", "interpol_modeles.f"]

    try:
        # Run command to compile interpolator
        result = run(command, check=True, text=True, capture_output=True)
        # print(f"Compilation of interpolator successful") # ? Remove print?
    except CalledProcessError as e:
        print(f"Error compiling interpolator: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        chdir(cwd)
