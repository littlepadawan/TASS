import unittest
from unittest.mock import MagicMock, mock_open, patch

import source.output_management as output_management
from source.configuration_setup import Configuration


class TestOutputManagement(unittest.TestCase):

    @patch("source.output_management.makedirs")
    @patch("source.output_management.datetime")
    def test_set_up_output_directory(self, mock_datetime, mock_makedirs):
        """
        Test that the output directory is created with the correct name and a subdirectory for temp files
        """
        # Mock the current date and time
        mock_now = mock_datetime.now.return_value
        mock_now.strftime.return_value = "2024-05-04@12:00"

        # Create a mock Configuration object
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "/path/to/output"

        # Call the function
        output_management.set_up_output_directory(config)

        # Versify that the paths are generated correctly
        expected_output_directory = "/path/to/output/2024-05-04@12:00"
        expected_temp_directory = "/path/to/output/2024-05-04@12:00/temp"

        self.assertEqual(config.path_output_directory, expected_output_directory)

        # Verify that os.makedirs was called with the correct arguments
        mock_makedirs.assert_any_call(expected_output_directory)
        mock_makedirs.assert_any_call(expected_temp_directory)

    @patch("source.output_management.copyfile")
    def test_copy_config_file(self, mock_copyfile):
        """
        Test that the configuration file is copied to the output directory
        """
        # Create a mock Configuration object
        config = MagicMock(spec=Configuration)
        config.path_config = "/path/to/config"
        config.path_output_directory = "/path/to/output"

        # Call the function
        output_management.copy_config_file(config)

        # Verify that os.copyfile was called with the correct arguments
        mock_copyfile.assert_called_once_with("/path/to/config", "/path/to/output")

    @patch("source.output_management.open", new_callable=mock_open)
    def test_generate_parameter_file(self, mock_open):
        """
        Test that the parameter file is generated correctly
        """
        # Create a mock Configuration object
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "/path/to/output"

        # Define parameter sets
        successful_parameters = [
            {"Teff": 5000, "logg": 4.5, "FeH": 0.0},
            {"Teff": 6000, "logg": 4.0, "FeH": -0.5},
        ]
        no_files_found_for_interpolation = [
            {"Teff": 7000, "logg": 4.5, "FeH": 0.0},
            {"Teff": 8000, "logg": 4.0, "FeH": -0.5},
        ]
        multiple_files_found_for_interpolation = [
            {"Teff": 9000, "logg": 4.5, "FeH": 0.0},
            {"Teff": 10000, "logg": 4.0, "FeH": -0.5},
        ]

        # Call the function
        output_management.generate_parameter_file(
            config,
            successful_parameters,
            no_files_found_for_interpolation,
            multiple_files_found_for_interpolation,
        )

        # Get file handle from mock
        file_handle = mock_open.return_value.__enter__.return_value

        # Define expexted file content
        expected_content = (
            "----------------------------------------\n"
            "No spectrum generated because files\n"
            "needed for interpolation were not found:\n"
            "----------------------------------------\n"
            f"{no_files_found_for_interpolation[0]}\n"
            f"{no_files_found_for_interpolation[1]}\n"
            "\n\n----------------------------------------\n"
            "No spectrum generated because multiple\n"
            "matching model atmospheres were found\n"
            "for interpolation:\n"
            "----------------------------------------\n"
            f"{multiple_files_found_for_interpolation[0]}\n"
            f"{multiple_files_found_for_interpolation[1]}\n"
            "\n\n----------------------------------------\n"
            "Spectra generated:\n"
            "----------------------------------------\n"
            f"{successful_parameters[0]}\n"
            f"{successful_parameters[1]}\n"
        )

        # Verify that the file was written with the correct content
        file_handle.write.assert_any_call("----------------------------------------\n")
        file_handle.write.assert_any_call("No spectrum generated because files\n")
        file_handle.write.assert_any_call("needed for interpolation were not found:\n")
        file_handle.write.assert_any_call("----------------------------------------\n")
        file_handle.write.assert_any_call(f"{no_files_found_for_interpolation[0]}\n")
        file_handle.write.assert_any_call(f"{no_files_found_for_interpolation[1]}\n")
        file_handle.write.assert_any_call(
            "\n\n----------------------------------------\n"
        )
        file_handle.write.assert_any_call("No spectrum generated because multiple\n")
        file_handle.write.assert_any_call("matching model atmospheres were found\n")
        file_handle.write.assert_any_call("for interpolation:\n")
        file_handle.write.assert_any_call("----------------------------------------\n")
        file_handle.write.assert_any_call(
            f"{multiple_files_found_for_interpolation[0]}\n"
        )
        file_handle.write.assert_any_call(
            f"{multiple_files_found_for_interpolation[1]}\n"
        )
        file_handle.write.assert_any_call(
            "\n\n----------------------------------------\n"
        )
        file_handle.write.assert_any_call("Spectra generated:\n")
        file_handle.write.assert_any_call(f"{successful_parameters[0]}\n")
        file_handle.write.assert_any_call(f"{successful_parameters[1]}\n")

    @patch("source.output_management.open", new_callable=mock_open)
    def test_generate_parameter_file_only_successful_parameters(self, mock_open):
        """
        Test that the parameter file is generated correctly when
        there were only successfull parameters passed
        """
        # Create a mock Configuration object
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "/path/to/output"

        # Define parameter sets
        successful_parameters = [
            {"Teff": 5000, "logg": 4.5, "FeH": 0.0},
            {"Teff": 6000, "logg": 4.0, "FeH": -0.5},
        ]
        no_files_found_for_interpolation = []
        multiple_files_found_for_interpolation = []

        # Call the function
        output_management.generate_parameter_file(
            config,
            successful_parameters,
            no_files_found_for_interpolation,
            multiple_files_found_for_interpolation,
        )

        # Get file handle from mock
        file_handle = mock_open.return_value.__enter__.return_value

        # Define expexted file content
        expected_content = (
            "\n\n----------------------------------------\n"
            "Spectra generated:\n"
            "----------------------------------------\n"
            f"{successful_parameters[0]}\n"
            f"{successful_parameters[1]}\n"
        )

        # Verify that the file was written with the correct content
        file_handle.write.assert_any_call(
            "\n\n----------------------------------------\n"
        )
        file_handle.write.assert_any_call("Spectra generated:\n")
        file_handle.write.assert_any_call("----------------------------------------\n")
        file_handle.write.assert_any_call(f"{successful_parameters[0]}\n")
        file_handle.write.assert_any_call(f"{successful_parameters[1]}\n")
