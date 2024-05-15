from os import chdir, getcwd, listdir, path
from subprocess import PIPE, run

from source.configuration_setup import Configuration

# String templates for BABSMA and BSYN configuration files
# Placeholders are replaced with actual values in functions below
BABSMA_CONTENT = """
PURE-LTE: .true.
LAMBDA_MIN: {lambda_min:.0f}
LAMBDA_MAX: {lambda_max:.0f}
LAMBDA_STEP: {lambda_step:.2f}
MODELINPUT: '{model_input}'
MARCS-FILE: {marcs_file}
MODELOPAC: '{model_opac}'
METALLICITY: {metallicity:.2f}
'ALPHA/Fe:' {alpha:.2f}
'INDIVIDUAL ABUNDANCES:' {num_elements:.0f}
'{abundance_str}'
XIFIX: T
{xifix:.1f}
"""

BSYN_CONTENT = """
PURE-LTE: .true.
SEGMENTSFILE: ''
LAMBDA_MIN: {lambda_min:.0f}
LAMBDA_MAX: {lambda_max:.0f}
LAMBDA_STEP: {lambda_step:.2f}
'INTENSITY/FLUX:' 'Flux'
ABFIND: .false.
MODELOPAC: '{model_opac}'
RESULTFILE: '{result_file}'
METALLICITY: {metallicity:.2f}
'ALPHA/Fe:' {alpha:.2f}
'INDIVIDUAL ABUNDANCES:' {num_elements:.0f}
'{abundance_str}'
'{line_lists}'
SPHERICAL: .false.
"""


class TurbospectrumConfiguration:

    def __init__(self, config: Configuration, stellar_parameters: dict):
        self.path_model_atmosphere = None
        self.path_model_opac = None
        self.path_babsma = f"{config.path_output_directory}/temp/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}_babsma"  # TODO: Update with Mg and Ca
        self.path_bsyn = f"{config.path_output_directory}/temp/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}_bsyn"  # TODO: Update with Mg and Ca
        self.interpolated_model_atmosphere = True
        self.alpha = calculate_alpha(stellar_parameters["z"])
        self.num_elements = 0
        self.abundance_str = ""

        # set_abundances(self, stellar_parameters) # TODO: Implement when abundances has been added


def calculate_alpha(metallicity: float):
    """
    Calculate the alpha enhancement based on the metallicity.

    Args:
        metallicity (float): The metallicity

    Returns:
        float: The alpha enhancement
    """
    if metallicity < -1.0:
        alpha = 0.4
    elif -1.0 <= metallicity < 0.0:
        alpha = -0.4 * metallicity
    else:
        alpha = 0.0
    return alpha


def generate_path_model_opac(
    ts_config: TurbospectrumConfiguration,
    config: Configuration,
    stellar_parameters: dict,
):
    """
    Generate the path to the model opac file and set it in the Turbospectrum configuration.

    Args:
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration
        config (Configuration): The configuration
        stellar_parameters (dict): The stellar parameters
    """
    ts_config.path_model_opac = f"{config.path_output_directory}/temp/opac_p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}"


def generate_path_result_file(
    ts_config: TurbospectrumConfiguration,
    config: Configuration,
    stellar_parameters: dict,
):
    """
    Generate the path to the result file and set it in the Turbospectrum configuration.

    Args:
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration
        config (Configuration): The Configuration object containing path to the output directory.
        stellar_parameters (dict): The stellar parameters
    """
    # TODO: Update with Mg and Ca
    # TODO: Make sure this has the right format (follow TSFitPy? All params should be deducable from filename, and have + and -)
    ts_config.path_result_file = f"{config.path_output_directory}/p{stellar_parameters['teff']}_g{stellar_parameters['logg']}_z{stellar_parameters['z']}.spec"


