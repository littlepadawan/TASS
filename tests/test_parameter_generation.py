import os
import unittest
from shutil import rmtree
from unittest.mock import MagicMock, patch

import numpy as np
import source.parameter_generation as parameter_generation
from source.configuration_setup import Configuration


class TestParameterGeneration(unittest.TestCase):
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
            f.write("interpolator = ./tests/test_input/turbospectrum/interpolator\n")
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
            f.write("num_spectra = 10\n")
            f.write("teff_min = 5000\n")
            f.write("teff_max = 7000\n")
            f.write("logg_min = 4.0\n")
            f.write("logg_max = 5.0\n")
            f.write("z_min = -1.0\n")
            f.write("z_max = 0.5\n")
            f.write("[Turbospectrum_settings]\n")
            f.write("xit = 1.0\n")

        # Create file with stellar parameters for testing
        with open("tests/test_input/input_parameters.txt", "w") as f:
            f.write("teff logg z\n")
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
                {"teff": "7957", "logg": "4.91", "z": "-0.425"},
                {"teff": "5952", "logg": "2.71", "z": "-0.014"},
                {"teff": "3543", "logg": "1.19", "z": "-2.573"},
                {"teff": "3837", "logg": "5.41", "z": "0.258"},
                {"teff": "3070", "logg": "2.50", "z": "-4.387"},
                {"teff": "3862", "logg": "4.79", "z": "-1.686"},
                {"teff": "6897", "logg": "2.45", "z": "-0.636"},
                {"teff": "2920", "logg": "3.03", "z": "-3.941"},
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

    def test_generate_random_parameters_no_distance_check(self):
        """
        Test that the correct number of random stellar parameters are generated,
        and that they are within bounds
        """
        config = Configuration("tests/test_input/configuration.cfg")
        stellar_parameters = (
            parameter_generation.generate_random_parameters_no_distance_check(config)
        )
        self.assertEqual(len(stellar_parameters), 10)
        for parameters in stellar_parameters:
            self.assertGreaterEqual(int(parameters[0]), 5000)
            self.assertLessEqual(int(parameters[0]), 7000)
            self.assertGreaterEqual(float(parameters[1]), 4.0)
            self.assertLessEqual(float(parameters[1]), 5.0)
            self.assertGreaterEqual(float(parameters[2]), -2.0)
            self.assertLessEqual(float(parameters[2]), 0.5)

    def test_generate_random_parameters_no_distance_check_1000(self):
        """
        Test that 1000 random stellar parameters are generated,
        and that they are within bounds
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 1000
        stellar_parameters = (
            parameter_generation.generate_random_parameters_no_distance_check(config)
        )
        self.assertEqual(len(stellar_parameters), 1000)

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
        Test that the function successfully adds 10 randomly generated sets of stellar parameter when there are no conflicting parameter values
        Obs: This test is sensitive regarding the number of parmeters to generate. If num_spectra in config is changed, the expected values must be updated, and the mock numbers
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
        # Logg and z, interleaved
        uniform_values = [
            4.00,
            -1.000,
            4.11,
            -0.833,
            4.22,
            -0.667,
            4.33,
            -0.500,
            4.44,
            -0.333,
            4.56,
            -0.167,
            4.67,
            0.000,
            4.78,
            0.167,
            4.89,
            0.333,
            5.00,
            0.500,
        ]
        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000},
            {"teff": 5005, "logg": 4.11, "z": -0.833},
            {"teff": 5010, "logg": 4.22, "z": -0.667},
            {"teff": 5015, "logg": 4.33, "z": -0.500},
            {"teff": 5020, "logg": 4.44, "z": -0.333},
            {"teff": 5025, "logg": 4.56, "z": -0.167},
            {"teff": 5030, "logg": 4.67, "z": 0.000},
            {"teff": 5035, "logg": 4.78, "z": 0.167},
            {"teff": 5040, "logg": 4.89, "z": 0.333},
            {"teff": 5045, "logg": 5.00, "z": 0.500},
        ]
        with patch(
            "source.parameter_generation.random.randint", side_effect=randint_values
        ), patch(
            "source.parameter_generation.random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 3 for parameter_set in result))

            self.assertEqual(result, expected)

    @patch("random.randint")
    @patch("random.uniform")
    def test_generate_random_parameters_with_teff_collisions(
        self, mock_randint, mock_uniform
    ):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameter when there are conflicting teff values, but no collisions in logg and z values
        """
        # Set up mock values
        # Teff value collides, same value every time

        randint_values = [5000] * 10
        # Logg and z values, each set of values does not collide within the specified range
        uniform_values = [
            4.00,
            -1.000,
            4.06,
            -0.899,
            4.12,
            -0.799,
            4.18,
            -0.699,
            4.24,
            -0.599,
            4.30,
            -0.499,
            4.36,
            -0.399,
            4.42,
            -0.299,
            4.48,
            -0.199,
            4.54,
            -0.099,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.00, "z": -1.000},
            {"teff": 5000, "logg": 4.06, "z": -0.899},
            {"teff": 5000, "logg": 4.12, "z": -0.799},
            {"teff": 5000, "logg": 4.18, "z": -0.699},
            {"teff": 5000, "logg": 4.24, "z": -0.599},
            {"teff": 5000, "logg": 4.30, "z": -0.499},
            {"teff": 5000, "logg": 4.36, "z": -0.399},
            {"teff": 5000, "logg": 4.42, "z": -0.299},
            {"teff": 5000, "logg": 4.48, "z": -0.199},
            {"teff": 5000, "logg": 4.54, "z": -0.099},
        ]
        with patch("random.randint", side_effect=randint_values), patch(
            "random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 3 for parameter_set in result))
            self.assertEqual(result, expected)

    @patch("random.randint")
    @patch("random.uniform")
    def test_generate_random_parameters_with_teff_and_logg_collisions(
        self, mock_randint, mock_uniform
    ):
        """
        Test that the function successfully adds 10 randomly generated sets of stellar parameter when there are conflicting teff and logg values, but no collisions in z values
        """
        # Set up mock values
        # Teff value collides, same value every time
        randint_values = [5000] * 10
        # Logg value collides, same value every time
        # z values, each set of values does not collide within the specified range
        uniform_values = [
            4.0,
            -1.000,
            4.0,
            -0.899,
            4.0,
            -0.799,
            4.0,
            -0.699,
            4.0,
            -0.599,
            4.0,
            -0.499,
            4.0,
            -0.399,
            4.0,
            -0.299,
            4.0,
            -0.199,
            4.0,
            -0.099,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.0, "z": -1.000},
            {"teff": 5000, "logg": 4.0, "z": -0.899},
            {"teff": 5000, "logg": 4.0, "z": -0.799},
            {"teff": 5000, "logg": 4.0, "z": -0.699},
            {"teff": 5000, "logg": 4.0, "z": -0.599},
            {"teff": 5000, "logg": 4.0, "z": -0.499},
            {"teff": 5000, "logg": 4.0, "z": -0.399},
            {"teff": 5000, "logg": 4.0, "z": -0.299},
            {"teff": 5000, "logg": 4.0, "z": -0.199},
            {"teff": 5000, "logg": 4.0, "z": -0.099},
        ]
        with patch("random.randint", side_effect=randint_values), patch(
            "random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 3 for parameter_set in result))
            self.assertEqual(result, expected)

    @patch("random.randint")
    @patch("random.uniform")
    def test_generate_random_parameters_full_collision(
        self, mock_randint, mock_uniform
    ):
        """
        TODO: Change this comment, it is not accurate
        Test that the function only adds the first set when all subsequent sets are within the min delta for each parameter.
        """
        # Values close to each other, within the minimum delta range
        randint_values = [
            5000,
            5004,
            5002,
            5003,
            5001,
            5050,
            5060,
            5070,
            5080,
            5090,
            5100,
            5110,
            5120,
            5130,
            5140,
            5150,
            5160,
            5170,
            5180,
            5190,
        ]
        uniform_values = [
            4.0,
            -0.5,
            4.03,
            -0.4997,
            4.04,
            -0.4999,
            4.02,
            -0.4998,
            4.05,
            -0.4996,  # First 5 sets are close to the first, potential collisions
            4.10,
            -0.450,
            4.15,
            -0.400,
            4.20,
            -0.350,
            4.25,
            -0.300,
            4.30,
            -0.250,
            4.35,
            -0.200,
            4.40,
            -0.150,
            4.45,
            -0.100,
            4.50,
            -0.050,
            4.55,
            0.0,
            4.60,
            0.05,
            4.65,
            0.10,
            4.70,
            0.15,
        ]

        config = Configuration("tests/test_input/configuration.cfg")
        expected = [
            {"teff": 5000, "logg": 4.0, "z": -0.5},
            {"teff": 5050, "logg": 4.10, "z": -0.450},
            {"teff": 5060, "logg": 4.15, "z": -0.400},
            {"teff": 5070, "logg": 4.20, "z": -0.350},
            {"teff": 5080, "logg": 4.25, "z": -0.300},
            {"teff": 5090, "logg": 4.30, "z": -0.250},
            {"teff": 5100, "logg": 4.35, "z": -0.200},
            {"teff": 5110, "logg": 4.40, "z": -0.150},
            {"teff": 5120, "logg": 4.45, "z": -0.100},
            {"teff": 5130, "logg": 4.50, "z": -0.050},
        ]  # Only the first set should be added due to collision within min deltas

        with patch("random.randint", side_effect=randint_values), patch(
            "random.uniform", side_effect=uniform_values
        ):
            result = parameter_generation.generate_random_parameters(config)
            self.assertEqual(len(result), 10)
            self.assertTrue(all(len(parameter_set) == 3 for parameter_set in result))
            self.assertEqual(result, expected)

    def test_generate_evenly_spaced_output_size_perfect_fit(self):
        """
        Test that output size matches the requested number of spectra when it fits perfectly
        I.e. num_spectra = intervals^dimensions
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 1000
        result = parameter_generation.generate_evenly_spaced_parameters(config)
        self.assertEqual(len(result), 1000)

    def test_generate_evenly_spaced_output_size_just_above(self):
        """
        Test that output size matches the requested number of spectra when the requested number is just above "a perfect square
        I.e. num_spectra = intervals^dimensions + 1
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 103
        result = parameter_generation.generate_evenly_spaced_parameters(config)
        self.assertEqual(len(result), 103)

    def test_generate_evenly_spaced_output_size_just_below(self):
        """
        Test that output size matches the requested number of spectra when the requested number is just below "a perfect square
        I.e. num_spectra = intervals^dimensions - 1
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 80
        result = parameter_generation.generate_evenly_spaced_parameters(config)
        self.assertEqual(len(result), 80)

    def test_generate_evenly_spaced_parameters_value_distribution(self):
        """
            Test if the values are evenly spaced within their ranges
                np.diff(unique_teffs): This calculates the difference between consecutive elements in unique_teffs, giving you an array of differences (or steps) between the values.
        np.diff(unique_teffs)[0]: This is the first difference in the array. You're comparing every other difference against this first difference to check if they are all approximately equal.
        atol=1e-2: You are allowing a difference of up to 0.01 between the first difference and every subsequent difference, regardless of the scale of the numbers involved.
        rtol=1e-5: You are also allowing a relative error of 0.00001, scaled by the absolute size of the first difference.
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.num_spectra = 64
        result = parameter_generation.generate_evenly_spaced_parameters(config)
        teff_values, logg_values, z_values = zip(*result)

        unique_teffs = sorted(set(teff_values))
        unique_loggs = sorted(set(logg_values))
        unique_zs = sorted(set(z_values))

        # Check that the step size are consistent
        self.assertTrue(
            np.allclose(
                np.diff(unique_teffs),
                np.diff(unique_teffs)[0],
                atol=1,
                rtol=0,
            )
        )
        print("Logg Values:", unique_teffs)

        print("Differences:", np.diff(unique_teffs))
        print("First Difference:", np.diff(unique_teffs)[0])
        self.assertTrue(
            np.allclose(
                np.diff(unique_loggs),
                np.diff(unique_loggs)[0],
                atol=0.01,
                rtol=0,
            )
        )
        self.assertTrue(
            np.allclose(
                np.diff(unique_zs),
                np.diff(unique_zs)[0],
                atol=0.001,
                rtol=0,
            )
        )

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

    @patch("source.parameter_generation.generate_evenly_spaced_parameters")
    def test_generate_parameters_evenly_spaced(
        self, mock_generate_evenly_spaced_parameters
    ):
        """
        Test that the function calls generate_evenly_spaced_parameters when read_stellar_parameters_from_file is False and random_parameters is False
        """
        config = Configuration("tests/test_input/configuration.cfg")
        config.read_stellar_parameters_from_file = False
        config.random_parameters = False
        parameter_generation.generate_parameters(config)
        mock_generate_evenly_spaced_parameters.assert_called_once_with(config)
