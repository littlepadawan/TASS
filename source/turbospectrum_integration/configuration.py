from os import chdir, getcwd, listdir, path
from subprocess import PIPE, run

from source.configuration_setup import Configuration
from source.turbospectrum_integration.utils import compose_filename

# String templates for BABSMA and BSYN configuration files
# Placeholders are replaced with actual values during runtime
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
{abundances}
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
{abundances}
{line_lists}
SPHERICAL: .false.
30
300.00
15
1.30
"""


class TurbospectrumConfiguration:

    def __init__(self, config: Configuration, stellar_parameters: dict):
        self.alpha = calculate_alpha(stellar_parameters["z"])
        self.file_name = compose_filename(stellar_parameters, self.alpha)

        self.path_model_atmosphere = None
        self.path_model_opac = (
            f"{config.path_output_directory}/temp/opac_{self.file_name}"
        )
        self.path_babsma = (
            f"{config.path_output_directory}/temp/{self.file_name}_babsma"
        )
        self.path_bsyn = f"{config.path_output_directory}/temp/{self.file_name}_bsyn"
        self.path_result = f"{config.path_output_directory}/{self.file_name}.spec"
        self.interpolated_model_atmosphere = True

        set_abundances(self, stellar_parameters)


def calculate_alpha(metallicity: float):
    """
    Calculate the alpha enhancement based on the metallicity.

    Args:
        metallicity (float): Metallicity

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


def generate_abundance_str(stellar_parameters: dict):
    """
    Generate abundance string used in the babsma and bsyn scripts.

    The function converts the relative values of the abundances of
    Mg and Ca to absolute values, and formats it to a string to use
    in the babsma and bsyn scripts under the line "INDIVIDUAL ABUNDANCES".
    The function assumes that the metallicity (Fe/H) is stored in the dictionary
    stellar_parameters as value to the key "z".
    Args:
        stellar_parameters (dict): The stellar parameters containing the abundances of Mg and Ca
    Returns:
        int: Number of elements
        str: abundance string
    """
    # Element numbers and solar abundances for Mg and Ca
    # Reference: photospheric abundances from Magg+ 2022A&A...661A.140M
    elements = {
        "mg": {"element_number": 12, "solar_abundance": 7.55},
        "ca": {"element_number": 20, "solar_abundance": 6.37},
    }

    num_abundances = 0
    abundance_lines = []

    # Get the metallicity
    metallicity = stellar_parameters["z"]

    # Iterate over the elements
    for element, data in elements.items():
        # Get the relative abundance of the current element
        relative_abundance = stellar_parameters.get(element)
        if relative_abundance is not None:
            element_number = data["element_number"]
            solar_abundance = data["solar_abundance"]

            # Convert relative abundance to absolute abundance
            absolute_abundance = solar_abundance + metallicity + relative_abundance
            # Create line with the element number and the absolute abundance
            abundance_lines.append(f"{element_number} {absolute_abundance:.2f}")
            num_abundances += 1

    # Start the abundance string with the keyword required by the scripts, followed by the number of elements
    abundance_str = f"'INDIVIDUAL ABUNDANCES:' {num_abundances}\n"
    # Add the lines with the absolute abundances
    abundance_str += "\n".join(abundance_lines)

    return num_abundances, abundance_str


def set_abundances(ts_config: TurbospectrumConfiguration, stellar_parameters: dict):
    """
    Set the number of elements and the abundance string in the Turbospectrum configuration.

    A wrapper function that calls generate_abundance_str and sets the values in the Turbospectrum configuration.

    Args:
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration
        stellar_parameters (dict): The stellar parameters containing the abundances

    Side effects:
        Sets the number of elements and the abundance string in the Turbospectrum configuration.
    """
    num_elements, abundance_str = generate_abundance_str(stellar_parameters)

    ts_config.num_elements = num_elements
    ts_config.abundance_str = abundance_str


def is_model_atmosphere_marcs(ts_config: TurbospectrumConfiguration):
    """
    Check if the model atmosphere is a MARCS model.

    The function checks an attribute of the Turbospectrum configuration and
    returns a corresponding string to use in the babsma script.
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
    Create the babsma script.

    Replaces placeholders in the BABSMA_CONTENT variable with actual values
    and creates the script.
    Args:
        config (Configuration): The Configuration object
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration object
        stellar_parameters (dict): The stellar parameters
    """
    # Replace placeholders in BABSMA_CONTENT with values from config, ts_config,
    # and stellar_parameters
    babsma_config = BABSMA_CONTENT.format(
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_input=ts_config.path_model_atmosphere,
        marcs_file=is_model_atmosphere_marcs(ts_config),
        model_opac=ts_config.path_model_opac,
        metallicity=stellar_parameters["z"],
        alpha=ts_config.alpha,
        abundances=ts_config.abundance_str,
        xifix=config.xit,
    )

    # Write babsma_config to a file
    with open(ts_config.path_babsma, "w") as file:
        file.write(babsma_config)


def create_line_lists_str(config: Configuration):
    """
    Create a string with the paths to the line lists.

    Args:
        config (Configuration): The Configuration object containing the path to the directory
        with the line lists.

    Returns:
        str: A string with the paths to the line lists, separated by newlines.
    """
    # TODO: Add error handling? What if the directory is empty? Or contains other files than line lists?
    directory = config.path_linelists
    # Gather all file paths in the directory into a list
    line_list_paths = [
        path.join(directory, file)
        for file in listdir(directory)
        if path.isfile(path.join(directory, file))
    ]

    # Format the list as a string containing the keyword needed for the bsyn script,
    # with each path on a new line
    line_lists_str = "NFILES: {:d}".format(len(line_list_paths))
    for file in line_list_paths:
        line_lists_str += "\n{}".format(file)

    line_lists_str += "\n"

    return line_lists_str


def create_bsyn(
    config: Configuration,
    ts_config: TurbospectrumConfiguration,
    stellar_parameters: dict,
):
    """
    Create the bsyn script.

    Replaces placeholders in the BSYN_CONTENT variable with actual values
    and creates the script.
    Args:
        config (Configuration): The Configuration object
        ts_config (TurbospectrumConfiguration): The Turbospectrum configuration object
        stellar_parameters (dict): The stellar parameters
    """
    # Replace placeholders in BSYN_CONTENT with values from config, ts_config, and stellar_parameters
    bsyn_config = BSYN_CONTENT.format(
        lambda_min=config.wavelength_min,
        lambda_max=config.wavelength_max,
        lambda_step=config.wavelength_step,
        model_opac=ts_config.path_model_opac,
        result_file=ts_config.path_result,
        metallicity=stellar_parameters["z"],
        alpha=ts_config.alpha,
        abundances=ts_config.abundance_str,
        line_lists=create_line_lists_str(config),
    )

    # Write the configuration to a file
    with open(ts_config.path_bsyn, "w") as file:
        file.write(bsyn_config)
