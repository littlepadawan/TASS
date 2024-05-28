import os  # TODO: Is entire module needed?
import sys
from configparser import ConfigParser


# TODO: Add validation functions for turbospectrum settings
class Configuration:
    """
    Class to handle the configuration of the Turbospectrum wrapper.
    # TODO: Improve documenation
    """

    def __init__(self, config_path="input/configuration.cfg"):
        """
        Initialize the configuration object.

        Args:
            config_path (str, optional): The path to the configuration file to use. Defaults to "input/configuration.cfg".

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        self.config_file = os.path.abspath(config_path)
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"The config file {self.config_file} does not exist."
            )

        self.compiler = None
        self.path_turbospectrum = None
        self.path_turbospectrum_compiled = None
        self.path_interpolator = None
        self.path_linelists = None
        self.path_model_atmospheres = None
        self.path_input_parameters = None
        self.path_output_directory = None
        self.path_config = config_path

        self.wavelength_min = 0
        self.wavelength_max = 0
        self.wavelength_step = 0

        self.read_stellar_parameters_from_file = False
        self.random_parameters = True
        self.teff_min = 0
        self.teff_max = 0
        self.logg_min = 0
        self.logg_max = 0
        self.z_min = 0
        self.z_max = 0
        self.mg_min = 0
        self.mg_max = 0
        self.ca_min = 0
        self.ca_max = 0

        self.num_spectra = 0
        self.num_points_teff = 0
        self.num_points_logg = 0
        self.num_points_z = 0
        self.num_points_mg = 0
        self.num_points_ca = 0

        self.xit = 0

        self._load_configuration_file()
        try:
            self._validate_configuration()
        except (FileNotFoundError, ValueError) as e:
            print(e)
            sys.exit(1)

    def _load_configuration_file(self):
        """
        Load the configuration file and set the configuration parameters.

        Parameters in the configuration file must be explicity set in this function,
        meaning that additions to the configuration file will not be recognised by
        the program unless they are loaded by this function.

        Side effects: Sets the configuration parameters based on the configuration file.
        """
        # Read configuration file
        config_parser = ConfigParser()
        config_parser.read(self.config_file)

        # Set configuration parameters found in the configuration file
        self.compiler = config_parser.get("Turbospectrum_compiler", "compiler").lower()

        self.path_turbospectrum = os.path.abspath(
            config_parser.get("Paths", "turbospectrum")
        )
        self.path_interpolator = os.path.abspath(
            config_parser.get("Paths", "interpolator")
        )
        self.path_linelists = os.path.abspath(config_parser.get("Paths", "linelists"))
        self.path_model_atmospheres = os.path.abspath(
            config_parser.get("Paths", "model_atmospheres")
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

        self.read_stellar_parameters_from_file = config_parser.getboolean(
            "Stellar_parameters", "read_from_file"
        )

        # Only load these parameters if stellar parameters should be generated,
        # since they're not needed the stellar parameters are read from a file
        if self.read_stellar_parameters_from_file == False:
            self.random_parameters = config_parser.getboolean(
                "Stellar_parameters", "random_parameters"
            )
            self.teff_min = config_parser.getint("Stellar_parameters", "teff_min")
            self.teff_max = config_parser.getint("Stellar_parameters", "teff_max")
            self.logg_min = config_parser.getfloat("Stellar_parameters", "logg_min")
            self.logg_max = config_parser.getfloat("Stellar_parameters", "logg_max")
            self.z_min = config_parser.getfloat("Stellar_parameters", "z_min")
            self.z_max = config_parser.getfloat("Stellar_parameters", "z_max")
            self.mg_min = config_parser.getfloat("Stellar_parameters", "mg_min")
            self.mg_max = config_parser.getfloat("Stellar_parameters", "mg_max")
            self.ca_min = config_parser.getfloat("Stellar_parameters", "ca_min")
            self.ca_max = config_parser.getfloat("Stellar_parameters", "ca_max")

            # Load settings for parameter generation
            # If random parameters are specified, the number of sets to generate is needed
            if self.random_parameters == True:
                self.num_spectra = config_parser.getint(
                    "Random_settings", "num_spectra"
                )
            # If evenly spaced parameters are specified, the number of points for each parameter is needed
            else:
                self.num_points_teff = config_parser.getint(
                    "Even_settings", "num_points_teff"
                )
                self.num_points_logg = config_parser.getint(
                    "Even_settings", "num_points_logg"
                )
                self.num_points_z = config_parser.getint(
                    "Even_settings", "num_points_z"
                )
                self.num_points_mg = config_parser.getint(
                    "Even_settings", "num_points_mg"
                )
                self.num_points_ca = config_parser.getint(
                    "Even_settings", "num_points_ca"
                )
        else:
            self.path_input_parameters = os.path.abspath(
                config_parser.get("Paths", "input_parameters")
            )

        self.xit = config_parser.getfloat("Turbospectrum_settings", "xit")

    def _validate_turbospectrum_path(self):
        """
        Check that the path to the Turbospectrum directory exists.

        Raises:
            FileNotFoundError: If the path to the Turbospectrum directory does not exist.
        """
        if not os.path.exists(self.path_turbospectrum):
            raise FileNotFoundError(
                f"The specified directory containing Turbospectrum {self.config_file} does not exist."
            )

    def _validate_interpolator_path(self):
        """
        Check that the path to the interpolator directory exists.

        Raises:
            FileNotFoundError: If the path to the interpolator directory does not exist.
        """
        if not os.path.exists(self.path_interpolator):
            raise FileNotFoundError(
                f"The specified directory containing the interpolator {self.path_interpolator} does not exist."
            )

    def _validate_compiler(self):
        """
        Check that the compiler is supported and set the path to the compiled Turbospectrum executable.

        Suported compilers are "intel" and "gfortran".

        Side effects: Sets the path to the compiled Turbospectrum executable.
        Raises:
            ValueError: If the compiler is not supported.
        """
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

    def _validate_paths_to_directories(self):
        """
        Check that all paths to directories exist.

        Raises:
            FileNotFoundError: If any of the paths to directories do not exist.
        """
        paths = [
            self.path_linelists,
            self.path_model_atmospheres,
            self.path_output_directory,
        ]
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"The specified directory {path} does not exist."
                )

    def _validate_path_to_input_parameters(self):
        """
        Check that the path to the input parameters file exists.

        Raises:
            FileNotFoundError: If the path to the input parameters file does not exist.
        """
        if not os.path.exists(self.path_input_parameters):
            raise FileNotFoundError(
                f"The specified file {self.path_input_parameters} does not exist."
            )

    def _validate_wavelength_range(self):
        """
        Check that the wavelength range is valid.

        Raises:
            ValueError: If any wavelength parameter is negative or if the minimum wavelength is greater than the maximum wavelength.
        """
        if self.wavelength_min >= self.wavelength_max:
            raise ValueError(
                f"The minimum wavelength {self.wavelength_min} must be smaller than the maximum wavelength {self.wavelength_max}."
            )

        if (
            self.wavelength_min <= 0
            or self.wavelength_max <= 0
            or self.wavelength_step <= 0
        ):
            raise ValueError(f"The wavelength parameters must be greater than 0.")

    def _validate_stellar_parameters(self):
        """
        A wrapper function that checks that the stellar parameters are valid.
        """
        self._validate_effective_temperature()
        self._validate_surface_gravity()
        self._validate_metallicity()
        self._validate_magensium_abundance()
        self._validate_calcium_abundance()

        if self.random_parameters == True:
            self._validate_number_of_spectra()
        else:
            self._validate_evenly_spaced_parameters_points()

    def _validate_number_of_spectra(self):
        """
        Check that the number of spectra to generate is at least 1.

        Raises:
            ValueError: If the number of spectra is less than or equal to 0.
        """
        if self.num_spectra <= 0:
            raise ValueError(
                f"The number of spectra {self.num_spectra} must be greater than 0."
            )

    def _validate_effective_temperature(self):
        """
        Check that the effective temperature range is valid.

        Raises:
            ValueError: If any effective temperature parameter is negative or if the minimum effective temperature is greater than the maximum effective temperature.
        """
        if self.teff_min < 0:
            raise ValueError(
                f"The minimum effective temperature {self.teff_min} must be positive."
            )

        if self.teff_max < 0:
            raise ValueError(
                f"The maximum effective temperature {self.teff_max} must be positive."
            )

        if self.teff_min >= self.teff_max:
            raise ValueError(
                f"The minimum effective temperature {self.teff_min} must be smaller than the maximum effective temperature {self.teff_max}."
            )

    def _validate_surface_gravity(self):
        """
        Check that the surface gravity range is valid.

        Raises:
            ValueError: If any surface gravity parameter is negative or if the minimum surface gravity is greater than the maximum surface gravity.
        """
        # TODO: Istället för att raise'a error, skriv ut varningsmeddelande och fortsätt programmet. Och ändra gränsen till 2
        if self.logg_min < 0:
            raise ValueError(
                f"The minimum surface gravity {self.logg_min} must be positive."
            )

        if self.logg_max < 0:
            raise ValueError(
                f"The maximum surface gravity {self.logg_max} must be positive."
            )

        if self.logg_min >= self.logg_max:
            raise ValueError(
                f"The minimum surface gravity {self.logg_min} must be smaller than the maximum surface gravity {self.logg_max}."
            )

    def _validate_metallicity(self):
        """
        Check that the metallicity range is valid.

        Raises:
            ValueError: If the minimum metallicity is greater than the maximum metallicity.
        """
        if self.z_min >= self.z_max:
            raise ValueError(
                f"The minimum metallicity {self.z_min} must be smaller than the maximum metallicity {self.z_max}."
            )

    def _validate_magensium_abundance(self):
        """
        Check that the magnesium abundance range is valid.

        Raises:
            ValueError: If the minimum magnesium abundance is greater than the maximum magnesium abundance.
        """
        if self.mg_min >= self.mg_max:
            raise ValueError(
                f"The minimum magnesium abundance {self.mg_min} must be smaller than the maximum magnesium abundance {self.mg_max}."
            )

    def _validate_calcium_abundance(self):
        """
        Check that the calcium abundance range is valid.

        Raises:
            ValueError: If the minimum calcium abundance is greater than the maximum calcium abundance.
        """
        if self.ca_min >= self.ca_max:
            raise ValueError(
                f"The minimum calcium abundance {self.ca_min} must be smaller than the maximum calcium abundance {self.ca_max}."
            )

    def _validate_evenly_spaced_parameters_points(self):
        """
        Check that the number of points for each parameter is at least 1.

        Raises:
            ValueError: If the number of points for any parameter is less than 1.
        """
        if (
            self.num_points_teff < 1
            or self.num_points_logg < 1
            or self.num_points_z < 1
            or self.num_points_mg < 1
            or self.num_points_ca < 1
        ):
            raise ValueError(
                f"The number of points for each parameter must be at least 1."
            )

    def _validate_configuration(self):
        """
        A wrapper function that checks if all required parameters are set and within range.
        """
        self._validate_turbospectrum_path()
        self._validate_compiler()
        self._validate_paths_to_directories()
        self._validate_wavelength_range()

        if self.read_stellar_parameters_from_file == True:
            self._validate_path_to_input_parameters()
        else:
            self._validate_stellar_parameters()
