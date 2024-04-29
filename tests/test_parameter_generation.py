import unittest
from unittest.mock import patch, MagicMock
from configuration_setup import Configuration
import parameter_generation
import os
from shutil import rmtree


class TestParameterGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
            f.write("num_spectra = 10\n")
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("feh_min = -2.0\n")
            f.write("feh_max = 0.5\n")

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

    @classmethod
    def tearDownClass(cls):
        # Remove dummy directories and files
        rmtree("tests/test_input")

    def test_read_parameters_from_file(self):
        """
        Test that the stellar parameters are read from the input file
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.read_stellar_parameters_from_file = True
        config.path_input_parameters = "tests/test_input/input_parameters.txt"
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

    def test_generate_random_parameters(self):
        """
        Test that the correct number of random stellar parameters are generated,
        and that they are within bounds
        """
        config = Configuration("tests/test_input/configuration.cfg")
        stellar_parameters = parameter_generation.generate_random_parameters(config)
        self.assertEqual(len(stellar_parameters), 10)
        for parameters in stellar_parameters:
            self.assertGreaterEqual(int(parameters[0]), 5000)
            self.assertLessEqual(int(parameters[0]), 7000)
            self.assertGreaterEqual(float(parameters[1]), 4.0)
            self.assertLessEqual(float(parameters[1]), 5.0)
            self.assertGreaterEqual(float(parameters[2]), -2.0)
            self.assertLessEqual(float(parameters[2]), 0.5)

    def test_generate_random_parameters_1000(self):
        """
        Test that 1000 random stellar parameters are generated,
        and that they are within bounds
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 1000
        stellar_parameters = parameter_generation.generate_random_parameters(config)
        self.assertEqual(len(stellar_parameters), 1000)
