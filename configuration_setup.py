from configparser import ConfigParser
import os


class Configuration:
    """
    Represents the configuration settings for the Turbospectrum wrapper.

    Attributes:
        config_file (str): The absolute path to the configuration file.
        config_parser (ConfigParser): The configuration parser object.
        compiler (str): The TurboSpectrum compiler.
        path_turbospectrum (str): The absolute path to the TurboSpectrum directory.
        path_turbospectrum_compiled (str): The absolute path to the compiled TurboSpectrum executable.
        path_linelists (str): The absolute path to the linelists directory.
        path_model_atmospheres (str): The absolute path to the model atmospheres directory.
        path_input_parameters (str): The absolute path to the input parameters file.
        path_output_directory (str): The absolute path to the output directory.
        wavelength_min (float): The minimum wavelength in Å.
        wavelength_max (float): The maximum wavelength in Å.
        wavelength_step (float): The wavelength step.
    """

    def __init__(self, config_path="input/configuration.cfg"):
        self.config_file = os.path.abspath(config_path)
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"The config file {self.config_file} does not exist."
            )

        # TODO: Better to initiate to None or to default values?
        self.compiler = None
        self.path_turbospectrum = None
        self.path_turbospectrum_compiled = None
        self.path_linelists = None
        self.path_model_atmospheres = None
        self.path_input_parameters = None
        self.path_output_directory = None

        self.wavelength_min = 0
        self.wavelength_max = 0
        self.wavelength_step = 0

        self._load_configuration_file()
        self._validate_configuration()

    def _load_configuration_file(self):
        # Read configuration file
        config_parser = ConfigParser()
        config_parser.read(self.config_file)

        # Set configuration parameters found in the configuration file
        # Parameters in the configuration file must be explicity set here,
        # so if you add something to the configuration file, you must also add it here,
        # otherwise it will not be recognized by the program.
        self.compiler = config_parser.get("Turbospectrum_compiler", "compiler").lower()

        self.path_turbospectrum = os.path.abspath(
            config_parser.get("Paths", "turbospectrum")
        )
        self.path_linelists = os.path.abspath(config_parser.get("Paths", "linelists"))
        self.path_model_atmospheres = os.path.abspath(
            config_parser.get("Paths", "model_atmospheres")
        )
        self.path_input_parameters = os.path.abspath(
            config_parser.get("Paths", "input_parameters")
        )
        self.path_output_directory = os.path.abspath(
            config_parser.get("Paths", "output_directory")
        )

        self.wavelength_min = config_parser.getfloat(
            "Atmosphere_parameters", "wavelength_min"
        )
        self.wavelength_max = config_parser.getfloat(
            "Atmosphere_parameters", "wavelength_max"
        )
        self.wavelength_step = config_parser.getfloat(
            "Atmosphere_parameters", "wavelength_step"
        )

    def _validate_configuration(self):
        # TODO: Improve error messages so user knows how to fix them
        """
        Check that all required parameters are set and within range
        """
        # Turbospectrum path
        if not os.path.exists(self.path_turbospectrum):
            raise FileNotFoundError(
                f"The specified directory containing Turbospectrum {self.config_file} does not exist."
            )

        # Compiler
        if self.compiler == "intel":
            self.path_turbospectrum_compiled = os.path.join(
                self.path_turbospectrum, "exec"
            )
        elif self.compiler == "gfortran":
            self.path_turbospectrum_compiled = os.path.join(
                self.path_turbospectrum, "exec-gf"
            )
        else:
            raise ValueError(f"Compiler {self.compiler} is not supported.")

        # Paths - directories
        paths_dir = [
            self.path_linelists,
            self.path_model_atmospheres,
            self.path_output_directory,
        ]
        for path in paths_dir:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"The specified directory {path} does not exist."
                )

        # Paths - files
        paths_files = [self.path_input_parameters]
        for path in paths_files:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"The specified file {path} does not exist.")

        # Wavelength range
        if self.wavelength_min >= self.wavelength_max:
            raise ValueError(
                f"The minimum wavelength {self.wavelength_min} must be smaller than the maximum wavelength {self.wavelength_max}."
            )

        if (
            self.wavelength_min < 0
            or self.wavelength_max < 0
            or self.wavelength_step <= 0
        ):
            raise ValueError(f"The wavelength parameters must be positive.")
