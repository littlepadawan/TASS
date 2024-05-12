import os  # TODO: Maybe dont import entire os module
import shutil
import subprocess  # TODO: Maybe dont import entire subprocess module
from decimal import Decimal
from string import Template

import numpy as np
import output_management
import pandas as pd
import turbospectrum_integration.turbospectrum_integration as turbospectrum_integration
from configuration_setup import Configuration


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
set modele_out = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/p${Tref}_g${loggref}_z${zref}.alt

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
    unique_filename = f"interpolate_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}.script"
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
        # print(result)
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
    # print(f"interpolator_script_name: {interpolator_script_name}")
    _update_interpolator_script(
        interpolator_script_name,
        input_parameters,
        bracketing_models,
        config,
    )
    # Run interpolation script
    _run_interpolation_script(interpolator_script_name, config)
    # TODO: Remove interpolation script

    # Return filepath to model atmosphere
    return f"{config.path_output_directory}/p{input_parameters['teff']}_g{input_parameters['logg']}_z{input_parameters['feh']}.interpol"


def generate_abundance_string(elements, base_abundance, adjustments):
    # Generates formatted abundance strings for the config
    abundances = "'INDIVIDUAL ABUNDANCES:'\n"
    for element, base in base_abundance.items():
        adjusted = base + adjustments.get(element, 0)
        abundances += f"{element}  {adjusted:.6f}\n"
    return abundances


def generate_default_alpha(metallicity: float):
    # THis is how TSFitPy calculates the alpha value
    alpha = 0.0
    if metallicity < -1.0:
        alpha = 0.4
    elif -1.0 <= metallicity < 0.0:
        alpha = -0.4 * metallicity
    else:
        alpha = 0.0
    return alpha


def generate_default_abundances(alpha: float):
    # This is how TSFitPy calculates the abundances
    # String to hold the abundances
    individual_abundances = "'INDIVIDUAL ABUNDANCES:'\n"
    element_numbers = {
        "H": 1,
        "He": 2,
        "O": 8,
        "Ne": 10,
        "Mg": 12,
        "Si": 14,
        "S": 16,
        "Ca": 20,
        "Fe": 26,
    }
    solar_abundances = {
        "H": 12.00,
        "He": 10.93,
        "O": 8.69,
        "Ne": 7.93,
        "Mg": 7.60,
        "Si": 7.51,
        "S": 7.12,
        "Ca": 6.34,
        "Fe": 7.50,
    }
    for element, element_number in element_numbers.items():
        abundance = solar_abundances[element] + (
            alpha if element in ["O", "Ne", "Mg", "Si", "S", "Ca"] else 0
        )  # Apply alpha enhancement to alpha elements
        individual_abundances += f"{element_number}  {abundance:.2f}\n"

    return individual_abundances


def create_babsma(config: Configuration, stellar_parameters: dict, model_path: str):
    """
    Create the babsma file
    """
    babsma_template = """
PURE-LTE: .true.
LAMBDA_MIN: {lambda_min:.0f}
LAMBDA_MAX: {lambda_max:.0f}
LAMBDA_STEP: {lambda_step:.2f}
MODELINPUT: '{model_input}'
MARCS-FILE: .false.
MODELOPAC: '{model_opac}'
METALLICITY: {metallicity:.2f}
'ALPHA/Fe:' {alpha:.2f}
HELIUM: 0.00
R-PROCESS: 0.00
S-PROCESS: 0.00
'INDIVIDUAL ABUNDANCES:' 0
XIFIX: T
1.5
"""
    alpha_def = generate_default_alpha(stellar_parameters["feh"])
    # abundances_str = generate_default_abundances(alpha)

    # Fill the templates
    babsma_config = babsma_template.format(
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_input=model_path,
        model_opac=f"{config.path_output_directory}/opac_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}",
        metallicity=stellar_parameters["feh"],
        alpha=alpha_def,
    )

    babsma_file_path = f"{config.path_output_directory}/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}_babsma"  # TODO: Should be unique

    with open(babsma_file_path, "w") as file:
        file.write(babsma_config)
    return babsma_file_path


