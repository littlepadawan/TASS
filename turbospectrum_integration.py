from decimal import Decimal
import shutil
from string import Template
import subprocess  # TODO: Maybe dont import entire subprocess module
import os  # TODO: Maybe dont import entire os module
import re

import numpy as np
import pandas as pd
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
    """
    Compile the interpolator using the specified compiler (comes with Turbospectrum)
    """

    # Change the current working directory to where the interpolator is located
    original_directory = os.getcwd()
    os.chdir(config.path_interpolator)

    # Command from readme: gfortran -o interpol_modeles interpol_modeles.f
    command = [config.compiler, "-o", "interpol_modeles", "interpol_modeles.f"]

    try:
        # Run command to compile interpolator
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Compilation of interpolator successful")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling interpolator: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        os.chdir(original_directory)


def _parse_model_atmosphere_filename(filename: str):
    """
    Parse the filename of a model atmosphere to get its parameters
    """
    pattern = (
        r"p(\d+)_g([\+\-]\d+\.\d+)_m(\d+\.\d+)_t(\d+)_st_z([\+\-]\d+\.\d+)_.*\.mod"
    )

    match = re.match(pattern, filename)
    if match:

        # print(f"feh: {feh_decimal}")
        # print(f"filename: {filename}")
        # print()
        return {
            "teff": match.group(1),
            "logg": match.group(2),
            "feh": match.group(5),
            "filename": filename,
        }
    return None


def _extract_parameters_from_filenames(directory: str):
    """
    Extract the parameters from the filenames of the model atmospheres
    """
    models = []
    for filename in os.listdir(directory):
        model_parameters = _parse_model_atmosphere_filename(filename)
        if model_parameters:
            models.append(model_parameters)

    return models


def _create_model_grid(models: list):
    """
    Convert a list of dictionaries into a DataFrame for easy manipulation
    @param models: List of dictionaries with keys "teff", "logg", "feh", and "filename"
    """
    df = pd.DataFrame(models)
    return df


def _get_models_with_lower_parameter(
    target_parameter: str, target_value, model_grid: pd.DataFrame
):
    # Get all models where the value of target_parameter is lower than target_value
    filtered_lower = []
    if target_parameter == "teff":
        filtered_lower = model_grid[
            model_grid[target_parameter].astype(int) < target_value
        ]
    else:
        filtered_lower = model_grid[
            model_grid[target_parameter].astype(float) < target_value
        ]
    if filtered_lower.empty:
        raise ValueError(
            f"No models with {target_parameter} value lower than {target_value} found"
        )
    return filtered_lower


def _get_models_with_higher_parameter(
    target_parameter: str, target_value, model_grid: pd.DataFrame
):
    # Get all models where the value of target_parameter is higher than target_value
    filtered_higher = []
    if target_parameter == "teff":
        filtered_higher = model_grid[
            model_grid[target_parameter].astype(int) > target_value
        ]
    else:
        filtered_higher = model_grid[
            model_grid[target_parameter].astype(float) > target_value
        ]
    if filtered_higher.empty:
        raise ValueError(
            f"No models with {target_parameter} value higher than {target_value} found"
        )
    return filtered_higher


def _get_closest_models(target_parameter: str, target_value, model_grid: pd.DataFrame):
    # Calculate the minimum difference between the target value and the value of the filtered models
    min_difference = 0
    closest_models = []
    if target_parameter == "teff":
        min_difference = (
            (target_value - model_grid[target_parameter].astype(int)).abs().min()
        )
        # Get the models where the difference matches min_difference
        closest_models = model_grid[
            (target_value - model_grid[target_parameter].astype(int)).abs()
            == min_difference
        ]
    else:
        min_difference = (
            (target_value - model_grid[target_parameter].astype(float)).abs().min()
        )
        # Get the models where the difference matches min_difference
        closest_models = model_grid[
            (target_value - model_grid[target_parameter].astype(float)).abs()
            == min_difference
        ]

    return closest_models


