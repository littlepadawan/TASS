from os import chdir, getcwd, path
from shutil import copyfile
from subprocess import CalledProcessError, run

import numpy as np
import pandas as pd
from source.configuration_setup import Configuration
from source.turbospectrum_integration.configuration import calculate_alpha
from source.turbospectrum_integration.utils import (
    collect_model_atmosphere_parameters,
    compose_filename,
)


def needs_interpolation(
    stellar_parameters: dict, alpha: float, model_atmospheres: pd.DataFrame
):
    """
    Check if the given stellar parameters need interpolation.

    Interpolation is needed if there is no matching model atmosphere.
        stellar_parameters (dict): The stellar parameters to check for interpolation, expected to contain the keys
    "teff", "logg", and "z"
        model_atmospheres (DataFrame): A DataFrame containing the parameters of each model atmosphere.

    Returns:
        bool: True if the stellar parameters need interpolation, False otherwise.
        DataFrame: A DataFrame with the model atmospheres that match the given stellar parameters.
    """

    matches = model_atmospheres[
        (model_atmospheres["teff"] == stellar_parameters["teff"])
        & (model_atmospheres["logg"] == stellar_parameters["logg"])
        & (model_atmospheres["z"] == stellar_parameters["z"])
        & (model_atmospheres["alpha"] == alpha)
    ]
    # TODO: Maybe change the function to have three different return values:
    # no matches and needs interpolation -> (true, None)
    # more than one match -> (false, None)
    # one match -> (false, match)
    if matches.empty:
        return True, None
    else:
        return False, matches


