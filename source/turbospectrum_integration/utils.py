from os import listdir
from re import match

import pandas as pd


def parse_model_atmosphere_filename(filename: str):
    """
    Parse the filename of a model atmosphere and extract its parameters.

    The filename should not contain the full path, only the filename itself in the format:
    'p<teff>_g<logg>_m<feh>_t<alpha>_st_z<z>_<anything>.mod'

    After `<z>`, an underscore should be followed by any valid string, which
    must end with the `.mod` file extension.

    Example filename: s6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod

    Args:
        filename (str): The filename of the model atmosphere.

    Returns:
        dict: A dictionary containing the parameters of the model atmosphere.
    """
    # TODO: T värde ska anges i input filen. Microturbolunce, XIT, v_micro (km/s) (kolla mejl)
    # TODO: Lägg till alpha värde i pattern. OBS a och o i pattern ska vara samma värde
    pattern = (
        r"p(\d+)_g([\+\-]\d+\.\d+)_m(\d+\.\d+)_t(\d+)_st_z([\+\-]\d+\.\d+)_.*\.mod"
    )
    # Check if the filename matches the pattern
    result = match(pattern, filename)
    # If it matches, extract the parameters
    if result:
        teff_str, logg_str, z_str, turbulence_str = (
            result.group(1),
            result.group(2),
            result.group(5),
            result.group(4),
        )
        return {
            "teff": int(teff_str),
            "logg": float(logg_str),
            "z": float(z_str),
            "teff_str": teff_str,
            "logg_str": logg_str,
            "z_str": z_str,
            "turbulence_str": turbulence_str,
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


def stellar_parameter_to_str(stellar_parameter):
    """
    Convert stellar parameters to a string.

    Args:
        stellar_parameter: The stellar parameter to make a string of.

    Returns:
        str: A string representation of the stellar parameter.
    """
    if stellar_parameter < 0:
        return f"{stellar_parameter}"
    else:
        return f"+{stellar_parameter}"


def compose_filename(stellar_parameters: dict):
    teff_str = stellar_parameters["teff"]
    logg_str = stellar_parameter_to_str(stellar_parameters["logg"])
    z_str = stellar_parameter_to_str(stellar_parameters["z"])
    mg_str = stellar_parameter_to_str(stellar_parameters["mg"])
    ca_str = stellar_parameter_to_str(stellar_parameters["ca"])

    file_name = f"p{teff_str}_g{logg_str}_z{z_str}_mg{mg_str}_ca{ca_str}"
    return file_name
