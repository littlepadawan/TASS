import unittest
from unittest.mock import patch, MagicMock
import subprocess
from input.configuration import Configuration
import spectrum_synthesis_utils as utils
import os
from shutil import rmtree


# Run tests with this command: python3 -m unittest tests.test_config
class TestConfig(unittest.TestCase):

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

    def test_non_existing_config(self):
        """
        Test that an error is raised if the config file does not exist
        """
        with self.assertRaises(FileNotFoundError):
            config = Configuration("tests/non_existing_config.cfg")

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


class TestCompile(unittest.TestCase):
    def setUp(self):
        # Set up a Configuration object
        self.config = Configuration()

    @patch("spectrum_synthesis_utils.os.chdir")
    @patch("spectrum_synthesis_utils.subprocess.run")
    def test_compile_turbospectrum_success(self, mock_run, mock_chdir):
        """
        Test that Turbospectrum is compiled successfully
        """
        # Mock subprocess.run to somulate a successful command
        mock_run.return_value = MagicMock(check=True)

        utils.compile_turbospectrum(self.config)

        # Check if subprocess.run was called correclty
        mock_run.assert_called_once_with(
            ["make"], check=True, text=True, capture_output=True
        )

    @patch("spectrum_synthesis_utils.os.chdir")
    @patch("spectrum_synthesis_utils.subprocess.run")
    def test_compile_turbospectrum_failure(self, mock_run, mock_chdir):
        """
        Test that an error is raised if Turbospectrum compilation fails
        """
        # Mock subprocess.run to somulate a failed command
        mock_run.side_effect = subprocess.CalledProcessError(1, "make", "Error")

        with self.assertRaises(subprocess.CalledProcessError):
            utils.compile_turbospectrum(self.config)

    @patch("spectrum_synthesis_utils.os.chdir")
    @patch("spectrum_synthesis_utils.subprocess.run")
    def test_return_to_original_directory(self, mock_run, mock_chdir):
        """
        Test that the working directory is changed back to the original directory
        """
        original_directory = "/original/directory"
        with patch(
            "spectrum_synthesis_utils.os.getcwd", return_value=original_directory
        ):
            utils.compile_turbospectrum(self.config)

        # Make sure os.chdir is called to return to the original directory
        mock_chdir.assert_called_with(original_directory)


if __name__ == "__main__":
    unittest.main()