def _get_models_with_exact_value(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get models with a parameter value equal to the target value.

    Args:
        target_parameter (str): The parameter to filter the models by.
        target_value: The target value to filter the models by, can be an integer or float
        model_atmospheres (pd.DataFrame): A DataFrame containing the parameters of each model atmosphere.

    Raises:
        ValueError: If no models with the target parameter value equal to the target value are found.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the target parameter value equal to the target value.
    """
    # filtered_models = model_atmospheres[
    #     model_atmospheres[target_parameter] == target_value
    # ]
    # if filtered_models.empty:
    #     raise ValueError(
    #         f"No models with {target_parameter} value equal to {target_value} found"
    #     )
    filtered_models = model_atmospheres[
        model_atmospheres[target_parameter] == target_value
    ]
    return filtered_models


def _get_models_with_lower_parameter_value(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get models with a parameter value lower than the target value.

    Args:
        target_parameter (str): The parameter to filter the models by. Expected to be 'teff', 'logg', or 'z'.
        target_value: The target value to filter the models by. Can be an integer or float.
        model_atmospheres (pd.DataFrame): A DataFrame containing the parameters of each model atmosphere.
    Raises:
        ValueError: If no models with the target parameter value lower
        than the target value are found.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the target parameter value lower than the target value.
    """
    # ! There are no models with alppha < 0.0. Is this a valid solution?
    # if target_parameter == "alpha" and target_value == 0.0:
    #     return _get_models_with_exact_value(
    #         target_parameter, target_value, model_atmospheres
    #     )

    # filtered_models = model_atmospheres[
    #     model_atmospheres[target_parameter] < target_value
    # ]
    # if filtered_models.empty:
    #     raise ValueError(
    #         f"No models with {target_parameter} value lower than {target_value} found"
    #     )
    filtered_models = model_atmospheres[
        model_atmospheres[target_parameter] < target_value
    ]
    return filtered_models


def _get_models_with_higher_parameter_value(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get models with a parameter value higher than the target value.

    Args:
        target_parameter (str): The parameter to filter the models by. Expected to be 'teff', 'logg', or 'z'.
        target_value: The target value to filter the models by. Can be an integer or float.
        model_atmospheres (pd.DataFrame): A DataFrame containing the parameters of each model atmosphere.
    Raises:
        ValueError: If no models with the target parameter value higher than the target value are found.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the target parameter value higher than the target value.
    """
    # Debugging: print the DataFrame and the data type of the target parameter column
    # print("Model Atmospheres DataFrame:")
    # print(model_atmospheres)
    # print(
    #     f"Data type of {target_parameter} column: {model_atmospheres[target_parameter].dtype}"
    # )
    # print(f"Data type of target_value: {type(target_value)}")

    # if model_atmospheres[target_parameter].dtype == "int64":
    #     target_value = int(target_value)
    # else:
    #     target_value = float(target_value)

    # filtered_models = model_atmospheres[
    #     model_atmospheres[target_parameter] > target_value
    # ]

    # # Debugging: print the filtered DataFrame
    # # print("Filtered Models DataFrame:")
    # # print(filtered_models)

    # if filtered_models.empty:
    #     raise ValueError(
    #         f"No models with {target_parameter} value higher than {target_value} found"
    #     )
    filtered_models = model_atmospheres[
        model_atmospheres[target_parameter] > target_value
    ]
    return filtered_models


def _get_closest_models(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get the models with the closest parameter value to the target value.

    The function calculates the minimum difference between the target value and the value of the models
    and returns the models where the difference matches the minimum difference.
    Args:
        target_parameter (str): The parameter to filter the models by. Expected to be 'teff', 'logg', or 'z'.
        target_value: The target value to filter the models by. Can be an integer or float.
        model_atmospheres (pd.DataFrame): A DataFrame containing the parameters of each model atmosphere.
    Returns:
        pd.DataFrame: A DataFrame with the models that have the closest parameter value to the target value.
    """
    # # Calculate the minimum difference between the target value and the value of the filtered models
    # column_dtype = model_atmospheres[target_parameter].dtype
    # tolerance = 0
    # if column_dtype == "int64":
    #     target_value = int(target_value)
    # elif column_dtype == "float64":
    #     target_value = float(target_value)
    #     tolerance = 0.01

    # differences = (target_value - model_atmospheres[target_parameter]).abs()

    # # # Debugging: Print the differences
    # # print(f"Differences for {target_parameter}:\n{differences}")

    # min_difference = round(differences.min(), 3)

    # # # Debugging: Print the minimum difference
    # # print(f"Minimum difference for {target_parameter}: {min_difference}")

    # # Filter to get the models where the difference matches the minimum difference
    # closest_models = model_atmospheres[np.isclose(differences, min_difference)]

    # # Debugging: Print the closest models
    # # print(
    # #     f"Closest models for {target_parameter} with target value {target_value} and min difference {min_difference}:\n{closest_models}"
    # # )
    # # print("")
    column_dtype = model_atmospheres[target_parameter].dtype
    target_value = int(target_value) if column_dtype == "int64" else float(target_value)
    differences = (target_value - model_atmospheres[target_parameter]).abs()
    min_difference = round(differences.min(), 3)
    closest_models = model_atmospheres[np.isclose(differences, min_difference)]

    return closest_models


def _get_bracketing_models(stellar_parameters: dict, model_atmospheres: pd.DataFrame):
    """
    Get the bracketing models for the given stellar parameters.

    The bracketing models are used to interpolate the model atmosphere
    and need to follow thevstructure required by Turbospectrum's
    interpolator:
    Model 1: Tefflow logglow zlow alflow
    Model 2: Tefflow logglow zup alfup
    Model 3: Tefflow loggup zlow alflow
    Model 4: Tefflow loggup zup alfup
    Model 5: Teffup logglow zlow alflow
    Model 6: Teffup logglow zup alfup
    Model 7: Teffup loggup zlow alflow
    Model 8: Teffup loggup zup alfup

    Args:
        stellar_parameters (dict): The stellar parameters to find bracketing models for.
        model_atmospheres (pd.DataFrame): A DataFrame containing the parameters of each model atmosphere.

    Returns:
        list: A list of DataFrames entries containing the bracketing models.
    """
    # # Get all models with correct turbulence
    correct_turbulence_models = _get_models_with_exact_value(
        "turbulence_str", "01", model_atmospheres
    )

    # Get all models with lower Teff value than the given stellar parameters
    tefflow_models = _get_models_with_lower_parameter_value(
        "teff", stellar_parameters["teff"], correct_turbulence_models
    )
    # Filter these models to get the ones with the closest Teff value to the target parameter
    closest_tefflow_models = _get_closest_models(
        "teff", stellar_parameters["teff"], tefflow_models
    )

    # From the subset of models with the closest lower Teff value,
    # get the models with a logg value lower than the target parameter
    tefflow_logglow_models = _get_models_with_lower_parameter_value(
        "logg", stellar_parameters["logg"], closest_tefflow_models
    )
    # Filter these models to get the ones with the closest logg value to the target parameter
    closest_tefflow_logglow_models = _get_closest_models(
        "logg", stellar_parameters["logg"], tefflow_logglow_models
    )

    # From the subset of models with the closest lower Teff and logg values,
    # get the models with a z value less than the target parameter
    tefflow_logglow_zlow_models = _get_models_with_lower_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_logglow_models
    )
    # Filter these models to get the ones with the closest lower z value to the target parameter
    closest_tefflow_logglow_zlow_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_logglow_zlow_models
    )

    # Model 1: Tefflow logglow zlow alflow
    # Calculate alflow based of zlow
    zlow = closest_tefflow_logglow_models.iloc[0]["z"]
    alflow = calculate_alpha(zlow)

    # From the subset of models with the closest lower Teff, logg, and z values,
    # get the models with alpha = alflow
    tefflow_logglow_zlow_alflow_models = _get_models_with_exact_value(
        "alpha", alflow, closest_tefflow_logglow_zlow_models
    )
    # Choose the first model in the subset
    # If no models with alflow are found, choose the one with the closest alpha value
    model1 = (
        tefflow_logglow_zlow_alflow_models.iloc[0]
        if not tefflow_logglow_zlow_alflow_models.empty
        else _get_closest_models(
            "alpha", alflow, closest_tefflow_logglow_zlow_models
        ).iloc[0]
    )

    # From the subset of models with the closest lower Teff and logg values,
    # get the models with a z value greater than the target parameter
    tefflow_logglow_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_logglow_models
    )

    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_tefflow_logglow_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_logglow_zup_models
    )
    # Model 2: Tefflow logglow zup alfup
    # Calculate alfup based of zup
    zup = closest_tefflow_logglow_zup_models.iloc[0]["z"]
    alfup = calculate_alpha(zup)

    # From the subset of models with the closest lower Teff value, lower logg value, and higher z value,
    # get the models with an alpha value = alfup
    tefflow_logglow_zup_alfup_models = _get_models_with_exact_value(
        "alpha", alfup, closest_tefflow_logglow_zup_models
    )
    # Choose the first model in the subset
    # If no models with alfup are found, choose the one with the closest alpha value
    model2 = (
        tefflow_logglow_zup_alfup_models.iloc[0]
        if not tefflow_logglow_zup_alfup_models.empty
        else _get_closest_models(
            "alpha", alfup, closest_tefflow_logglow_zup_models
        ).iloc[0]
    )

    # From the subset of models with the closest lower Teff value,
    # get the models with a logg value greater than the target parameter
    tefflow_loggup_models = _get_models_with_higher_parameter_value(
        "logg", stellar_parameters["logg"], closest_tefflow_models
    )
    # Filter these models to get the ones with the closest higher logg value to the target parameter
    closest_tefflow_loggup_models = _get_closest_models(
        "logg", stellar_parameters["logg"], tefflow_loggup_models
    )

    # From the subset of models with the closest lower Teff value and higher logg value,
    # get the models with a z value less than the target parameter
    tefflow_loggup_zlow_models = _get_models_with_lower_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_loggup_models
    )
    # Filter these models to get the ones with the closest lower z value to the target parameter
    closest_tefflow_loggup_zlow_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_loggup_zlow_models
    )

    # Model 3: Tefflow loggup zlow alflow
    # Calculate alflow based of zlow
    zlow = closest_tefflow_loggup_zlow_models.iloc[0]["z"]
    alflow = calculate_alpha(zlow)

    # From the subset of models with the closest lower Teff value, higher logg value, and lower z value,
    # get the models with alpha = alflow
    tefflow_loggup_zlow_alflow_models = _get_models_with_exact_value(
        "alpha", alflow, closest_tefflow_loggup_zlow_models
    )
    # Choose the first model in the subset
    # If no models with alflow are found, choose the one with the closest alphavalue
    model3 = (
        tefflow_logglow_zlow_models.iloc[0]
        if not tefflow_logglow_zlow_models.empty
        else _get_closest_models(
            "alpha", alflow, closest_tefflow_logglow_zlow_models
        ).iloc[0]
    )

    # From the subset of models with the closest lower Teff value and higher logg value,
    # get the models with a z value greater than the target parameter
    tefflow_loggup_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_loggup_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_tefflow_loggup_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_loggup_zup_models
    )

    # Model 4: Tefflow loggup zup alfup
    # Calculate alfup based of zup
    zup = closest_tefflow_loggup_zup_models.iloc[0]["z"]
    alfup = calculate_alpha(zup)

    # From the subset of models with the closest lower Teff value, higher logg value, and higher z value,
    # get the models with alpha = alfup
    tefflow_loggup_zup_alfup_models = _get_models_with_exact_value(
        "alpha", alfup, closest_tefflow_loggup_zup_models
    )
    # Choose the first model in the subset
    # If no models with alfup are found, choose the one with the closest alpha value
    model4 = (
        tefflow_loggup_zup_alfup_models.iloc[0]
        if not tefflow_loggup_zup_alfup_models.empty
        else _get_closest_models(
            "alpha", alfup, closest_tefflow_loggup_zup_models
        ).iloc[0]
    )

    # Get all models with higher Teff value than the target
    teffup_models = _get_models_with_higher_parameter_value(
        "teff", stellar_parameters["teff"], correct_turbulence_models
    )
    # Get the models that have the closest higher Teff value to the target parameter
    closest_teffup_models = _get_closest_models(
        "teff", stellar_parameters["teff"], teffup_models
    )

    # From the subset of models with the closest higher Teff value,
    # get the models with a logg value less than the target parameter
    teffup_logglow_models = _get_models_with_lower_parameter_value(
        "logg", stellar_parameters["logg"], closest_teffup_models
    )
    # Filter these models to get the ones with the closest lower logg value to the target parameter
    closest_teffup_logglow_models = _get_closest_models(
        "logg", stellar_parameters["logg"], teffup_logglow_models
    )

    # From the subset of models with the closest higher Teff and lower logg value,
    # get the models with a z value less than the target parameter
    teffup_logglow_zlow_models = _get_models_with_lower_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_logglow_models
    )
    # Filter these models to get the ones with the closest lower z value to the target parameter
    closest_teffup_logglow_zlow_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_logglow_zlow_models
    )

    # Model 5: Teffup logglow zlow alflow
    # Calculate alflow based of zlow
    zlow = closest_teffup_logglow_zlow_models.iloc[0]["z"]
    alflow = calculate_alpha(zlow)

    # From the subset of models with the closest higher Teff value, lower logg value, and lower z value,
    # get the models with alpha = alflow
    teffup_logglow_zlow_alflow_models = _get_models_with_exact_value(
        "alpha", alflow, closest_teffup_logglow_zlow_models
    )
    # Choose the first model in the subset
    # If no models with alflow are found, choose the one with the closest alpha value
    model5 = (
        teffup_logglow_zlow_alflow_models.iloc[0]
        if not teffup_logglow_zlow_alflow_models.empty
        else _get_closest_models(
            "alpha", alflow, closest_teffup_logglow_zlow_models
        ).iloc[0]
    )

    # From the subset of models with the closest higher Teff and lower logg values,
    # get the models with a z value greater than the target parameter
    teffup_logglow_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_logglow_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_teffup_logglow_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_logglow_zup_models
    )

    # Model 6: Teffup logglow zup alfup
    # Calculate alfup based of zup
    zup = closest_teffup_logglow_zup_models.iloc[0]["z"]
    alfup = calculate_alpha(zup)

    # From the subset of models with the closest higher Teff value, lower logg value, and higher z value,
    # get the models with alpha = alfup
    teffup_logglow_zup_alfup_models = _get_models_with_exact_value(
        "alpha", alfup, closest_teffup_logglow_zup_models
    )
    # Choose the first model in the subset
    # If no models with alfup are found, choose the one with the closest alpha value
    model6 = (
        teffup_logglow_zup_alfup_models.iloc[0]
        if not teffup_logglow_zup_alfup_models.empty
        else _get_closest_models(
            "alpha", alfup, closest_teffup_logglow_zup_models
        ).iloc[0]
    )

    # From the subset of models with the closest higher Teff value,
    # get the models with a logg value greater than the target parameter
    teffup_loggup_models = _get_models_with_higher_parameter_value(
        "logg", stellar_parameters["logg"], closest_teffup_models
    )
    # Filter these models to get the ones with the closest higher logg value to the target parameter
    closest_teffup_loggup_models = _get_closest_models(
        "logg", stellar_parameters["logg"], teffup_loggup_models
    )

    # From the subset of models with the closest higher Teff and higher logg values,
    # get the models with a z value less than the target parameter
    teffup_loggup_zlow_models = _get_models_with_lower_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_loggup_models
    )
    # Filter these models to get the ones with the closest lower z value to the target parameter
    closest_teffup_loggup_zlow_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_loggup_zlow_models
    )

    # Model 7: Teffup loggup zlow alflow
    # Calculate alflow based of zlow
    zlow = closest_teffup_loggup_zlow_models.iloc[0]["z"]
    alflow = calculate_alpha(zlow)

    # From the subset of models with the closest higher Teff value, higher logg value, and lower z value,
    # get the models with alpha = alflow
    teffup_loggup_zlow_alflow_models = _get_models_with_exact_value(
        "alpha", alflow, closest_teffup_loggup_zlow_models
    )
    # Filter these models to get the ones with the closest lower alpha value to the target parameter
    # If no models are found, return the closest model (not sure if this is closest)
    model7 = (
        teffup_loggup_zlow_alflow_models.iloc[0]
        if (teffup_loggup_zlow_alflow_models.index.size > 0)
        else closest_teffup_loggup_zlow_models.iloc[0]
    )

    # From the subset of models with the closest higher Teff and higher logg values,
    # get the models with a z value greater than the target parameter
    teffup_loggup_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_loggup_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_teffup_loggup_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_loggup_zup_models
    )

    # Model 8: Teffup loggup zup alfup
    # Calculate alfup based of zup
    zup = closest_teffup_loggup_zup_models.iloc[0]["z"]
    alfup = calculate_alpha(zup)
    # From the subset of models with the closest higher Teff value, higher logg value, and higher z value,
    # get the models with alpha = alfup
    teffup_loggup_zup_alfup_models = _get_models_with_exact_value(
        "alpha", alfup, closest_teffup_loggup_zup_models
    )
    # Filter these models to get the ones with the closest higher alpha value to the target parameter
    # If no models are found, return the closest model (not sure if this is closest)
    model8 = (
        teffup_loggup_zup_alfup_models.iloc[0]
        if not teffup_loggup_zup_alfup_models.empty
        else closest_teffup_loggup_zup_models.iloc[0]
    )

    return [model1, model2, model3, model4, model5, model6, model7, model8]


