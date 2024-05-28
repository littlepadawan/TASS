import os
import unittest
from shutil import rmtree
from unittest.mock import MagicMock, patch

from source.configuration_setup import Configuration


# Run tests with this command: python3 -m unittest tests.test_config
class TestConfigurationSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up dummy directories and files for testing
        os.makedirs("tests/test_input", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum/interpolator", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum/exec", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum/exec-gf", exist_ok=True)
        os.makedirs("tests/test_input/linelists", exist_ok=True)
        os.makedirs("tests/test_input/model_atmospheres", exist_ok=True)
        open("tests/test_input/input_parameters.txt", "a").close()
        os.makedirs("tests/test_input/output", exist_ok=True)

        # Create config file for testing
        with open("tests/test_input/configuration.cfg", "w") as f:
            f.write("[Turbospectrum_compiler]\n")
            f.write("Compiler = gfortran\n")
            f.write("[Paths]\n")
            f.write("turbospectrum = ./tests/test_input/turbospectrum/\n")
            f.write("interpolator = ./tests/test_input/turbospectrum/interpolator/\n")
            f.write("linelists = ./tests/test_input/linelists/\n")
            f.write("model_atmospheres = ./tests/test_input/model_atmospheres/\n")
            f.write("input_parameters = ./tests/test_input/input_parameters.txt\n")
            f.write("output_directory = ./tests/test_input/output\n")
            f.write("[Atmosphere_parameters]\n")
            f.write("wavelength_min = 5700\n")
            f.write("wavelength_max = 7000\n")
            f.write("wavelength_step = 0.05\n")
            f.write("[Stellar_parameters]\n")
            f.write("read_from_file = False\n")
            f.write("random_parameters = True\n")
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("z_min = -1.0\n")
            f.write("z_max = 0.5\n")
            f.write("mg_min = -0.8\n")
            f.write("mg_max = 1.2\n")
            f.write("ca_min = -0.8\n")
            f.write("ca_max = 1.2\n")
            f.write("[Random_settings]\n")
            f.write("num_spectra = 10\n")
            f.write("[Even_settings]\n")
            f.write("num_points_teff = 10\n")
            f.write("num_points_logg = 8\n")
            f.write("num_points_z = 5\n")
            f.write("num_points_mg = 5\n")
            f.write("num_points_ca = 5\n")
            f.write("[Turbospectrum_settings]\n")
            f.write("xit = 1.0\n")

    @classmethod
    def tearDownClass(cls):
        # Remove dummy directories and files
        rmtree("tests/test_input")

    def test_config_default(self):
        """
        Test that the default config file is used if no path is given
        """
        config = Configuration()
        self.assertEqual(config.config_file, os.path.abspath("input/configuration.cfg"))

    def test_config_path(self):
        """
        Test that the correct config file is used if a path is given
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertEqual(
            config.config_file, os.path.abspath("tests/test_input/configuration.cfg")
        )

    @patch("source.configuration_setup.os.path.exists", return_value=False)
    def test_non_existing_config_file(self, mock_exists):
        """
        Test that an error is raised if the config file does not exist
        """
        with self.assertRaises(FileNotFoundError):
            Configuration("tests/non_existing_config.cfg")

    @patch("source.configuration_setup.os.path.exists", return_value=True)
    @patch("source.configuration_setup.Configuration._load_configuration_file")
    @patch("source.configuration_setup.Configuration._validate_configuration")
    def test_errors_caught_in_constructor(self, mock_validate, mock_load, mock_exists):
        """
        Test that errors are caught in the constructor
        """
        mock_validate.side_effect = ValueError()
        with self.assertRaises(SystemExit) as cm:
            Configuration()
        self.assertEqual(cm.exception.code, 1)

    @patch("source.configuration_setup.os.path.exists", return_value=True)
    def test_validate_turbospectrum_path_success(self, mock_exists):
        """
        Test that an error is not raised if the path to Turbospectrum exists
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertTrue(os.path.exists(config.path_turbospectrum))

    def test_validate_turbospectrum_path_failure(self):
        """
        Test that an error is raised if the path to Turbospectrum does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_turbospectrum = "tests/non_existing_turbospectrum"
        with self.assertRaises(FileNotFoundError):
            config._validate_turbospectrum_path()

    @patch("source.configuration_setup.os.path.exists", return_value=True)
    def test_validate_interpolator_path_success(self, mock_exists):
        """
        Test that an error is not raised if the path to the interpolator exists
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertTrue(os.path.exists(config.path_interpolator))

    def test_validate_interpolator_path_failure(self):
        """
        Test that an error is raised if the path to the interpolator does not exist
        """
        # !Test passes but coverage does not acknowledge it
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_interpolator = "tests/turbospectrum/non_existing_interpolator"
        with self.assertRaises(FileNotFoundError):
            config._validate_interpolator_path()

    def test_compiler_gfortran(self):
        """
        Test that the path to Turbospectrum is set correctly for gfortran
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.compiler = "gfortran"
        config._validate_compiler()
        self.assertEqual(
            config.path_turbospectrum_compiled,
            os.path.abspath("tests/test_input/turbospectrum/exec-gf"),
        )

    def test_compiler_intel(self):
        """
        Test that the path to Turbospectrum is set correctly for intel
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.compiler = "intel"
        config._validate_compiler()
        self.assertEqual(
            config.path_turbospectrum_compiled,
            os.path.abspath("tests/test_input/turbospectrum/exec"),
        )

    def test_invalid_compiler(self):
        """
        Test that an error is raised if the compiler is not supported
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.compiler = "invalid_compiler"
        with self.assertRaises(ValueError):
            config._validate_compiler()

    @patch("source.configuration_setup.os.path.exists", return_value=True)
    def test_validate_path_to_directories_success(self, mock_exists):
        """
        Test that the path validation works when the paths exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertTrue(os.path.exists(config.path_turbospectrum))
        self.assertTrue(os.path.exists(config.path_linelists))
        self.assertTrue(os.path.exists(config.path_model_atmospheres))
        self.assertTrue(os.path.exists(config.path_output_directory))

    def test_invalid_path_linelists(self):
        """
        Test that an error is raised if the path to linelists does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_linelists = "tests/non_existing_linelists"
        with self.assertRaises(FileNotFoundError):
            config._validate_paths_to_directories()

    def test_invalid_path_model_atmospheres(self):
        """
        Test that an error is raised if the path to model atmospheres does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_model_atmospheres = "tests/non_existing_model_atmospheres"
        with self.assertRaises(FileNotFoundError):
            config._validate_paths_to_directories()

    def test_invalid_path_output_directory(self):
        """
        Test that an error is raised if the path to the output directory does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_output_directory = "tests/non_existing_output"
        with self.assertRaises(FileNotFoundError):
            config._validate_paths_to_directories()

    def test_invalid_path_input_parameters(self):
        """
        Test that an error is raised if the path to input parameters does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.read_stellar_parameters_from_file = True
        config.path_input_parameters = "tests/non_existing_input_parameters"
        with self.assertRaises(FileNotFoundError):
            config._validate_path_to_input_parameters()

    def test_invalid_wavelength_min_larger_than_max(self):
        """
        Test that an error is raised if the min wavelength is greater than the max wavelength
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = 7000
        config.wavelength_max = 5700
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_invalid_wavelength_min_equals_max(self):
        """
        Test that an error is raised if the min wavelength is equal to the max wavelength
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = 5700
        config.wavelength_max = 5700
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_invalid_wavelength_negative_min(self):
        """
        Test that an error is raised if the min wavelength is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = -1
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_invalid_wavelength_negative_max(self):
        """
        Test that an error is raised if the max wavelength is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_max = -1
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_invalid_wavelegth_negative_step(self):
        """
        Test that an error is raised if the wavelength step is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_step = -1
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_invalid_wavelength_step_zero(self):
        """
        Test that an error is raised if the wavelength step is zero
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_step = 0
        with self.assertRaises(ValueError):
            config._validate_wavelength_range()

    def test_valid_stellar_parameters(self):
        """
        Test that the stellar parameters are set correctly
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertFalse(config.read_stellar_parameters_from_file)
        self.assertEqual(config.num_spectra, 10)
        self.assertEqual(config.teff_min, 5000)
        self.assertEqual(config.teff_max, 7000)
        self.assertEqual(config.logg_min, 4.0)
        self.assertEqual(config.logg_max, 5.0)
        self.assertEqual(config.z_min, -1.0)
        self.assertEqual(config.z_max, 0.5)

    def test_negative_num_spectra(self):
        """
        Test that an error is raised if the number of spectra is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = -5
        with self.assertRaises(ValueError):
            config._validate_number_of_spectra()

    def test_zero_num_spectra(self):
        """
        Test that an error is raised if the number of spectra is zero
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 0
        with self.assertRaises(ValueError):
            config._validate_number_of_spectra()

    def test_invalid_teff_min_larger_than_max(self):
        """
        Test that an error is raised if the min effective temperature is greater than the max effective temperature
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_min = 7000
        config.teff_max = 5000
        with self.assertRaises(ValueError):
            config._validate_effective_temperature()

    def test_invalid_teff_min_negative(self):
        """
        Test that an error is raised if the min effective temperature is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_min = -1
        with self.assertRaises(ValueError):
            config._validate_effective_temperature()

    def test_invalid_teff_max_negative(self):
        """
        Test that an error is raised if the max effective temperature is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_max = -1
        with self.assertRaises(ValueError):
            config._validate_effective_temperature()

    def test_invalid_logg_min_larger_than_max(self):
        """
        Test that an error is raised if the min surface gravity is greater than the max surface gravity
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_min = 5.0
        config.logg_max = 4.0
        with self.assertRaises(ValueError):
            config._validate_surface_gravity()

    def test_invalid_logg_min_negative(self):
        """
        Test that an error is raised if the min surface gravity is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_min = -1
        with self.assertRaises(ValueError):
            config._validate_surface_gravity()

    def test_invalid_logg_max_negative(self):
        """
        Test that an error is raised if the max surface gravity is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_max = -1
        with self.assertRaises(ValueError):
            config._validate_surface_gravity()

    def test_invalid_z_min_larger_than_max(self):
        """
        Test that an error is raised if the min metallicity is greater than the max metallicity
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.z_min = 0.5
        config.z_max = -1.0
        with self.assertRaises(ValueError):
            config._validate_metallicity()

    def test_no_stellar_parameters_loaded_if_read_from_file(self):
        """
        Test that no stellar parameters are loaded from configuration file if they are supposed to be read from a file
        """
        with open(
            "tests/test_input/configuration_read_stellar_parameters_from_file.cfg", "w"
        ) as f:
            f.write("[Turbospectrum_compiler]\n")
            f.write("Compiler = gfortran\n")
            f.write("[Paths]\n")
            f.write("turbospectrum = ./tests/test_input/turbospectrum/\n")
            f.write("interpolator = ./tests/test_input/turbospectrum/interpolator/\n")
            f.write("linelists = ./tests/test_input/linelists/\n")
            f.write("model_atmospheres = ./tests/test_input/model_atmospheres/\n")
            f.write("input_parameters = ./tests/test_input/input_parameters.txt\n")
            f.write("output_directory = ./tests/test_input/output\n")
            f.write("[Atmosphere_parameters]\n")
            f.write("wavelength_min = 5700\n")
            f.write("wavelength_max = 7000\n")
            f.write("wavelength_step = 0.05\n")
            f.write("[Stellar_parameters]\n")
            f.write("read_from_file = True\n")  # This is the only difference
            f.write("random_parameters = True\n")
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("z_min = -1.0\n")
            f.write("z_max = 0.5\n")
            f.write("mg_min = -0.8\n")
            f.write("mg_max = 1.2\n")
            f.write("ca_min = -0.8\n")
            f.write("ca_max = 1.2\n")
            f.write("[Random_settings]\n")
            f.write("num_spectra = 10\n")
            f.write("[Even_settings]\n")
            f.write("num_points_teff = 10\n")
            f.write("num_points_logg = 8\n")
            f.write("num_points_z = 5\n")
            f.write("num_points_mg = 5\n")
            f.write("num_points_ca = 5\n")
            f.write("[Turbospectrum_settings]\n")
            f.write("xit = 1.0\n")
        config = Configuration(
            "tests/test_input/configuration_read_stellar_parameters_from_file.cfg"
        )
        self.assertEqual(config.num_spectra, 0)
        self.assertEqual(config.teff_max, 0)
        self.assertEqual(config.teff_min, 0)
        self.assertEqual(config.logg_max, 0)
        self.assertEqual(config.logg_min, 0)
        self.assertEqual(config.z_max, 0)
        self.assertEqual(config.z_min, 0)
        self.assertEqual(config.num_points_teff, 0)
        self.assertEqual(config.num_points_logg, 0)
        self.assertEqual(config.num_points_z, 0)
        self.assertEqual(config.num_points_mg, 0)
        self.assertEqual(config.num_points_ca, 0)

    def test_random_parameters_set_to_true(self):
        """
        Test that the number of spectra to generate is loaded if random parameters are set to True
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertTrue(config.random_parameters)
        self.assertEqual(config.num_spectra, 10)

    def test_random_parameters_set_to_false(self):
        """
        Test that the number of points in each parameter dimension is loaded if random parameters are set to False
        """
        with open(
            "tests/test_input/configuration_evenly_spaced_parameters.cfg", "w"
        ) as f:
            f.write("[Turbospectrum_compiler]\n")
            f.write("Compiler = gfortran\n")
            f.write("[Paths]\n")
            f.write("turbospectrum = ./tests/test_input/turbospectrum/\n")
            f.write("interpolator = ./tests/test_input/turbospectrum/interpolator/\n")
            f.write("linelists = ./tests/test_input/linelists/\n")
            f.write("model_atmospheres = ./tests/test_input/model_atmospheres/\n")
            f.write("input_parameters = ./tests/test_input/input_parameters.txt\n")
            f.write("output_directory = ./tests/test_input/output\n")
            f.write("[Atmosphere_parameters]\n")
            f.write("wavelength_min = 5700\n")
            f.write("wavelength_max = 7000\n")
            f.write("wavelength_step = 0.05\n")
            f.write("[Stellar_parameters]\n")
            f.write("read_from_file = False\n")
            f.write("random_parameters = False\n")  # This is the only difference
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("z_min = -1.0\n")
            f.write("z_max = 0.5\n")
            f.write("mg_min = -0.8\n")
            f.write("mg_max = 1.2\n")
            f.write("ca_min = -0.8\n")
            f.write("ca_max = 1.2\n")
            f.write("[Random_settings]\n")
            f.write("num_spectra = 10\n")
            f.write("[Even_settings]\n")
            f.write("num_points_teff = 10\n")
            f.write("num_points_logg = 8\n")
            f.write("num_points_z = 5\n")
            f.write("num_points_mg = 5\n")
            f.write("num_points_ca = 5\n")
            f.write("[Turbospectrum_settings]\n")
            f.write("xit = 1.0\n")
        config = Configuration(
            "tests/test_input/configuration_evenly_spaced_parameters.cfg"
        )

        # Test that number of points in each parameter dimension is loaded
        self.assertEqual(config.num_points_teff, 10)
        self.assertEqual(config.num_points_logg, 8)
        self.assertEqual(config.num_points_z, 5)
        self.assertEqual(config.num_points_mg, 5)
        self.assertEqual(config.num_points_ca, 5)

        # Test that number of spextra is not loaded
        self.assertEqual(config.num_spectra, 0)

    def test_invalid_mg_range(self):
        """
        Test that an error is raised if the min magnesium abundance is greater than the max magnesium abundance
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.mg_min = 1.2
        config.mg_max = -0.8
        with self.assertRaises(ValueError):
            config._validate_magnesium_abundance()

    def test_invalid_ca_range(self):
        """
        Test that an error is raised if the min calcium abundance is greater than the max calcium abundance
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.ca_min = 1.2
        config.ca_max = -0.8
        with self.assertRaises(ValueError):
            config._validate_calcium_abundance()

    def test_validate_evenly_spaced_parameter_points(self):
        """
        Test that an error is raised if the number of points in any parameter dimension is less than 1.
        """
        config = Configuration("tests/test_input/configuration.cfg")

        config.num_points_teff = 0
        with self.assertRaises(ValueError):
            config._validate_evenly_spaced_parameters_points()

        config.num_points_teff = 10
        config.num_points_logg = 0
        with self.assertRaises(ValueError):
            config._validate_evenly_spaced_parameters_points()

        config.num_points_logg = 8
        config.num_points_z = 0
        with self.assertRaises(ValueError):
            config._validate_evenly_spaced_parameters_points()

        config.num_points_z = 5
        config.num_points_mg = 0
        with self.assertRaises(ValueError):
            config._validate_evenly_spaced_parameters_points()

        config.num_points_mg = 5
        config.num_points_ca = 0
        with self.assertRaises(ValueError):
            config._validate_evenly_spaced_parameters_points()


if __name__ == "__main__":
    unittest.main()
