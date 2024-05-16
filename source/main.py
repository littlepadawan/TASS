import logging

from configuration_setup import Configuration
from output_management import (
    copy_config_file,
    remove_temp_files,
    set_up_output_directory,
)
from parameter_generation import generate_parameters
from turbospectrum_integration.compilation import (
    compile_interpolator,
    compile_turbospectrum,
)
from turbospectrum_integration.interpolation import create_template_interpolator_script
from turbospectrum_integration.run_turbospectrum import generate_all_spectra
from turbospectrum_integration.utils import collect_model_atmosphere_parameters


def main():
    # TODO: Add functionality to read path from commandline
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize configuration
        config = Configuration()

        # Set up output directory
        set_up_output_directory(config)

        # Copy configuration file to output directory for reference
        copy_config_file(config)

        # Load model atmospheres
        model_atmospheres = collect_model_atmosphere_parameters(
            config.path_model_atmospheres
        )

        # Generate stellar parameters
        stellar_parameters = generate_parameters(config)

        # Compile Turbospectrum and interpolator
        compile_turbospectrum(config)
        compile_interpolator(config)

        # Create template for interpolator script
        create_template_interpolator_script(config)
    except Exception as e:
        logging.error(f"Error during setup: {e}")
        raise e

    # Generate all spectra
    generate_all_spectra(config, model_atmospheres, stellar_parameters)

    # Remove temporary files
    # Toggle this if you want to access scipts and intermediate files used in the process
    # remove_temp_files(config)


if __name__ == "__main__":
    main()
