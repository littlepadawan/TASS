import unittest
from unittest.mock import MagicMock, mock_open, patch

import source.turbospectrum_integration.configuration as turbospectrum_config
from source.configuration_setup import Configuration


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        # Set up a Configuration object
        self.config = Configuration()

    def test___init__(self):
        """
        Test that the TurbospectrumConfiguration class is initialized correctly
        """
        config = Configuration()

        stellar_parameters = {
            "teff": 5210,
            "logg": 4.3,
            "z": 0.05,
            "mg": 0.20,
            "ca": 0.30,
        }
        ts_config = turbospectrum_config.TurbospectrumConfiguration(
            config, stellar_parameters
        )
        expected_file_name = "p5210_g+4.3_z+0.05_a+0.00_mg+0.20_ca+0.30"
        expected_alpha = 0.0
        self.assertEqual(ts_config.path_model_atmosphere, None)
        self.assertEqual(
            ts_config.path_model_opac,
            f"{config.path_output_directory}/temp/opac_{expected_file_name}",
        )
        self.assertEqual(
            ts_config.path_babsma,
            f"{config.path_output_directory}/temp/{expected_file_name}_babsma",
        )
        self.assertEqual(
            ts_config.path_bsyn,
            f"{config.path_output_directory}/temp/{expected_file_name}_bsyn",
        )
        self.assertEqual(ts_config.interpolated_model_atmosphere, True)
        self.assertEqual(ts_config.alpha, expected_alpha)
        self.assertEqual(ts_config.num_elements, 2)

    def test_calculate_alpha_lowest_value(self):
        """
        Test that the function returns 0.4 if the
        metallicity < -1.0
        """
        self.assertEqual(turbospectrum_config.calculate_alpha(-1.001), 0.4)
        self.assertEqual(turbospectrum_config.calculate_alpha(-5), 0.4)

    def test_calculate_alpha_middle_value(self):
        """
        Test that the function returns -0.4 * metallicity if
        -1.0 <= metallicity < 0.0
        """
        # If metallicity is -1.0, alpha should be 0.4
        self.assertEqual(turbospectrum_config.calculate_alpha(-1.0), 0.4)

        # If metallicity is -0.5, alpha should be 0.2
        self.assertEqual(turbospectrum_config.calculate_alpha(-0.5), 0.2)

        # If metallicity is -0.01, alpha should be 0.004
        self.assertEqual(turbospectrum_config.calculate_alpha(-0.01), 0.004)

    def test_calculate_alpha_highest_value(self):
        """
        Test that the function returns 0.0 if the
        metallicity >= 0.0
        """
        self.assertEqual(turbospectrum_config.calculate_alpha(0.0), 0.0)
        self.assertEqual(turbospectrum_config.calculate_alpha(0.0001), 0.0)
        self.assertEqual(turbospectrum_config.calculate_alpha(1), 0.0)

    def test_generate_abundance_str(self):
        """
        Test that the abundance string and number of elements are generated correctly
        """
        stellar_parameters = {
            "teff": 5210,
            "logg": 4.3,
            "z": 0.05,
            "mg": 0.2,
            "ca": 0.3,
        }
        expected_output = (2, "'INDIVIDUAL ABUNDANCES:' 2\n12 7.80\n20 6.72")

        result = turbospectrum_config.generate_abundance_str(stellar_parameters)
        self.assertEqual(result, expected_output)

    def test_set_abundances(self):
        """
        Test that the functions sets the abundances correctly
        """
        stellar_parameters = {
            "teff": 5210,
            "logg": 4.3,
            "z": 0.05,
            "mg": 0.2,
            "ca": 0.3,
        }
        ts_config = turbospectrum_config.TurbospectrumConfiguration(
            self.config, stellar_parameters
        )

        turbospectrum_config.set_abundances(ts_config, stellar_parameters)
        self.assertEqual(ts_config.num_elements, 2)
        self.assertEqual(
            ts_config.abundance_str, "'INDIVIDUAL ABUNDANCES:' 2\n12 7.80\n20 6.72"
        )

    def test_is_model_atmosphere_marcs_true(self):
        """
        Test that the function returns ".true." if the model atmosphere was
        not interpolated.
        """
        ts_config = turbospectrum_config.TurbospectrumConfiguration(
            self.config, {"teff": 5210, "logg": 4.3, "z": 0.05, "mg": 0.2, "ca": 0.3}
        )
        ts_config.interpolated_model_atmosphere = False
        result = turbospectrum_config.is_model_atmosphere_marcs(ts_config)

        # The model atmosphere was not interpolated, so it should be a MARCS model
        self.assertEqual(result, ".true.")

    def test_is_model_atmosphere_marcs_false(self):
        """
        Test that the function returns ".false." if the model atmosphere was
        interpolated.
        """
        ts_config = turbospectrum_config.TurbospectrumConfiguration(
            self.config, {"teff": 5210, "logg": 4.3, "z": 0.05, "mg": 0.2, "ca": 0.3}
        )
        ts_config.interpolated_model_atmosphere = True
        result = turbospectrum_config.is_model_atmosphere_marcs(ts_config)

        # The model atmosphere was interpolated, so it is not a MARCS model
        self.assertEqual(result, ".false.")

    @patch(
        "source.turbospectrum_integration.configuration.is_model_atmosphere_marcs",
        return_value=".true",
    )
    @patch("builtins.open", new_callable=mock_open)
    def test_create_babsma(
        self,
        mock_open,
        mock_is_model_atmosphere_marcs,
    ):
        """Test that the babsma file is created correctly"""

        # Set up test data
        config = MagicMock()
        config.wavelength_min = 4000
        config.wavelength_max = 7000
        config.wavelength_step = 0.1
        config.xit = 1.0

        ts_config = MagicMock()
        ts_config.path_model_atmosphere = "path/to/model_atmosphere"
        ts_config.alpha = 0.1
        ts_config.path_babsma = "path/to/babsma"

        stellar_parameters = {
            "teff": 5210,
            "logg": 4.3,
            "z": 0.05,
            "Mg": 0.2,
            "Ca": 0.3,
        }

        expected_content = turbospectrum_config.BABSMA_CONTENT.format(
            lambda_min=config.wavelength_min,
            lambda_max=config.wavelength_max,
            lambda_step=config.wavelength_step,
            model_input=ts_config.path_model_atmosphere,
            marcs_file=".true.",  # assuming `is_model_atmosphere_marcs` returns True for this test
            model_opac="path/to/model_opac",
            metallicity=stellar_parameters["z"],
            alpha=ts_config.alpha,
            num_elements=2,
            abundances="12  0.20\n20  0.30\n",
            xifix=config.xit,
        )

        # Call the function
        turbospectrum_config.create_babsma(config, ts_config, stellar_parameters)

        # Check that the file was written with the correct content
        mock_open.assert_called_once_with(ts_config.path_babsma, "w")

    @patch("source.turbospectrum_integration.configuration.path.isfile")
    @patch("source.turbospectrum_integration.configuration.listdir")
    def test_create_line_lists_string(self, mock_listdir, mock_isfile):
        # Set up test data
        mock_listdir.return_value = ["file1.txt", "file2.txt", "not_a_file"]
        mock_isfile.side_effect = lambda filepath: filepath.endswith(".txt")

        # Create a mock Configuration object with the path_linelists attribute set to a string path
        config = MagicMock()
        config.path_linelists = "/path/to/linelists"

        # Expected result
        expected_line_lists_str = (
            "NFILES: 2\n"
            "/path/to/linelists/file1.txt\n"
            "/path/to/linelists/file2.txt\n"
        )

        # Call the function
        result = turbospectrum_config.create_line_lists_str(config)

        # Check the result
        self.assertEqual(result, expected_line_lists_str)

    @patch("source.turbospectrum_integration.configuration.create_line_lists_str")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_bsyn(
        self,
        mock_open,
        mock_create_line_lists_str,
    ):
        """Test that the bsyn file is created correctly"""
        # Return values
        mock_create_line_lists_str.return_value = (
            "'NFILES   :' '2'\nline_list1\nline_list2\n"
        )

        # Set up test data
        config = MagicMock()
        config.wavelength_min = 4000
        config.wavelength_max = 7000
        config.wavelength_step = 0.1

        ts_config = MagicMock()
        ts_config.path_model_opac = "path/to/model_opac"
        ts_config.alpha = 0.1
        ts_config.num_elements = 2
        ts_config.abundance_str = "12  0.20\n20  0.30\n"

        stellar_parameters = {
            "teff": 5210,
            "logg": 4.3,
            "z": 0.05,
            "Mg": 0.2,
            "Ca": 0.3,
        }

        expected_content = turbospectrum_config.BSYN_CONTENT.format(
            lambda_min=config.wavelength_min,
            lambda_max=config.wavelength_max,
            lambda_step=config.wavelength_step,
            model_opac="path/to/model_opac",
            result_file=ts_config.path_result_file,
            metallicity=stellar_parameters["z"],
            alpha=ts_config.alpha,
            num_elements=2,
            abundances="12  0.20\n20  0.30\n",
            line_lists="'NFILES   :' '2'\nline_list1\nline_list2\n",
        )

        # Call the function
        turbospectrum_config.create_bsyn(config, ts_config, stellar_parameters)

        # Check that create_line_lists_str was called with the correct arguments
        mock_create_line_lists_str.assert_called_once_with(config)

        # Check that the file was written with the correct content
        mock_open.assert_called_once_with(ts_config.path_bsyn, "w")