def _find_bracketing_models(target_parameters: dict, model_grid: pd.DataFrame):
    # Get all models with lower Teff value than the target
    tefflow_models = _get_models_with_lower_parameter(
        "teff", target_parameters["teff"], model_grid
    )
    # Get the models that have the closest Teff value to the target parameter
    closest_tefflow_models = _get_closest_models(
        "teff", target_parameters["teff"], tefflow_models
    )

    # From the subset of models with the closest lower Teff value, get the models with a logg value less than the target parameter
    tefflow_logglow_models = _get_models_with_lower_parameter(
        "logg", target_parameters["logg"], closest_tefflow_models
    )
    # Get the models that have the closest logg value to the target parameter
    closest_tefflow_logglow_models = _get_closest_models(
        "logg", target_parameters["logg"], tefflow_logglow_models
    )

    # From the subset of models with the closest lower Teff and logg values, get the models with a feh value less than the target parameter
    tefflow_logglow_fehlow_models = _get_models_with_lower_parameter(
        "feh", target_parameters["feh"], closest_tefflow_logglow_models
    )
    # Get the models that have the closest lower feh value to the target parameter
    closest_tefflow_logglow_fehlow_models = _get_closest_models(
        "feh", target_parameters["feh"], tefflow_logglow_fehlow_models
    )

    # From the subset of models with the closest lower Teff and logg values, get the models with a feh value greater than the target parameter
    tefflow_logglow_fehhigh_models = _get_models_with_higher_parameter(
        "feh", target_parameters["feh"], closest_tefflow_logglow_models
    )
    # Get the models that have the closest higher feh value to the target parameter
    closest_tefflow_logglow_fehhigh_models = _get_closest_models(
        "feh", target_parameters["feh"], tefflow_logglow_fehhigh_models
    )

    # From the subset of models with the closest lower Teff value, get the models with a logg value greater than the target parameter
    tefflow_logghigh_models = _get_models_with_higher_parameter(
        "logg", target_parameters["logg"], closest_tefflow_models
    )
    # Get the models that have the closest higher logg value to the target parameter
    closest_tefflow_logghigh_models = _get_closest_models(
        "logg", target_parameters["logg"], tefflow_logghigh_models
    )

    # From the subset of models with the closest lower Teff value and higher logg value, get the models with a feh value less than the target parameter
    tefflow_logghigh_fehlow_models = _get_models_with_lower_parameter(
        "feh", target_parameters["feh"], closest_tefflow_logghigh_models
    )
    # Get the models that have the closest lower feh value to the target parameter
    closest_tefflow_logghigh_fehlow_models = _get_closest_models(
        "feh", target_parameters["feh"], tefflow_logghigh_fehlow_models
    )

    # From the subset of models with the closest lower Teff value and higher logg value, get the models with a feh value greater than the target parameter
    tefflow_logghigh_fehhigh_models = _get_models_with_higher_parameter(
        "feh", target_parameters["feh"], closest_tefflow_logghigh_models
    )
    # Get the models that have the closest higher feh value to the target parameter
    closest_tefflow_logghigh_fehhigh_models = _get_closest_models(
        "feh", target_parameters["feh"], tefflow_logghigh_fehhigh_models
    )

    # Get all models with higher Teff value than the target
    teffhigh_models = _get_models_with_higher_parameter(
        "teff", target_parameters["teff"], model_grid
    )
    # Get the models that have the closest higher Teff value to the target parameter
    closest_teffhigh_models = _get_closest_models(
        "teff", target_parameters["teff"], teffhigh_models
    )

    # From the subset of models with the closest higher Teff value, get the models with a logg value less than the target parameter
    teffhigh_logglow_models = _get_models_with_lower_parameter(
        "logg", target_parameters["logg"], closest_teffhigh_models
    )
    # Get the models that have the closest lower logg value to the target parameter
    closest_teffhigh_logglow_models = _get_closest_models(
        "logg", target_parameters["logg"], teffhigh_logglow_models
    )

    # From the subset of models with the closest higher Teff and lower logg value, get the models with a feh value less than the target parameter
    teffhigh_logglow_fehlow_models = _get_models_with_lower_parameter(
        "feh", target_parameters["feh"], closest_teffhigh_logglow_models
    )
    # Get the models that have the closest lower feh value to the target parameter
    closest_teffhigh_logglow_fehlow_models = _get_closest_models(
        "feh", target_parameters["feh"], teffhigh_logglow_fehlow_models
    )

    # From the subset of models with the closest higher Teff and lower logg values, get the models with a feh value greater than the target parameter
    teffhigh_logglow_fehhigh_models = _get_models_with_higher_parameter(
        "feh", target_parameters["feh"], closest_teffhigh_logglow_models
    )
    # Get the models that have the closest higher feh value to the target parameter
    closest_teffhigh_logglow_fehhigh_models = _get_closest_models(
        "feh", target_parameters["feh"], teffhigh_logglow_fehhigh_models
    )

    # From the subset of models with the closest higher Teff value, get the models with a logg value greater than the target parameter
    teffhigh_logghigh_models = _get_models_with_higher_parameter(
        "logg", target_parameters["logg"], closest_teffhigh_models
    )
    # Get the models that have the closest higher logg value to the target parameter
    closest_teffhigh_logghigh_models = _get_closest_models(
        "logg", target_parameters["logg"], teffhigh_logghigh_models
    )

    # From the subset of models with the closest higher Teff and higher logg values, get the models with a feh value less than the target parameter
    teffhigh_logghigh_fehlow_models = _get_models_with_lower_parameter(
        "feh", target_parameters["feh"], closest_teffhigh_logghigh_models
    )
    # Get the models that have the closest lower feh value to the target parameter
    closest_teffhigh_logghigh_fehlow_models = _get_closest_models(
        "feh", target_parameters["feh"], teffhigh_logghigh_fehlow_models
    )

    # From the subset of models with the closest higher Teff and higher logg values, get the models with a feh value greater than the target parameter
    teffhigh_logghigh_fehhigh_models = _get_models_with_higher_parameter(
        "feh", target_parameters["feh"], closest_teffhigh_logghigh_models
    )
    # Get the models that have the closest higher feh value to the target parameter
    closest_teffhigh_logghigh_fehhigh_models = _get_closest_models(
        "feh", target_parameters["feh"], teffhigh_logghigh_fehhigh_models
    )

    # Gets the first model in every subset # TODO: Is this correct logic?
    model1 = closest_tefflow_logglow_fehlow_models.iloc[0]
    model2 = closest_tefflow_logglow_fehhigh_models.iloc[0]
    model3 = closest_tefflow_logghigh_fehlow_models.iloc[0]
    model4 = closest_tefflow_logghigh_fehhigh_models.iloc[0]
    model5 = closest_teffhigh_logglow_fehlow_models.iloc[0]
    model6 = closest_teffhigh_logglow_fehhigh_models.iloc[0]
    model7 = closest_teffhigh_logghigh_fehlow_models.iloc[0]
    model8 = closest_teffhigh_logghigh_fehhigh_models.iloc[0]

    return [model1, model2, model3, model4, model5, model6, model7, model8]