def run_babsma(config: Configuration, babsma_file_path: str):
    """
    Run babsma
    """
    babsma_executable = f"{config.path_turbospectrum_compiled}/babsma_lu"
    cwd = os.getcwd()
    os.chdir(
        config.path_turbospectrum
    )  # Change to directory where babsma is expected to run
    # Make sure the configuration file is executable (TODO REMOVE?)
    subprocess.run(["chmod", "+x", babsma_file_path], check=True)
    with open(babsma_file_path, "r") as file:
        result = subprocess.run(
            [babsma_executable],
            stdin=file,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if result.returncode != 0:
        print(f"Error running babsma: {result.stderr}")
    os.chdir(cwd)


def create_bsyn(config: Configuration, stellar_parameters: dict):
    """
    Generate the bsyn file
    """
    bsyn_template = """
PURE-LTE: .true.
SEGMENTSFILE: ''
LAMBDA_MIN: {lambda_min:.0f}
LAMBDA_MAX: {lambda_max:.0f}
LAMBDA_STEP: {lambda_step:.2f}
'INTENSITY/FLUX:' 'Flux'
'COS(THETA):' 1.00
ABFIND: .false.
MODELOPAC: '{model_opac}'
RESULTFILE: '{result_file}'
METALLICITY: {metallicity:.2f}
'ALPHA/Fe:' {alpha:.2f}
HELIUM: 0.00
R-PROCESS: 0.00
S-PROCESS: 0.00
'INDIVIDUAL ABUNDANCES:' 0
ISOTOPES: 0
'{line_lists}'
SPHERICAL: .false.
"""
    alpha_def = generate_default_alpha(stellar_parameters["feh"])
    # Make a list of line lists
    directory = config.path_linelists
    line_list_paths = [
        os.path.join(directory, file)
        for file in directory
        if os.path.isfile(os.path.join(directory, file))
    ]
    # Convert to string for script
    line_lists = "'NFILES   :' '{:d}'\n".format(len(line_list_paths))
    for file in line_list_paths:
        line_lists += "{}\n".format(file)
    opac_model_path = f"{config.path_output_directory}/opac_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}"
    result_file_path = f"{config.path_output_directory}/spectrum_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}"
    bsyn_config = bsyn_template.format(
        pure_lte=".true.",
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_opac=opac_model_path,
        result_file=result_file_path,
        metallicity=stellar_parameters["feh"],
        alpha=alpha_def,
        helium=0.00,
        r_process=0.00,
        s_process=0.00,
        line_lists="\n".join(line_list_paths),
    )

    bsyn_file_path = f"{config.path_output_directory}/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['feh']}_bsyn"

    with open(bsyn_file_path, "w") as file:
        file.write(bsyn_config)
    return bsyn_file_path


def run_bsyn(config: Configuration, bsyn_file_path: str):
    """
    Run bsyn
    """
    bsyn_executable = f"{config.path_turbospectrum_compiled}/bsyn_lu"
    cwd = os.getcwd()
    os.chdir(
        config.path_turbospectrum
    )  # Change to directory where bsyn is expected to run
    # Make sure the configuration file is executable (TODO REMOVE?)
    subprocess.run(["chmod", "+x", bsyn_file_path], check=True)
    with open(bsyn_file_path, "r") as file:
        result = subprocess.run(
            [bsyn_executable],
            stdin=file,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if result.returncode != 0:
        print(f"Error running bsyn: {result.stderr}")
    os.chdir(cwd)


def generate_one_spectrum(
    config: Configuration, input_parameters: dict, model_grid: pd.DataFrame
):
    """
    Generates a spectrum for a set of input parameters.
    """
    # TODO: Check if model atmosphere needs to be interpolated
    needs_interpolation, matching_models = _needs_interpolation(
        input_parameters, model_grid
    )
    # TODO: Generate interpolated model atmosphere
    if needs_interpolation:
        model_path = generate_interpolated_model_atmosphere(config, input_parameters)

    # TODO: Generate babsma
    babsma_file_path = create_babsma(config, input_parameters, model_path)
    # TODO: Run babsma
    run_babsma(config, babsma_file_path)

    # TODO: Generate bsyn
    bsyn_file_path = create_bsyn(config, input_parameters)
    # TODO: Run bsyn
    run_babsma(config, bsyn_file_path)

    # TODO: Save spectrum

    pass


def generate_all_spectra(config: Configuration):
    # TODO: Compile Turbospectrum
    compile_turbospectrum(config)
    # TODO: Compile interpolator
    compile_interpolator(config)
    # Read the model atmospheres

    # TODO: Set up output directory
    # TODO: Generate one spectra for each set of input parameters
    pass


if __name__ == "__main__":
    config = Configuration()
    output_management.set_up_output_directory(config)
    generate_all_spectra(config)
