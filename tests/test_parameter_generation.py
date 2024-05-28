import os
import unittest
from shutil import rmtree
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import source.parameter_generation as parameter_generation
from source.configuration_setup import Configuration


class TestParameterGeneration(unittest.TestCase):
    MIN_PARAMETER_DELTA = {
        "teff": 50,
        "logg": 0.1,
        "z": 0.1,
        "mg": 0.1,
        "ca": 0.1,
    }

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

        # Create file with stellar parameters for testing
        with open("tests/test_input/input_parameters.txt", "w") as f:
            f.write("teff logg z mg ca\n")
            f.write("7957  4.91 -0.425  0.12  0.15\n")
            f.write("5952  2.71 -0.014 -0.05  0.10\n")
            f.write("3543  1.19 -2.573  0.25 -0.10\n")
            f.write("3837  5.41  0.258  0.18  0.20\n")
            f.write("3070  2.50 -4.387 -0.30 -0.25\n")
            f.write("3862  4.79 -1.686  0.00  0.05\n")
            f.write("6897  2.45 -0.636  0.10 -0.05\n")
            f.write("2920  3.03 -3.941 -0.20  0.00\n")

        cls.existing_parameters = {
            "teff": [5000, 5100, 5200],
            "logg": [4.0, 4.1, 4.2],
            "z": [-1.0, -0.9, -0.8],
            "mg": [0.1, 0.2, 0.3],
            "ca": [0.2, 0.3, 0.4],
        }

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
                {
                    "teff": 7957,
                    "logg": 4.91,
                    "z": -0.425,
                    "mg": 0.12,
                    "ca": 0.15,
                },
                {
                    "teff": 5952,
                    "logg": 2.71,
                    "z": -0.014,
                    "mg": -0.05,
                    "ca": 0.10,
                },
                {
                    "teff": 3543,
                    "logg": 1.19,
                    "z": -2.573,
                    "mg": 0.25,
                    "ca": -0.10,
                },
                {
                    "teff": 3837,
                    "logg": 5.41,
                    "z": 0.258,
                    "mg": 0.18,
                    "ca": 0.20,
                },
                {
                    "teff": 3070,
                    "logg": 2.50,
                    "z": -4.387,
                    "mg": -0.30,
                    "ca": -0.25,
                },
                {
                    "teff": 3862,
                    "logg": 4.79,
                    "z": -1.686,
                    "mg": 0.00,
                    "ca": 0.05,
                },
                {
                    "teff": 6897,
                    "logg": 2.45,
                    "z": -0.636,
                    "mg": 0.10,
                    "ca": -0.05,
                },
                {
                    "teff": 2920,
                    "logg": 3.03,
                    "z": -3.941,
                    "mg": -0.20,
                    "ca": 0.00,
                },
            ],
        )

    @patch("source.parameter_generation.sys.exit")
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

    def test_within_min_delta_no_valid_candidates(self):
        """
        Test that the function returns False when no candidate values are within minimun delta from the given value
        """
        parameter_value = 5000
        min_delta = 5
        candidate_values = [5005, 5010, 5015]
        for candidate in candidate_values:
            self.assertFalse(
                parameter_generation._within_min_delta(
                    parameter_value, candidate, min_delta
                )
            )

    def test_within_min_delta_valid_candidate(self):
        """
        Test that the function returns True when a candidate value is within minimun delta from the given value
        """
        parameter_value = 5000
        min_delta = 5
        candidate_values = [5004, 5003, 4999, 4996]
        for candidate in candidate_values:
            self.assertTrue(
                parameter_generation._within_min_delta(
                    parameter_value, candidate, min_delta
                )
            )

    @patch("source.parameter_generation.random.randint")
    @patch("source.parameter_generation.random.uniform")
    def test_generate_random_parameters_no_conflicts(self, mock_randint, mock_uniform):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameters when there are no conflicting parameter values.
        Obs: This test is sensitive regarding the number of parameters to generate. If num_spectra in config is changed, the expected values must be updated, and the mock numbers.
        """
        # Set up mock values
        # Teff
        randint_values = [
            5000,
            5005,
            5010,
            5015,
            5020,
            5025,
            5030,
            5035,
            5040,
            5045,
        ]
        # Logg, z, mg, and ca, interleaved
        uniform_values = [
            4.00,
            -1.000,
            0.1,
            0.2,
            4.11,
            -0.833,
            0.2,
            0.1,
            4.22,
            -0.667,
            0.3,
            0.0,
            4.33,
            -0.500,
            0.0,
            -0.1,
            4.44,
            -0.333,
            -0.1,
            -0.2,
            4.56,
            -0.167,
            -0.2,
            0.3,
            4.67,
            0.000,
            0.4,
            -0.3,
            4.78,
            0.167,
            0.5,
            0.4,
            4.89,
            0.333,
            -0.4,
            0.5,
            5.00,
            0.500,
            0.6,
            -0.4,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000, "mg": 0.1, "ca": 0.2},
            {"teff": 5005, "logg": 4.11, "z": -0.833, "mg": 0.2, "ca": 0.1},
            {"teff": 5010, "logg": 4.22, "z": -0.667, "mg": 0.3, "ca": 0.0},
            {"teff": 5015, "logg": 4.33, "z": -0.500, "mg": 0.0, "ca": -0.1},
            {"teff": 5020, "logg": 4.44, "z": -0.333, "mg": -0.1, "ca": -0.2},
            {"teff": 5025, "logg": 4.56, "z": -0.167, "mg": -0.2, "ca": 0.3},
            {"teff": 5030, "logg": 4.67, "z": 0.000, "mg": 0.4, "ca": -0.3},
            {"teff": 5035, "logg": 4.78, "z": 0.167, "mg": 0.5, "ca": 0.4},
            {"teff": 5040, "logg": 4.89, "z": 0.333, "mg": -0.4, "ca": 0.5},
            {"teff": 5045, "logg": 5.00, "z": 0.500, "mg": 0.6, "ca": -0.4},
        ]

        with patch("source.parameter_generation.random.randint"), patch(
            "source.parameter_generation.random.uniform"
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(
                all(len(parameter_set) == 5 for parameter_set in result)
            )  # Ensure all parameter sets have 5 parameters

            self.assertEqual(result, expected)

    @patch("source.parameter_generation.random.randint")
    @patch("source.parameter_generation.random.uniform")
    def test_generate_random_parameters_with_mixed_collisions(
        self, mock_randint, mock_uniform
    ):
        """
        Test that the function handles a mix of valid and conflicting parameter sets.
        """
        # Set up mock values to create a mix of valid and conflicting sets
        randint_values = [
            5000,
            5005,
            5000,
            5010,
            5000,
            5015,
            5020,
            5025,
            5030,
            5035,
            5040,
            5050,
            5060,
        ]
        # Logg, z, mg, and ca values, interleaved
        uniform_values = [
            4.00,
            -1.000,
            0.1,
            0.2,  # Conflict
            4.06,
            -0.899,
            0.2,
            0.1,
            4.00,
            -1.000,
            0.1,
            0.2,  # Conflict
            4.12,
            -0.799,
            0.3,
            0.0,
            4.00,
            -1.000,
            0.1,
            0.2,  # Conflict
            4.18,
            -0.699,
            0.0,
            -0.1,
            4.24,
            -0.599,
            -0.1,
            -0.2,
            4.30,
            -0.499,
            -0.2,
            0.3,
            4.36,
            -0.399,
            0.4,
            -0.3,
            4.42,
            -0.299,
            0.5,
            0.4,
            4.48,
            -0.199,
            -0.4,
            0.5,
            4.54,
            -0.099,
            0.6,
            -0.4,  # Ensure we have enough unique values to reach 10 sets
            4.60,
            0.000,
            0.7,
            0.6,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000, "mg": 0.1, "ca": 0.2},
            {"teff": 5005, "logg": 4.06, "z": -0.899, "mg": 0.2, "ca": 0.1},
            {"teff": 5010, "logg": 4.12, "z": -0.799, "mg": 0.3, "ca": 0.0},
            {"teff": 5015, "logg": 4.18, "z": -0.699, "mg": 0.0, "ca": -0.1},
            {"teff": 5020, "logg": 4.24, "z": -0.599, "mg": -0.1, "ca": -0.2},
            {"teff": 5025, "logg": 4.30, "z": -0.499, "mg": -0.2, "ca": 0.3},
            {"teff": 5030, "logg": 4.36, "z": -0.399, "mg": 0.4, "ca": -0.3},
            {"teff": 5035, "logg": 4.42, "z": -0.299, "mg": 0.5, "ca": 0.4},
            {"teff": 5040, "logg": 4.48, "z": -0.199, "mg": -0.4, "ca": 0.5},
            {"teff": 5050, "logg": 4.54, "z": -0.099, "mg": 0.6, "ca": -0.4},
        ]

        with patch(
            "source.parameter_generation.random.randint", side_effect=randint_values
        ), patch(
            "source.parameter_generation.random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 5 for parameter_set in result))
            self.assertEqual(result, expected)

    @patch("random.randint")
    @patch("random.uniform")
    def test_generate_random_parameters_with_teff_collisions(
        self, mock_randint, mock_uniform
    ):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameters when there are conflicting teff values, but no collisions in logg, z, mg, and ca values.
        """
        # Set up mock values
        # Teff value collides, same value every time
        randint_values = [5000] * 10
        # Logg, z, mg, and ca values, each set of values does not collide within the specified range
        uniform_values = [
            4.00,
            -1.000,
            0.1,
            0.2,
            4.06,
            -0.899,
            0.2,
            0.1,
            4.12,
            -0.799,
            0.3,
            0.0,
            4.18,
            -0.699,
            0.0,
            -0.1,
            4.24,
            -0.599,
            -0.1,
            -0.2,
            4.30,
            -0.499,
            -0.2,
            0.3,
            4.36,
            -0.399,
            0.4,
            -0.3,
            4.42,
            -0.299,
            0.5,
            0.4,
            4.48,
            -0.199,
            -0.4,
            0.5,
            4.54,
            -0.099,
            0.6,
            -0.4,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000, "mg": 0.1, "ca": 0.2},
            {"teff": 5000, "logg": 4.06, "z": -0.899, "mg": 0.2, "ca": 0.1},
            {"teff": 5000, "logg": 4.12, "z": -0.799, "mg": 0.3, "ca": 0.0},
            {"teff": 5000, "logg": 4.18, "z": -0.699, "mg": 0.0, "ca": -0.1},
            {"teff": 5000, "logg": 4.24, "z": -0.599, "mg": -0.1, "ca": -0.2},
            {"teff": 5000, "logg": 4.30, "z": -0.499, "mg": -0.2, "ca": 0.3},
            {"teff": 5000, "logg": 4.36, "z": -0.399, "mg": 0.4, "ca": -0.3},
            {"teff": 5000, "logg": 4.42, "z": -0.299, "mg": 0.5, "ca": 0.4},
            {"teff": 5000, "logg": 4.48, "z": -0.199, "mg": -0.4, "ca": 0.5},
            {"teff": 5000, "logg": 4.54, "z": -0.099, "mg": 0.6, "ca": -0.4},
        ]

        with patch("random.randint", side_effect=randint_values), patch(
            "random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 5 for parameter_set in result))
            self.assertEqual(result, expected)

    @patch("random.randint")
    @patch("random.uniform")
    def test_generate_random_parameters_with_teff_and_logg_collisions(
        self, mock_randint, mock_uniform
    ):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameters when there are conflicting teff and logg values, but no collisions in z, mg, and ca values.
        """
        # Set up mock values
        # Teff value collides, same value every time
        randint_values = [5000] * 10
        # Logg value collides, same value every time
        # z, mg, and ca values, each set of values does not collide within the specified range
        uniform_values = [
            4.0,
            -1.000,
            0.1,
            0.2,
            4.0,
            -0.899,
            0.2,
            0.1,
            4.0,
            -0.799,
            0.3,
            0.0,
            4.0,
            -0.699,
            0.0,
            -0.1,
            4.0,
            -0.599,
            -0.1,
            -0.2,
            4.0,
            -0.499,
            -0.2,
            0.3,
            4.0,
            -0.399,
            0.4,
            -0.3,
            4.0,
            -0.299,
            0.5,
            0.4,
            4.0,
            -0.199,
            -0.4,
            0.5,
            4.0,
            -0.099,
            0.6,
            -0.4,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.0, "z": -1.000, "mg": 0.1, "ca": 0.2},
            {"teff": 5000, "logg": 4.0, "z": -0.899, "mg": 0.2, "ca": 0.1},
            {"teff": 5000, "logg": 4.0, "z": -0.799, "mg": 0.3, "ca": 0.0},
            {"teff": 5000, "logg": 4.0, "z": -0.699, "mg": 0.0, "ca": -0.1},
            {"teff": 5000, "logg": 4.0, "z": -0.599, "mg": -0.1, "ca": -0.2},
            {"teff": 5000, "logg": 4.0, "z": -0.499, "mg": -0.2, "ca": 0.3},
            {"teff": 5000, "logg": 4.0, "z": -0.399, "mg": 0.4, "ca": -0.3},
            {"teff": 5000, "logg": 4.0, "z": -0.299, "mg": 0.5, "ca": 0.4},
            {"teff": 5000, "logg": 4.0, "z": -0.199, "mg": -0.4, "ca": 0.5},
            {"teff": 5000, "logg": 4.0, "z": -0.099, "mg": 0.6, "ca": -0.4},
        ]
        with patch("random.randint", side_effect=randint_values), patch(
            "random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 5 for parameter_set in result))
            self.assertEqual(result, expected)

    def test_validate_new_set_no_collision(self):
        new_set = (5300, 4.3, -0.7, 0.4, 0.5)
        result = parameter_generation._validate_new_set(
            *new_set, self.existing_parameters
        )
        self.assertTrue(result, "The new set should be valid, no collisions expected.")

    def test_validate_new_set_collision(self):
        new_set = (5000, 4.0, -1.0, 0.1, 0.2)
        result = parameter_generation._validate_new_set(
            *new_set, self.existing_parameters
        )
        self.assertFalse(
            result,
            "The new set should be invalid due to collision with an existing set.",
        )

    def test_validate_new_set_partial_collision(self):
        new_set = (5000, 4.1, -1.0, 0.1, 0.2)
        result = parameter_generation._validate_new_set(
            *new_set, self.existing_parameters
        )
        self.assertTrue(
            result,
            "The new set should be valid, only partial collision in teff and logg.",
        )

    def test_validate_new_set_almost_full_collision(self):
        new_set = (5100, 4.1, -0.9, 0.2, 0.0)
        result = parameter_generation._validate_new_set(
            *new_set, self.existing_parameters
        )
        self.assertTrue(
            result,
            "The new set should be valid, ca is not within the minimum delta.",
        )

    def test_validate_new_set_close_but_no_collision(self):
        new_set = (5050, 4.05, -0.95, 0.15, 0.25)
        result = parameter_generation._validate_new_set(
            *new_set, self.existing_parameters
        )
        self.assertTrue(
            result,
            "The new set should be valid, no parameter within the minimum delta.",
        )

    @patch("source.parameter_generation.random.randint")
    @patch("source.parameter_generation.random.uniform")
    def test_generate_random_parameters_no_conflicts(self, mock_randint, mock_uniform):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameter when there are no conflicting parameter values
        Obs: This test is sensitive regarding the number of parameters to generate. If num_spectra in config is changed, the expected values must be updated, and the mock numbers
        """
        # Set up mock values
        # Teff
        randint_values = [
            5000,
            5005,
            5010,
            5015,
            5020,
            5025,
            5030,
            5035,
            5040,
            5045,
        ]
        # Logg, z, mg, and ca, interleaved
        uniform_values = [
            4.00,
            -1.000,
            0.1,
            0.2,
            4.11,
            -0.833,
            0.15,
            0.25,
            4.22,
            -0.667,
            0.2,
            0.3,
            4.33,
            -0.500,
            0.25,
            0.35,
            4.44,
            -0.333,
            0.3,
            0.4,
            4.56,
            -0.167,
            0.35,
            0.45,
            4.67,
            0.000,
            0.4,
            0.5,
            4.78,
            0.167,
            0.45,
            0.55,
            4.89,
            0.333,
            0.5,
            0.6,
            5.00,
            0.500,
            0.55,
            0.65,
        ]
        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000, "mg": 0.1, "ca": 0.2},
            {"teff": 5005, "logg": 4.11, "z": -0.833, "mg": 0.15, "ca": 0.25},
            {"teff": 5010, "logg": 4.22, "z": -0.667, "mg": 0.2, "ca": 0.3},
            {"teff": 5015, "logg": 4.33, "z": -0.500, "mg": 0.25, "ca": 0.35},
            {"teff": 5020, "logg": 4.44, "z": -0.333, "mg": 0.3, "ca": 0.4},
            {"teff": 5025, "logg": 4.56, "z": -0.167, "mg": 0.35, "ca": 0.45},
            {"teff": 5030, "logg": 4.67, "z": 0.000, "mg": 0.4, "ca": 0.5},
            {"teff": 5035, "logg": 4.78, "z": 0.167, "mg": 0.45, "ca": 0.55},
            {"teff": 5040, "logg": 4.89, "z": 0.333, "mg": 0.5, "ca": 0.6},
            {"teff": 5045, "logg": 5.00, "z": 0.500, "mg": 0.55, "ca": 0.65},
        ]
        with patch(
            "source.parameter_generation.random.randint", side_effect=randint_values
        ), patch(
            "source.parameter_generation.random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 5 for parameter_set in result))
            self.assertEqual(result, expected)

    @patch("source.parameter_generation.read_parameters_from_file")
    def test_generate_parameters_read_from_file(self, mock_read_parameters_from_file):
        """
        Test that the function calls read_parameters_from_file when read_stellar_parameters_from_file is True
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.read_stellar_parameters_from_file = True
        parameter_generation.generate_parameters(config)
        mock_read_parameters_from_file.assert_called_once_with(config)

    @patch("source.parameter_generation.generate_random_parameters")
    def test_generate_parameters_random(self, mock_generate_random_parameters):
        """
        Test that the function calls generate_random_parameters when read_stellar_parameters_from_file is False and random_parameters is True
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.read_stellar_parameters_from_file = False
        config.random_parameters
        parameter_generation.generate_parameters(config)
        mock_generate_random_parameters.assert_called_once_with(config)

    def test_generate_evenly_spaced_parameters(self):
        config = Configuration("tests/test_input/configuration.cfg")
        config.random_parameters = False
        config.num_points_teff = 10
        config.num_points_logg = 8
        config.num_points_z = 5
        config.num_points_mg = 5
        config.num_points_ca = 5

        expected_teff = np.round(np.linspace(5000, 7000, 10))
        expected_logg = np.round(np.linspace(4.0, 5.0, 8), 2)
        expected_z = np.round(np.linspace(-1.0, 0.5, 5), 3)
        expected_mg = np.round(np.linspace(-0.8, 1.2, 5), 3)
        expected_ca = np.round(np.linspace(-0.8, 1.2, 5), 3)

        result = parameter_generation.generate_evenly_spaced_parameters(config)
        result_teff = {param["teff"] for param in result}
        result_logg = {param["logg"] for param in result}
        result_z = {param["z"] for param in result}
        result_mg = {param["mg"] for param in result}
        result_ca = {param["ca"] for param in result}

        np.testing.assert_equal(sorted(result_teff), sorted(expected_teff))
        np.testing.assert_equal(sorted(result_logg), sorted(expected_logg))
        np.testing.assert_equal(sorted(result_z), sorted(expected_z))
        np.testing.assert_equal(sorted(result_mg), sorted(expected_mg))
        np.testing.assert_equal(sorted(result_ca), sorted(expected_ca))

        self.assertEqual(
            len(result),
            len(expected_teff)
            * len(expected_logg)
            * len(expected_z)
            * len(expected_mg)
            * len(expected_ca),
        )