def generate_abundance_str(stellar_parameters: dict):
    """
    Generate formatted abundance string used in the configuration.

    Args:
        stellar_parameters (dict): The stellar parameters
    Returns:
        tuple: The number of elements and the abundance string
    """
    abundance_str = ""
    element_numbers = {
        "Mg": 12,
        "Ca": 20,
    }

    # TODO: Values need convesion from relative to absolute (given by Ulrike)
    # TODO: Fråga Ulrike - ska man ta det konverterade värdet + alpha?
    # TODO: Error handling - what if element is not in stellar_parameters?
    num_abundances = 0
    for element, element_number in element_numbers.items():
        abundance = stellar_parameters.get(element)
        if abundance is not None:
            abundance_str += f"{element_number}  {abundance:.2f}\n"
            num_abundances += 1

    return num_abundances, abundance_str


def set_abundances(ts_config: TurbospectrumConfiguration, stellar_parameters: dict):
    """
    Set the number of elements and the abundance string in the Turbospectrum configuration.

    Args:
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration
        stellar_parameters (dict): The stellar parameters containing the abundances
    """
    num_elements, abundance_str = generate_abundance_str(stellar_parameters)
    ts_config.num_elements = num_elements
    ts_config.abundance_str = abundance_str


def is_model_atmosphere_marcs(ts_config: TurbospectrumConfiguration):
    """
    Check if the model atmosphere is a MARCS model.

    Args:
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration

    Returns:
        str: ".true." if the model atmosphere is a MARCS model,
        ".false." if the model atmosphere has been generated by interpolation.
    """
    if ts_config.interpolated_model_atmosphere:
        # If the model atmosphere has been interpolated, it is not a MARCS model
        return ".false."
    else:
        # Otherwise, it means an existing MARCS model is used
        return ".true."


def create_babsma(
    config: Configuration,
    ts_config: TurbospectrumConfiguration,
    stellar_parameters: dict,
):
    """
    Create the BABSMA configuration file.

    Replaces placeholders in the BABSMA_CONTENT template with actual values
    and creates the script.
    Args:
        config (Configuration): The Configuration
        ts_config (TurbospectrumConfiguration): _description_
        stellar_parameters (dict): _description_
    """
    # TODO: This should be removed eventually, since these values are set in ts_config
    num_elements, abundance_str = generate_abundance_str(stellar_parameters)

    babsma_config = BABSMA_CONTENT.format(
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_input=ts_config.path_model_atmosphere,
        marcs_file=is_model_atmosphere_marcs(ts_config),
        model_opac=ts_config.path_model_opac,
        metallicity=stellar_parameters["z"],
        alpha=ts_config.alpha,
        num_elements=num_elements,
        abundance_str=abundance_str,
        xifix=config.xit,
    )

    with open(ts_config.path_babsma, "w") as file:
        file.write(babsma_config)


def create_line_lists_str(config: Configuration):
    """
    Create a string with the paths to the line lists.

    Args:
        config (Configuration): The Configuration object containing the path to the directory
        with the line lists.

    Returns:
        str: The string with the paths to the line lists separated by newlines.
    """
    # TODO: Add error handling? What if the directory is empty?
    directory = config.path_linelists
    # Gather all file paths in the directory into a list
    line_list_paths = [
        path.join(directory, file)
        for file in listdir(directory)
        if path.isfile(path.join(directory, file))
    ]

    # Format the list as a string containing the keyword needed for the bsyn script,
    # with each path on a new line
    line_lists_str = "'NFILES   :' '{:d}'\n".format(len(line_list_paths))
    for file in line_list_paths:
        line_lists_str += "{}\n".format(file)

    return line_lists_str


def create_bsyn(
    config: Configuration,
    ts_config: TurbospectrumConfiguration,
    stellar_parameters: dict,
):
    """
    Create the BSYN configuration file.

    Args:
        config (Configuration): The Configuration object
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration object
        stellar_parameters (dict): The stellar parameters
    """
    bsyn_config = BSYN_CONTENT.format(
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_opac=ts_config.path_model_opac,
        result_file=ts_config.path_result_file,
        metallicity=stellar_parameters["z"],
        alpha=ts_config.alpha,
        num_elements=ts_config.num_elements,
        abundance_str=ts_config.abundance_str,
        line_lists=create_line_lists_str(config),
    )

    with open(ts_config.path_bsyn, "w") as file:
        file.write(bsyn_config)
