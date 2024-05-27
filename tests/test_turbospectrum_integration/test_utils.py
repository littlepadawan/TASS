import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from pandas.testing import assert_frame_equal
from source.turbospectrum_integration import utils as utils
from tests.model_atmospheres_data_for_testing import FILENAMES


class TestUtils(unittest.TestCase):

    # Parse the filenames of the model atmospheres used for testing
    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(utils.parse_model_atmosphere_filename(filename))

    def test_parse_model_atmosphere_filename_match(self):
        """
        Test that the expected parameters are returned
        if the filename matches the pattern.
        """
        filename = "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
        expected_output = {
            "teff": 6000,
            "logg": 4.0,
            "z": -2.00,
            "alpha": 0.40,
            "teff_str": "6000",
            "turbulence_str": "02",
            "logg_str": "+4.0",
            "z_str": "-2.00",
            "alpha_str": "+0.40",
            "filename": "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod",
        }

        output = utils.parse_model_atmosphere_filename(filename)

        self.assertEqual(output, expected_output)

    def test_parse_model_atmosphere_filename_no_match(self):
        """
        Test that None is returned if the filename does
        not match the pattern.
        """
        # The filename starts with 's' instead of 'p'
        filename = "s6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
        expected_output = None

        output = utils.parse_model_atmosphere_filename(filename)

        self.assertEqual(output, expected_output)

    @patch("source.turbospectrum_integration.utils.parse_model_atmosphere_filename")
    @patch("source.turbospectrum_integration.utils.listdir")
    def test_collect_model_atmosphere_parameters(self, mock_listdir, mock_parse):
        """
        Test that the expected DataFrame is returned
        when collecting the parameters of the model atmospheres.
        (This test takes quite a long time to run)
        """

        # Add a random file, that does not match the patter, to the list of filenames
        FILENAMES.append("random_file.doc")

        # Mock the directory content
        mock_listdir.return_value = FILENAMES

        # Mock the 'parse_model_atmosphere_filename' behaviou
        def parse_side_effect(filename):
            for item in self.PARSED_FILENAMES:
                if item["filename"] == filename:
                    return item
            return None

        mock_parse.side_effect = parse_side_effect

        # Expected parameters
        expected = pd.DataFrame(self.PARSED_FILENAMES)

        result = utils.collect_model_atmosphere_parameters("dummy_directory")

        assert_frame_equal(result, expected)
        FILENAMES.remove("random_file.doc")