def _get_models_for_interpolation(stellar_parameters: dict, model_directory: str):
    """
    Wrapper function to get all the models needed for interpolation

    Args:
        stellar_parameters (dict): The stellar parameters to find bracketing models for.
        model_directory (str): The absolute path to the directory containing the model atmospheres.

    Returns:
        list: A list of DataFrames entries containing the bracketing models.
    """
    # Parse filenames in the model directory to get the model atmospheres
    all_models = collect_model_atmosphere_parameters(model_directory)
    # Get the bracketing models for the given stellar parameters
    bracketing_models = _get_bracketing_models(stellar_parameters, all_models)

    return bracketing_models


def create_template_interpolator_script(config: Configuration):
    """
    Create the template script used to run the interpolator.

    The script is a copy of the one provided by Turbospectrum (interpolator/interpol.script).
    Changes from the original script are:
    - The paths are set by placeholders
    - The values are set by placeholders
    - Some comments are removed

    This function only needs to be called once per run.
    Args:
        config (Configuration): The Configuration object containing the path to the directory with the interpolator.

    Side effects:
        Writes the template script to the interpolator directory.
    """

    # The template will be placed in the interpolator directory
    # TODO: Check if path to interpolator already ends with '/'
    path_template_script = f"{config.path_output_directory}/temp/interpolate.script"

    # TODO: alup and alflpw + xit need to be fetched from config
    script_content = r"""#!/bin/csh -f
set model_path = {{PY_MODEL_PATH}}

set marcs_binary = '.false.'

#enter here the values requested for the interpolated model 
foreach Tref   ( {{PY_TREF}} )
foreach loggref ( {{PY_LOGGREF}} )
foreach zref ( {{PY_ZREF}} )
set modele_out = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.alt

#plane-parallel models
set model1 = {{PY_MODEL1}}
set model2 = {{PY_MODEL2}}
set model3 = {{PY_MODEL3}}
set model4 = {{PY_MODEL4}}
set model5 = {{PY_MODEL5}}
set model6 = {{PY_MODEL6}}
set model7 = {{PY_MODEL7}}
set model8 = {{PY_MODEL8}}

#### the test option is set to .true. if you want to plot comparison model (model_test)
set test = '.false.'
set model_test = 'Testwebformat/p5750_g+4.5_m0.0_t01_ap_z-0.25_a+0.00_c+0.00_n+0.00_o+0.00_r+0.00_s+0.00.mod'

# interpolation program (for further details see interpol_modeles.f)
./interpol_modeles <<EOF
'${model_path}/${model1}'
'${model_path}/${model2}'
'${model_path}/${model3}'
'${model_path}/${model4}'
'${model_path}/${model5}'
'${model_path}/${model6}'
'${model_path}/${model7}'
'${model_path}/${model8}'
'${modele_out}'
'${modele_out2}'
${Tref}
${loggref}
${zref}
${test}
${marcs_binary}
'${model_test}'
EOF

end
end 
end
"""
    with open(path_template_script, "w") as file:
        file.write(script_content)


