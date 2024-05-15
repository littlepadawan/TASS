from os import chdir, getcwd
from shutil import copyfile
from subprocess import CalledProcessError, run

import pandas as pd
from source.configuration_setup import Configuration
from source.turbospectrum_integration.utils import collect_model_atmosphere_parameters

# TODO: Refactor functions to find higher, lower, and closest models to be more DRY
# TODO: Refactor the function to get bracketing models to be more DRY
# TODO: Generate the model DataFrame once for the entire run instead of once per spectrum (like the config object)
# TODO: Extract the script string to a file
# TODO: Create template script should be called once for the entire run, maybe this file can just exist in wrapper directory, and the program copies the unique script to the interpolator directory?
# ? Create some spectrum object that hold stellar parameters, script path, etc. and pass that to the functions instead of just the stellar parameters?
# TODO: Create a function that is used once per run to set up interpolation things
# TODO: If several closest files are found - containing the same parameters - the interpolation and spectrum generation for this set of stellar parameter should stop


def needs_interpolation(stellar_parameters: dict, model_atmospheres: pd.DataFrame):
    """
    Check if the given stellar parameters need interpolation.

    Expected stellar parameters are teff, logg, and z.
    Args:
        stellar_parameters (dict): The stellar parameters to check for interpolation.
        model_atmospheres (DataFrame): A DataFrame of dictionaries containing the parameters of each model atmosphere.

    Returns:
        bool: True if the stellar parameters need interpolation, False otherwise.
        DataFrame: A DataFrame with the model atmospheres that match the given stellar parameters.
    """

    matches = model_atmospheres[
        (model_atmospheres["teff"] == stellar_parameters["teff"])
        & (model_atmospheres["logg"] == stellar_parameters["logg"])
        & (model_atmospheres["z"] == stellar_parameters["z"])
    ]
    # TODO: Maybe change to if no matches -> needs interpolation so (true, None), if more than one match (false, None), if one match (false, match)
    if matches.empty:
        return True, None
    else:
        return False, matches


