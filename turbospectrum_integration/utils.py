from os import listdir
from re import match

import pandas as pd


def parse_model_atmosphere_filename(filename: str):
    """
    Parse the filename of a model atmosphere and extract its parameters.

    @param filename: The filename of the model atmosphere (not the full path)
    The filename is expected to be in the format:
    'p<teff>_g<logg>_m<feh>_t<alpha>_st_z<z>_<anything>.mod'

    After `<z>`, an underscore should be followed by any valid string, which
    must end with the `.mod` file extension.

    Example filename: s6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod
    """
    pattern = (
        r"p(\d+)_g([\+\-]\d+\.\d+)_m(\d+\.\d+)_t(\d+)_st_z([\+\-]\d+\.\d+)_.*\.mod"
    )
    # Check if the filename matches the pattern
    result = match(pattern, filename)
    # If it matches, extract the parameters
    if result:
        return {
            "teff": result.group(1),
            "logg": result.group(2),
            "feh": result.group(5),
            "filename": filename,
        }
    return None


def collect_model_atmosphere_parameters(directory: str):
    """
    Collect the parameters of all model atmospheres in the directory.

    Args:
        directory (str): The file path to the directory containing the model atmospheres.

    Returns:
        DataFrame: A DataFrame of dictionaries containing the parameters of each model atmosphere.
    """
    models = []
    for filename in listdir(directory):
        model_parameters = parse_model_atmosphere_filename(filename)

        if model_parameters:
            models.append(model_parameters)

    df = pd.DataFrame(models)

    return df
