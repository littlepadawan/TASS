from os import listdir
from re import match

import pandas as pd


def parse_model_atmosphere_filename(filename: str):
    """
    Parse the filename of a model atmosphere and extract its parameters.

    The filename should not contain the full path, only the filename itself in the format:
    p<teff>_g<logg>_m<some number>_t<xit>_st_z<z>_a<alpha>_c<some number>_n<some number>_o<some number>_r<some number>_s<some number>.mod

    Example filename: p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod

    Args:
        filename (str): The filename of the model atmosphere.

    Returns:
        dict: A dictionary containing the parameters of the model atmosphere.
    """
    # TODO: t value should be specified in config (microturbolunce, XIT, v_micro (km/s), and read from the pattern
    pattern = r"p(\d+)_g([\+\-]\d+\.\d+)_m([\+\-]?\d+\.\d+)_t(\d+)_st_z([\+\-]\d+\.\d+)_a([\+\-]\d+\.\d+)_c([\+\-]\d+\.\d+)_n([\+\-]\d+\.\d+)_o([\+\-]\d+\.\d+)_r([\+\-]\d+\.\d+)_s([\+\-]\d+\.\d+)\.mod"
    # Check if the filename matches the pattern
    result = match(pattern, filename)
    # If it matches, extract the parameters
    if result:
        teff_str, logg_str, z_str, turbulence_str, alpha_str = (
            result.group(1),
            result.group(2),
            result.group(5),
            result.group(4),
            result.group(6),
        )

        return {
            "teff": int(teff_str),
            "logg": float(logg_str),
            "z": float(z_str),
            "alpha": float(alpha_str),
            "teff_str": teff_str,
            "logg_str": logg_str,
            "z_str": z_str,
            "turbulence_str": turbulence_str,
            "alpha_str": alpha_str,
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


def stellar_parameter_to_str(stellar_parameter, decimals):
    """
    Convert stellar parameters to a string.

    Args:
        stellar_parameter: The stellar parameter to turn into a string.
        decimals: The number of decimals to include in the string.
    Returns:
        str: A string representation of the stellar parameter.
    """
    return f"{stellar_parameter:+.{decimals}f}"


def compose_filename(stellar_parameters: dict, alpha: float):
    """
    Generate a filename based on the stellar parameters.

    Args:
        stellar_parameters (dict): The stellar parameters for which to generate the filename.
        alpha (float): The alpha enhancement.
    Returns:
        str: The filename
    """
    # TODO: This should contain t values
    teff_str = stellar_parameters["teff"]
    logg_str = stellar_parameter_to_str(stellar_parameters["logg"], 1)
    z_str = stellar_parameter_to_str(stellar_parameters["z"], 2)
    mg_str = stellar_parameter_to_str(stellar_parameters["mg"], 2)
    ca_str = stellar_parameter_to_str(stellar_parameters["ca"], 2)
    alpha_str = stellar_parameter_to_str(alpha, 2)

    file_name = f"p{teff_str}_g{logg_str}_z{z_str}_a{alpha_str}_mg{mg_str}_ca{ca_str}"
    return file_name