def copy_template_interpolator_script(
    config: Configuration, alpha: float, stellar_parameters: dict
):
    """
    Copy the template interpolator script to a unique script for this set of stellar parameters.

    This function is used to create a unique script for each set of stellar parameters to interpolate an atmosphere for.
    This is done to enable (eventually) running the interpolator in parallel for multiple spectra.

    Args:
        config (Configuration): The Configuration object containing paths to the interpolator directory.
        stellar_parameters (dict): The stellar parameters to interpolate.

    Returns:
        str: The path of the copied script.
    """
    unique_filename = compose_filename(stellar_parameters, alpha)
    path_to_script_copy = (
        f"{config.path_output_directory}/temp/interpolate_{unique_filename}.script"
    )

    copyfile(
        f"{config.path_output_directory}/temp/interpolate.script", path_to_script_copy
    )
    # Filename is returned so it can be used to run the interpolator
    return path_to_script_copy


def _load_parameters_to_interpolator_script(
    script_path: str,
    stellar_parameters: dict,
    bracketing_models: list,
    config: Configuration,
):
    """
    Load the stellar parameters and bracketing models into the interpolator script.

    Args:
        script_path (str): The path to the script file to load the parameters into.
        stellar_parameters (dict): The stellar parameters to interpolate.
        bracketing_models (list): The bracketing models used for interpolation.
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Side effects:
        The placeholder in the script file is modified with the stellar parameters and bracketing models.
    """
    # Read the script file
    with open(script_path, "r") as file:
        script_content = file.read()

    # Set the parameter values
    # updates = {
    #     "MODEL_PATH": config.path_model_atmospheres,
    #     "TREF": stellar_parameters["teff"],
    #     "LOGGREF": stellar_parameters["logg"],
    #     "ZREF": stellar_parameters["z"],
    #     "OUTPUT_PATH": f"{config.path_output_directory}/temp",
    #     "TEFFLOW": bracketing_models[0]["teff_str"],
    #     "TEFFUP": bracketing_models[7]["teff_str"],
    #     "LOGGLOW": bracketing_models[0]["logg_str"],
    #     "LOGGUP": bracketing_models[7]["logg_str"],
    #     "ZLOW": bracketing_models[0]["z_str"],
    #     "ZUP": bracketing_models[7]["z_str"],
    # }
    # print(
    #     f"Bracketing models: \n{bracketing_models[0]} \n{bracketing_models[1]} \n{bracketing_models[2]}\n{bracketing_models[3]}\n{bracketing_models[4]}\n{bracketing_models[5]}\n{bracketing_models[6]}\n{bracketing_models[7]}"
    # )
    updates = {
        "MODEL_PATH": config.path_model_atmospheres,
        "TREF": stellar_parameters["teff"],
        "LOGGREF": stellar_parameters["logg"],
        "ZREF": stellar_parameters["z"],
        "OUTPUT_PATH": f"{config.path_output_directory}/temp",
        "MODEL1": bracketing_models[0].filename,
        "MODEL2": bracketing_models[1].filename,
        "MODEL3": bracketing_models[2].filename,
        "MODEL4": bracketing_models[3].filename,
        "MODEL5": bracketing_models[4].filename,
        "MODEL6": bracketing_models[5].filename,
        "MODEL7": bracketing_models[6].filename,
        "MODEL8": bracketing_models[7].filename,
    }

    # Replace the placeholders with the values
    for update, value in updates.items():
        script_content = script_content.replace(f"{{{{PY_{update}}}}}", str(value))
    with open(script_path, "w") as file:
        file.write(script_content)