def _needs_interpolation(stellar_parameters: dict, model_grid: pd.DataFrame):
    """
    Check if the model atmosphere needs to be interpolated
    """
    matches = model_grid[
        (model_grid["teff"] == stellar_parameters["teff"])
        & (model_grid["logg"] == stellar_parameters["logg"])
        & (model_grid["feh"] == stellar_parameters["feh"])
    ]
    if matches.empty:
        return True, None
    else:
        return False, matches


def _get_models_for_interpolation(model_directory: str, stellar_parameters: dict):
    """
    Get the files needed for interpolation
    """
    # Parse filenames to get the parameters
    all_models = _extract_parameters_from_filenames(model_directory)
    # Create a DataFrame from the models
    model_grid = _create_model_grid(all_models)
    # Get the bracketing models
    bracketing_models = _find_bracketing_models(stellar_parameters, model_grid)
    return bracketing_models


def create_template_interpolator_script(config: Configuration):
    """
    Create a template script for the interpolator. Should be called just once per program run
    The things changed from original script are:
    - the model_path and modele_out are set by placeholders
    - the interpolation values are set by placeholders
    - some comments have been removed
    """
    template_script_path = f"{config.path_interpolator}/interpolate.script"

    script_content = r"""#!/bin/csh -f
set model_path = {{PY_MODEL_PATH}}

set marcs_binary = '.false.'
#set marcs_binary = '.true.'

#enter here the values requested for the interpolated model 
foreach Tref   ( {{PY_TREF}} )
foreach loggref ( {{PY_LOGGREF}} )
foreach zref ( {{PY_ZREF}} )
set modele_out = {{PY_OUTPUT_PATH}}/${Tref}g${loggref}z${zref}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/${Tref}g${loggref}z${zref}.alt

# grid values bracketting the interpolation point (should be automatised!)
set Tefflow = {{PY_TEFFLOW}}
set Teffup  = {{PY_TEFFUP}}
set logglow = {{PY_LOGGLOW}}
set loggup  = {{PY_LOGGUP}}
set zlow    = {{PY_FEHLOW}}
set zup     = {{PY_FEHUP}}
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
    with open(template_script_path, "w") as file:
        file.write(script_content)


def remove_template_interpolator_script(config: Configuration):
    """
    Remove the template interpolator script
    """
    template_script_path = f"{config.path_interpolator}/interpolate.script"
    os.remove(template_script_path)  # TODO: Add error handling


def copy_template_interpolator_script(config: Configuration, stellar_parameters: dict):
    """
    Copy the template interpolator script with a unique file name
    """
    unique_filename = f"interpolate_{stellar_parameters['teff']}_{stellar_parameters['logg']}_{stellar_parameters['feh']}.script"
    path_to_new_script = f"{config.path_interpolator}/{unique_filename}"

    shutil.copyfile(
        f"{config.path_interpolator}/interpolate.script", path_to_new_script
    )
    return unique_filename


def _update_interpolator_script(
    script_name: str, input_parameters: dict, models: list, config: Configuration
):
    """
    Update the interpolator script with the correct model paths and interpolation values
    """
    script_path = f"{config.path_interpolator}/{script_name}"
    with open(script_path, "r") as file:
        script_content = file.read()
    # if float(models[0]["logg"]) >= 0:
    #     models[0]["logg"] = f"+{models[0]['logg']}"
    # if float(models[7]["logg"]) >= 0:
    #     models[7]["logg"] = f"+{models[7]['logg']}"
    # if float(models[0]["feh"]) >= 0:
    #     models[0]["feh"] = f"+{models[0]['feh']}"
    # if float(models[7]["feh"]) >= 0:
    #     models[7]["feh"] = f"+{models[7]['feh']}"

    # Update the script with the correct model paths and interpolation values
    updates = {
        "MODEL_PATH": config.path_model_atmospheres,
        "TREF": input_parameters["teff"],
        "LOGGREF": input_parameters["logg"],
        "ZREF": input_parameters["feh"],
        "OUTPUT_PATH": config.path_output_directory,
        "TEFFLOW": models[0]["teff"],
        "TEFFUP": models[7]["teff"],
        "LOGGLOW": models[0]["logg"],
        "LOGGUP": models[7]["logg"],
        "FEHLOW": models[0]["feh"],
        "FEHUP": models[7]["feh"],
    }

    for update, value in updates.items():
        script_content = script_content.replace(f"{{{{PY_{update}}}}}", str(value))
    with open(script_path, "w") as file:
        file.write(script_content)


def _run_interpolation_script(script_name: str, config: Configuration):
    """
    Run the interpolation script
    """
    # Run the interpolation script
    original_directory = os.getcwd()
    os.chdir(config.path_interpolator)
    command = f"./{script_name}"
    try:
        subprocess.run(["chmod", "+x", script_name], check=True)
        result = subprocess.run([command], check=True, text=True, capture_output=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error running interpolation script: {e.stderr}")
        raise e
    finally:
        # Change back to the original working directory
        os.chdir(original_directory)


def generate_interpolated_model_atmosphere(
    config: Configuration, input_parameters: dict
):
    """
    Interpolate a model atmosphere
    """
    # Get files needed for interpolation. 8 MARCS files are needed (look in readme)
    bracketing_models = _get_models_for_interpolation(
        config.path_model_atmospheres, input_parameters
    )
    # Update script with model information
    interpolator_script_name = copy_template_interpolator_script(
        config, input_parameters
    )
    print(f"interpolator_script_name: {interpolator_script_name}")
    _update_interpolator_script(
        interpolator_script_name,
        input_parameters,
        bracketing_models,
        config,
    )
    # Run interpolation script
    _run_interpolation_script(interpolator_script_name, config)
    # TODO: Remove interpolation script
    # TODO: Set filepaths in config object


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


def run_babsma(config: Configuration):
    """
    Run babsma
    """
    pass


def generate_bsyn(config: Configuration, input_parameters: dict):
    """
    Generate the bsyn file
    """
    pass


def run_bsyn(config: Configuration):
    """
    Run bsyn
    """
    pass


def generate_one_spectrum(config: Configuration, input_parameters: dict):
    """
    Generates a spectrum for a set of input parameters.
    """
    # TODO: Check if model atmosphere needs to be interpolated
    # TODO: Generate interpolated model atmosphere

    # TODO: Generate babsma
    # TODO: Run babsma

    # TODO: Generate bsyn
    # TODO: Run bsyn

    # TODO: Save spectrum

    pass


def generate_all_spectra(config: Configuration):
    # TODO: Compile Turbospectrum
    # TODO: Compile interpolator
    # TODO: Set up output directory
    # TODO: Generate one spectra for each set of input parameters
    pass


if __name__ == "__main__":
    config = Configuration()
    output_management.set_up_output_directory(config)
    generate_all_spectra(config)