def _get_models_with_lower_parameter_value(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get models with a parameter value lower than the target value.

    Args:
        target_parameter (str): The parameter to filter the models by.
        target_value: The target value to filter the models by.
        model_atmospheres (pd.DataFrame): A DataFrame of dictionaries
        containing the parameters of each model atmosphere.

    target_parameter is expected to be 'teff', 'logg', or 'z'.
    target_value is expected to be an integer or float.
    Raises:
        ValueError: If no models with the target parameter value lower
        than the target value are found.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the target parameter value lower than the target value.
    """

    filtered_models = model_atmospheres[
        model_atmospheres[target_parameter] < target_value
    ]
    if filtered_models.empty:
        raise ValueError(
            f"No models with {target_parameter} value lower than {target_value} found"
        )
    return filtered_models


def _get_models_with_higher_parameter_value(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get models with a parameter value higher than the target value.

    Args:
        target_parameter (str): The parameter to filter the models by.
        target_value: The target value to filter the models by.
        model_atmospheres (pd.DataFrame): A DataFrame of dictionaries containing the parameters of each model atmosphere.

    Raises:
        ValueError: If no models with the target parameter value higher than the target value are found.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the target parameter value higher than the target value.
    """

    filtered_models = model_atmospheres[
        model_atmospheres[target_parameter].astype(int) > target_value
    ]
    if filtered_models.empty:
        raise ValueError(
            f"No models with {target_parameter} value higher than {target_value} found"
        )
    return filtered_models


def _get_closest_models(
    target_parameter: str, target_value, model_atmospheres: pd.DataFrame
):
    """
    Get the models with the closest parameter value to the target value.

    The function calculates the minimum difference between the target value and the value of the models
    and returns the models where the difference matches the minimum difference.
    Args:
        target_parameter (str): The parameter to filter the models by.
        target_value: The target value to filter the models by.
        model_grid (pd.DataFrame): A DataFrame of dictionaries containing the parameters of each model atmosphere.

    Returns:
        pd.DataFrame: A DataFrame with the models that have the closest parameter value to the target value.
    """
    # Calculate the minimum difference between the target value and the value of the filtered models
    column_dtype = model_atmospheres[target_parameter].dtype
    if column_dtype == "int64":
        target_value = int(target_value)
    elif column_dtype == "float64":
        target_value = float(target_value)

    differences = (target_value - model_atmospheres[target_parameter]).abs()
    min_difference = differences.min()

    # Filter to get the models where the difference matches the minimum difference
    closest_models = model_atmospheres[differences == min_difference]

    return closest_models


def _get_bracketing_models(stellar_parameters: dict, model_atmospheres: pd.DataFrame):
    """
    Get the bracketing models for the given stellar parameters.

    The bracketing models are used to interpolate the model atmosphere
    and need to follow thevstructure required by Turbospectrum's
    interpolator:
    Model 1: Tefflow logglow zlow
    Model 2: Tefflow logglow zup
    Model 3: Tefflow loggup zlow
    Model 4: Tefflow loggup zup
    Model 5: Teffup logglow zlow
    Model 6: Teffup logglow zup
    Model 7: Teffup loggup zlow
    Model 8: Teffup loggup zup

    Args:
        stellar_parameters (dict): The stellar parameters to find bracketing models for.
        model_atmospheres (pd.DataFrame): A DataFrame of dictionaries containing the parameters of each model atmosphere.

    Returns:
        list: A list of DataFrames entries containing the bracketing models.
    """
    # Get all models with lower Teff value than the given stellar parameters
    tefflow_models = _get_models_with_lower_parameter_value(
        "teff", stellar_parameters["teff"], model_atmospheres
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

    # From the subset of models with the closest lower Teff and logg values,
    # get the models with a z value greater than the target parameter
    tefflow_logglow_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_logglow_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_tefflow_logglow_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_logglow_zup_models
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

    # From the subset of models with the closest lower Teff value and higher logg value,
    # get the models with a z value greater than the target parameter
    tefflow_loggup_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_tefflow_loggup_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_tefflow_loggup_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], tefflow_loggup_zup_models
    )

    # Get all models with higher Teff value than the target
    teffup_models = _get_models_with_higher_parameter_value(
        "teff", stellar_parameters["teff"], model_atmospheres
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

    # From the subset of models with the closest higher Teff and lower logg values,
    # get the models with a z value greater than the target parameter
    teffup_logglow_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_logglow_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_teffup_logglow_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_logglow_zup_models
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

    # From the subset of models with the closest higher Teff and higher logg values,
    # get the models with a z value greater than the target parameter
    teffup_loggup_zup_models = _get_models_with_higher_parameter_value(
        "z", stellar_parameters["z"], closest_teffup_loggup_models
    )
    # Filter these models to get the ones with the closest higher z value to the target parameter
    closest_teffup_loggup_zup_models = _get_closest_models(
        "z", stellar_parameters["z"], teffup_loggup_zup_models
    )

    # Gets the first model in every subset # TODO: Om det inte finns en närmaste modell, avbryt och ge felmeddelande
    model1 = closest_tefflow_logglow_zlow_models.iloc[0]
    model2 = closest_tefflow_logglow_zup_models.iloc[0]
    model3 = closest_tefflow_loggup_zlow_models.iloc[0]
    model4 = closest_tefflow_loggup_zup_models.iloc[0]
    model5 = closest_teffup_logglow_zlow_models.iloc[0]
    model6 = closest_teffup_logglow_zup_models.iloc[0]
    model7 = closest_teffup_loggup_zlow_models.iloc[0]
    model8 = closest_teffup_loggup_zup_models.iloc[0]

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

    Args:
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Side effects:
        Writes the template script to the interpolator directory.
    """

    # The template will be placed in the interpolator directory
    # TODO: Check if path to interpolator already ends with '/'
    path_template_script = f"{config.path_interpolator}/interpolate.script"

    script_content = r"""#!/bin/csh -f
set model_path = {{PY_MODEL_PATH}}

set marcs_binary = '.false.'
#set marcs_binary = '.true.'

#enter here the values requested for the interpolated model 
foreach Tref   ( {{PY_TREF}} )
foreach loggref ( {{PY_LOGGREF}} )
foreach zref ( {{PY_ZREF}} )
set modele_out = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.alt

# grid values bracketting the interpolation point (should be automatised!)
set Tefflow = {{PY_TEFFLOW}}
set Teffup  = {{PY_TEFFUP}}
set logglow = {{PY_LOGGLOW}}
set loggup  = {{PY_LOGGUP}}
set zlow    = {{PY_ZLOW}}
set zup     = {{PY_ZUP}}
set alflow  = +0.00
set alfup   = +0.00
set xit     = 01

#plane-parallel models
set model1 = p${Tefflow}_g${logglow}_m0.0_t${xit}_st_z${zlow}_a${alflow}_c+0.00_n+0.00_o${alflow}_r+0.00_s+0.00.mod
set model2 = p${Tefflow}_g${logglow}_m0.0_t${xit}_st_z${zup}_a${alfup}_c+0.00_n+0.00_o${alfup}_r+0.00_s+0.00.mod
set model3 = p${Tefflow}_g${loggup}_m0.0_t${xit}_st_z${zlow}_a${alflow}_c+0.00_n+0.00_o${alflow}_r+0.00_s+0.00.mod
set model4 = p${Tefflow}_g${loggup}_m0.0_t${xit}_st_z${zup}_a${alfup}_c+0.00_n+0.00_o${alfup}_r+0.00_s+0.00.mod
set model5 = p${Teffup}_g${logglow}_m0.0_t${xit}_st_z${zlow}_a${alflow}_c+0.00_n+0.00_o${alflow}_r+0.00_s+0.00.mod
set model6 = p${Teffup}_g${logglow}_m0.0_t${xit}_st_z${zup}_a${alfup}_c+0.00_n+0.00_o${alfup}_r+0.00_s+0.00.mod
set model7 = p${Teffup}_g${loggup}_m0.0_t${xit}_st_z${zlow}_a${alflow}_c+0.00_n+0.00_o${alflow}_r+0.00_s+0.00.mod
set model8 = p${Teffup}_g${loggup}_m0.0_t${xit}_st_z${zup}_a${alfup}_c+0.00_n+0.00_o${alfup}_r+0.00_s+0.00.mod


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


def copy_template_interpolator_script(config: Configuration, stellar_parameters: dict):
    """
    Copy the template script used to run the interpolator to a unique file.

    This function is used to create a unique script for each spectrum to be interpolated.
    This is done to enable running the interpolator in parallel for multiple spectra.

    Args:
        config (Configuration): The Configuration object containing paths to the interpolator directory.
        stellar_parameters (dict): The stellar parameters to interpolate.

    Returns:
        str: The unique filename of the copied script.
    """
    unique_filename = f"interpolate_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}.script"
    path_to_script_copy = f"{config.path_interpolator}/{unique_filename}"

    copyfile(f"{config.path_interpolator}/interpolate.script", path_to_script_copy)
    # Filename is returned so it can be used to run the interpolator
    return unique_filename


def _load_parameters_to_interpolator_script(
    script_name: str,
    stellar_parameters: dict,
    bracketing_models: list,
    config: Configuration,
):
    """
    Load the stellar parameters and bracketing models into the interpolator script.

    Args:
        script_name (str): The name of the script file to load the parameters into.
        stellar_parameters (dict): The stellar parameters to interpolate.
        bracketing_models (list): The bracketing models used for interpolation.
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Side effects:
        The placeholder in the script file is modified with the stellar parameters and bracketing models.
    """
    script_path = f"{config.path_interpolator}/{script_name}"  # TODO: This should be a parameter to the function
    with open(script_path, "r") as file:
        script_content = file.read()

    # Set the parameter values
    updates = {
        "MODEL_PATH": config.path_model_atmospheres,
        "TREF": stellar_parameters["teff"],
        "LOGGREF": stellar_parameters["logg"],
        "ZREF": stellar_parameters["z"],
        "OUTPUT_PATH": config.path_output_directory,
        "TEFFLOW": bracketing_models[0]["teff_str"],
        "TEFFUP": bracketing_models[7]["teff_str"],
        "LOGGLOW": bracketing_models[0]["logg_str"],
        "LOGGUP": bracketing_models[7]["logg_str"],
        "ZLOW": bracketing_models[0]["z_str"],
        "ZUP": bracketing_models[7]["z_str"],
    }

    # Replace the placeholders with the values
    for update, value in updates.items():
        script_content = script_content.replace(f"{{{{PY_{update}}}}}", str(value))
    with open(script_path, "w") as file:
        file.write(script_content)


def _run_interpolation_script(script_name: str, config: Configuration):
    """
    Run the interpolation script.

    Args:
        script_name (str): The name of the script file to run.
        config (Configuration): The Configuration object containing paths to the interpolator directory.

    Raises:
        e: If the interpolation script fails to run.
    """
    cwd = getcwd()

    # Change the current working directory to where the interpolator is located
    chdir(config.path_interpolator)

    # Build the command
    command = f"./{script_name}"

    try:
        # Make sure the script is executable
        run(["chmod", "+x", script_name], check=True)
        # Run the interpolation script
        run([command], check=True, text=True, capture_output=True)
    except CalledProcessError as e:
        print(f"Error running interpolation script: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        chdir(cwd)


def generate_interpolated_model_atmosphere(
    stellar_parameters: dict, config: Configuration
):
    """
    Generate an interpolated model atmosphere.

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
    interpolator_script_name = copy_template_interpolator_script(
        config, stellar_parameters
    )
    # Load the stellar parameters and bracketing models into the script
    _load_parameters_to_interpolator_script(
        interpolator_script_name,
        stellar_parameters,
        bracketing_models,
        config,
    )
    # Run interpolation script
    _run_interpolation_script(interpolator_script_name, config)

    # TODO: Remove the script file after running it

    # Return path to the interpolated model atmosphere # TODO: This should be set in some kind of spectrum object instead
    return f"{config.path_output_directory}/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}.interpol"