def _run_interpolation_script(script_path: str, config: Configuration):
    """
    Run the interpolation script.

    Args:
        script_path (str): The path to the script file to run.
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Raises:
        CalledProcessError: If the interpolation script fails to run.
    """
    cwd = getcwd()

    # Get the directory where the script is located
    script_dir = path.dirname(script_path)

    # Change the current working directory to where the script is located
    chdir(config.path_interpolator)
    # print(f"Running interpolation script in {script_dir}")

    # Build the command
    # command = f".{script_path}"

    try:
        # Make sure the script is executable
        run(["chmod", "+x", script_path], check=True)
        # Run the interpolation script
        run(
            [script_path],
            check=True,
            text=True,
            capture_output=True,
        )
    except CalledProcessError as e:
        print(f"Error running interpolation script: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        chdir(cwd)


def generate_interpolated_model_atmosphere(
    stellar_parameters: dict, alpha: float, config: Configuration
):
    """
    Generate an interpolated model atmosphere.

    This is a wrapper function that calls the functions needed to interpolate a model atmosphere for a set of stellar parameters.

    Args:
        stellar_parameters (dict): The stellar parameters to interpolate.
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Returns:
        str: The path to the interpolated model atmosphere.
    """

    # ! The interpolator script template needs to be created before this function can be called
    # Get files needed for interpolation
    bracketing_models = _get_models_for_interpolation(
        stellar_parameters, config.path_model_atmospheres
    )
    # Create a unique script for this interpolation
    interpolator_script_path = copy_template_interpolator_script(
        config, alpha, stellar_parameters
    )
    # Load the stellar parameters and bracketing models into the script
    _load_parameters_to_interpolator_script(
        interpolator_script_path,
        stellar_parameters,
        bracketing_models,
        config,
    )
    # Run interpolation script
    _run_interpolation_script(interpolator_script_path, config)

    # Return path to the interpolated model atmosphere # TODO: This should be set in some kind of spectrum object instead
    return f"{config.path_output_directory}/temp/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}.interpol"


# The following TODOs are thoughts on improvements and refactoring that could be done to the code
# (will be removed before the final "submission")
# TODO: Refactor functions to find higher, lower, and closest models to be more DRY
# TODO: Refactor the function to get bracketing models to be more DRY
# TODO: Generate the model DataFrame once for the entire run instead of once per spectrum (like the config object)
# TODO: Extract the script string to a file
# TODO: Create template script should be called once for the entire run, maybe this file can just exist in wrapper directory, and the program copies the unique script to the interpolator directory?
# ? Create some spectrum object that hold stellar parameters, script path, etc. and pass that to the functions instead of just the stellar parameters?
# TODO: Create a function that is used once per run to set up interpolation things
# TODO: If several closest files are found - containing the same parameters - the interpolation and spectrum generation for this set of stellar parameter should stop
