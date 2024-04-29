import unittest
from unittest.mock import patch, MagicMock
import subprocess
from configuration_setup import Configuration
import turbospectrum_integration
import parameter_generation
import os
from shutil import rmtree


# Run tests with this command: python3 -m unittest tests.test_config
class TestConfigSetup(unittest.TestCase):

    def setUp(self):
        # Set up dummy directories and files for testing
        os.makedirs("tests/test_input", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum", exist_ok=True)
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
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("feh_min = -2.0\n")
            f.write("feh_max = 0.5\n")

    def tearDown(self):
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

    @patch("configuration_setup.os.path.exists", return_value=False)
    def test_non_existing_config_file(self, mock_exists):
        """
        Test that an error is raised if the config file does not exist
        """
        with self.assertRaises(FileNotFoundError):
            Configuration("tests/non_existing_config.cfg")

    @patch("configuration_setup.os.path.exists", return_value=True)
    @patch("configuration_setup.Configuration._load_configuration_file")
    @patch("configuration_setup.Configuration._validate_configuration")
    def test_errors_caught_in_constructor(self, mock_validate, mock_load, mock_exists):
        """
        Test that errors are caught in the constructor
        """
        mock_validate.side_effect = ValueError()
        with self.assertRaises(SystemExit) as cm:
            Configuration()
        self.assertEqual(cm.exception.code, 1)

    def test_path_validation_success(self):
        """
        Test that the path validation works when the paths exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertTrue(os.path.exists(config.path_turbospectrum))
        self.assertTrue(os.path.exists(config.path_linelists))
        self.assertTrue(os.path.exists(config.path_model_atmospheres))
        self.assertTrue(os.path.isfile(config.path_input_parameters))
        self.assertTrue(os.path.exists(config.path_output_directory))

    def test_invalid_path_turbospectrum(self):
        """
        Test that an error is raised if the path to Turbospectrum does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_turbospectrum = "tests/non_existing_turbospectrum"
        with self.assertRaises(FileNotFoundError):
            config._validate_configuration()

    def test_invalid_path_linelists(self):
        """
        Test that an error is raised if the path to linelists does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_linelists = "tests/non_existing_linelists"
        with self.assertRaises(FileNotFoundError):
            config._validate_configuration()

    def test_invalid_path_model_atmospheres(self):
        """
        Test that an error is raised if the path to model atmospheres does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_model_atmospheres = "tests/non_existing_model_atmospheres"
        with self.assertRaises(FileNotFoundError):
            config._validate_configuration()

    def test_invalid_path_input_parameters(self):
        """
        Test that an error is raised if the path to input parameters does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_input_parameters = "tests/non_existing_input_parameters"
        with self.assertRaises(FileNotFoundError):
            config._validate_configuration()

    def test_invalid_path_output_directory(self):
        """
        Test that an error is raised if the path to the output directory does not exist
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_output_directory = "tests/non_existing_output"
        with self.assertRaises(FileNotFoundError):
            config._validate_configuration()

    def test_compiler_gfortran(self):
        """
        Test that the path to Turbospectrum is set correctly for gfortran
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.compiler = "gfortran"
        config._validate_configuration()
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
        config._validate_configuration()
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
            config._validate_configuration()

    def test_invalid_wavelength_min_larger_than_max(self):
        """
        Test that an error is raised if the min wavelength is greater than the max wavelength
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = 7000
        config.wavelength_max = 5700
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_wavelength_min_equals_max(self):
        """
        Test that an error is raised if the min wavelength is equal to the max wavelength
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = 5700
        config.wavelength_max = 5700
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_wavelength_negative_min(self):
        """
        Test that an error is raised if the min wavelength is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_min = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_wavelength_negative_max(self):
        """
        Test that an error is raised if the max wavelength is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_max = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_wavelegth_negative_step(self):
        """
        Test that an error is raised if the wavelength step is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_step = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_wavelength_step_zero(self):
        """
        Test that an error is raised if the wavelength step is zero
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.wavelength_step = 0
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_valid_stellar_parameters(self):
        """
        Test that the stellar parameters are set correctly
        """
        config = Configuration("tests/test_input/configuration.cfg")
        self.assertFalse(config.read_stellar_parameters_from_file)
        self.assertEqual(config.teff_min, 5000)
        self.assertEqual(config.teff_max, 7000)
        self.assertEqual(config.logg_min, 4.0)
        self.assertEqual(config.logg_max, 5.0)
        self.assertEqual(config.feh_min, -2.0)
        self.assertEqual(config.feh_max, 0.5)

    def test_invalid_teff_min_larger_than_max(self):
        """
        Test that an error is raised if the min effective temperature is greater than the max effective temperature
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_min = 7000
        config.teff_max = 5000
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_teff_min_negative(self):
        """
        Test that an error is raised if the min effective temperature is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_min = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_teff_max_negative(self):
        """
        Test that an error is raised if the max effective temperature is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.teff_max = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_logg_min_larger_than_max(self):
        """
        Test that an error is raised if the min surface gravity is greater than the max surface gravity
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_min = 5.0
        config.logg_max = 4.0
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_logg_min_negative(self):
        """
        Test that an error is raised if the min surface gravity is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_min = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_logg_max_negative(self):
        """
        Test that an error is raised if the max surface gravity is negative
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.logg_max = -1
        with self.assertRaises(ValueError):
            config._validate_configuration()

    def test_invalid_feh_min_larger_than_max(self):
        """
        Test that an error is raised if the min metallicity is greater than the max metallicity
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.feh_min = 0.5
        config.feh_max = -2.0
        with self.assertRaises(ValueError):
            config._validate_configuration()

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
            f.write("linelists = ./tests/test_input/linelists/\n")
            f.write("model_atmospheres = ./tests/test_input/model_atmospheres/\n")
            f.write("input_parameters = ./tests/test_input/input_parameters.txt\n")
            f.write("output_directory = ./tests/test_input/output\n")
            f.write("[Atmosphere_parameters]\n")
            f.write("wavelength_min = 5700\n")
            f.write("wavelength_max = 7000\n")
            f.write("wavelength_step = 0.05\n")
            f.write("[Stellar_parameters]\n")
            f.write("read_from_file = True\n")
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("feh_min = -2.0\n")
            f.write("feh_max = 0.5\n")
        config = Configuration(
            "tests/test_input/configuration_read_stellar_parameters_from_file.cfg"
        )
        self.assertEqual(config.teff_max, 0)
        self.assertEqual(config.teff_min, 0)
        self.assertEqual(config.logg_max, 0)
        self.assertEqual(config.logg_min, 0)
        self.assertEqual(config.feh_max, 0)
        self.assertEqual(config.feh_min, 0)


class TestTurbospectrumIntegration(unittest.TestCase):
    def setUp(self):
        # Set up a Configuration object
        self.config = Configuration()

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_compile_turbospectrum_success(self, mock_run, mock_chdir):
        """
        Test that Turbospectrum is compiled successfully
        """
        # Mock subprocess.run to somulate a successful command
        mock_run.return_value = MagicMock(check=True)

        turbospectrum_integration.compile_turbospectrum(self.config)

        # Check if subprocess.run was called correclty
        mock_run.assert_called_once_with(
            ["make"], check=True, text=True, capture_output=True
        )

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_compile_turbospectrum_failure(self, mock_run, mock_chdir):
        """
        Test that an error is raised if Turbospectrum compilation fails
        """
        # Mock subprocess.run to somulate a failed command
        mock_run.side_effect = subprocess.CalledProcessError(1, "make", "Error")

        with self.assertRaises(subprocess.CalledProcessError):
            turbospectrum_integration.compile_turbospectrum(self.config)

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_return_to_original_directory_after_compile(self, mock_run, mock_chdir):
        """
        Test that the working directory is changed back to the original directory after compiling Turbospectrum
        """
        original_directory = "/original/directory"
        with patch(
            "turbospectrum_integration.os.getcwd", return_value=original_directory
        ):
            turbospectrum_integration.compile_turbospectrum(self.config)

        # Make sure os.chdir is called to return to the original directory
        mock_chdir.assert_called_with(original_directory)


class TestParameterGeneration(unittest.TestCase):
    def setUp(self):
        # Set up dummy directories for testing
        os.makedirs("tests/test_input", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum/exec", exist_ok=True)
        os.makedirs("tests/test_input/turbospectrum/exec-gf", exist_ok=True)
        os.makedirs("tests/test_input/linelists", exist_ok=True)
        os.makedirs("tests/test_input/model_atmospheres", exist_ok=True)
        os.makedirs("tests/test_input/output", exist_ok=True)

        # Create config file for testing
        with open("tests/test_input/configuration.cfg", "w") as f:
            f.write("[Turbospectrum_compiler]\n")
            f.write("Compiler = gfortran\n")
            f.write("[Paths]\n")
            f.write("turbospectrum = ./tests/test_input/turbospectrum/\n")
            f.write("linelists = ./tests/test_input/linelists/\n")
            f.write("model_atmospheres = ./tests/test_input/model_atmospheres/\n")
            f.write("input_parameters = ./tests/test_input/input_parameters.txt\n")
            f.write("output_directory = ./tests/test_input/output\n")
            f.write("[Atmosphere_parameters]\n")
            f.write("wavelength_min = 5700\n")
            f.write("wavelength_max = 7000\n")
            f.write("wavelength_step = 0.05\n")
            f.write("[Stellar_parameters]\n")
            f.write("read_from_file = True\n")

        # Create file with stellar parameters for testing
        with open("tests/test_input/input_parameters.txt", "w") as f:
            f.write("teff logg fe/h\n")
            f.write("7957  4.91 -0.425\n")
            f.write("5952  2.71 -0.014\n")
            f.write("3543  1.19 -2.573\n")
            f.write("3837  5.41  0.258\n")
            f.write("3070  2.50 -4.387\n")
            f.write("3862  4.79 -1.686\n")
            f.write("6897  2.45 -0.636\n")
            f.write("2920  3.03 -3.941\n")

    def tearDown(self):
        # Remove dummy directories and files
        rmtree("tests/test_input")

    def test_read_parameters_from_file(self):
        """
        Test that the stellar parameters are read from the input file
        """
        config = Configuration("tests/test_input/configuration.cfg")
        stellar_parameters = parameter_generation.read_parameters_from_file(config)
        self.assertEqual(
            stellar_parameters,
            [
                {"teff": "7957", "logg": "4.91", "fe/h": "-0.425"},
                {"teff": "5952", "logg": "2.71", "fe/h": "-0.014"},
                {"teff": "3543", "logg": "1.19", "fe/h": "-2.573"},
                {"teff": "3837", "logg": "5.41", "fe/h": "0.258"},
                {"teff": "3070", "logg": "2.50", "fe/h": "-4.387"},
                {"teff": "3862", "logg": "4.79", "fe/h": "-1.686"},
                {"teff": "6897", "logg": "2.45", "fe/h": "-0.636"},
                {"teff": "2920", "logg": "3.03", "fe/h": "-3.941"},
            ],
        )

    @patch("parameter_generation.sys.exit")
    def test_read_parameters_from_file_missing_parameters(self, mock_exit):
        """
        Test that an error is raised if the input file is missing required parameters
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.path_input_parameters = "tests/test_input/input_parameters_missing.txt"
        with open("tests/test_input/input_parameters_missing.txt", "w") as f:
            f.write("teff logg\n")
            f.write("7957 4.91\n")
        parameter_generation.read_parameters_from_file(config)
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
