import unittest
from unittest.mock import patch, MagicMock
import subprocess
from configuration_setup import Configuration
import turbospectrum_integration
from model_atmospheres_data_for_testing import FILENAMES


class TestTurbospectrumIntegration(unittest.TestCase):

    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(
            turbospectrum_integration._parse_model_atmosphere_filename(filename)
        )

    MODEL_GRID = turbospectrum_integration._create_model_grid(PARSED_FILENAMES)

    def setUp(self):
        # Set up a Configuration object
        self.config = Configuration()

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_compile_turbospectrum_success(self, mock_run, mock_chdir):
        """
        Test that Turbospectrum is compiled successfully
        """
        # Mock subprocess.run to simulate a successful command
        mock_run.return_value = MagicMock(returncode=0)

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
        # Mock subprocess.run to simulate a failed command
        mock_run.side_effect = subprocess.CalledProcessError(1, "make", "Error")

        with self.assertRaises(subprocess.CalledProcessError):
            turbospectrum_integration.compile_turbospectrum(self.config)

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_return_to_original_directory_after_compile_turbospectrum(
        self, mock_run, mock_chdir
    ):
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

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_compile_interpolator_success(self, mock_run, mock_chdir):
        """
        Test that the interpolator is compiled successfully
        """
        # Command to compile interpolator
        # Copied from turbospectrum_integration.py
        command = ["gfortran", "-o", "interpol_modeles", "interpol_modeles.f"]
        # Mock subprocess.run to somulate a successful command
        mock_run.return_value = MagicMock(returncode=0)

        turbospectrum_integration.compile_interpolator(self.config)

        # Check if subprocess.run was called correclty
        mock_run.assert_called_once_with(
            command, check=True, text=True, capture_output=True
        )

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_compile_interpolator_failure(self, mock_run, mock_chdir):
        """
        Test that an error is raised if the interpolator compilation fails
        """
        # Command to compile interpolator
        # Copied from turbospectrum_integration.py
        command = ["gfortran", "-o", "interpol_modeles", "interpol_modeles.f"]
        # Mock subprocess.run to simulate a failed command
        mock_run.side_effect = subprocess.CalledProcessError(1, command, "Error")

        with self.assertRaises(subprocess.CalledProcessError):
            turbospectrum_integration.compile_interpolator(self.config)

    @patch("turbospectrum_integration.os.chdir")
    @patch("turbospectrum_integration.subprocess.run")
    def test_return_to_original_directory_after_compile_interpolator(
        self, mock_run, mock_chdir
    ):
        """
        Test that the working directory is changed back to the original directory after compiling the interpolator
        """
        original_directory = "/original/directory"
        with patch(
            "turbospectrum_integration.os.getcwd", return_value=original_directory
        ):
            turbospectrum_integration.compile_interpolator(self.config)

        # Make sure os.chdir is called to return to the original directory
        mock_chdir.assert_called_with(original_directory)

    def test_parse_model_atmosphere_filename_match(self):
        """
        Test that the model atmosphere filename is parsed correctly and returns the expected parameters if the filename matches the pattern
        """
        filename = "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
        expected_output = {
            "teff": "6000",
            "logg": "+4.0",
            "feh": "-2.00",
            "filename": "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod",
        }

        output = turbospectrum_integration._parse_model_atmosphere_filename(filename)
        # print(output)
        self.assertEqual(output, expected_output)

    def test_parse_model_atmosphere_filename_no_match(self):
        """
        Test that the model atmosphere filename is parsed correctly and returns None if the filename does not match the pattern
        """
        filename = "s6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
        expected_output = None

        output = turbospectrum_integration._parse_model_atmosphere_filename(filename)
        self.assertEqual(output, expected_output)

    @patch("turbospectrum_integration.os.listdir")
    @patch("turbospectrum_integration._parse_model_atmosphere_filename")
    def test_extract_parameters_from_filenames(self, mock_parse, mock_listdir):
        FILENAMES.append("random_file.doc")

        # Mock the directory content
        mock_listdir.return_value = FILENAMES

        # Expected grid
        expected_grid = self.PARSED_FILENAMES

        # Set up the mock to return a different directory for each file
        mock_parse.side_effect = lambda x: next(
            (item for item in expected_grid if item["filename"] == x), None
        )

        result = turbospectrum_integration._extract_parameters_from_filenames(
            "dummy_directory"
        )

        self.assertEqual(result, expected_grid)
        FILENAMES.remove("random_file.doc")

    def test_create_model_grid(self):
        pass

    def test_find_bracketing_models(self):
        parameters = {"teff": 5210, "logg": 4.3, "feh": 0.05}
        models = turbospectrum_integration._find_bracketing_models(
            parameters, self.MODEL_GRID
        )
        # for model in models:
        #     print(model)

    def test_needs_interpolation(self):
        pass

    def test_create_template_interpolator_script(self):
        parameters = {"teff": 5710, "logg": 4.6, "feh": 0.25}
        turbospectrum_integration.compile_interpolator(self.config)
        turbospectrum_integration.create_template_interpolator_script(self.config)
        turbospectrum_integration.generate_interpolated_model_atmosphere(
            self.config, parameters
        )

    def test_create_babsma(self):
        parameters = {"teff": 5710, "logg": 4.6, "feh": 0.25}
        turbospectrum_integration.compile_turbospectrum(self.config)
        turbospectrum_integration.compile_interpolator(self.config)
        all_models = turbospectrum_integration._extract_parameters_from_filenames(
            self.config.path_model_atmospheres
        )
        model_grid = turbospectrum_integration._create_model_grid(all_models)
        turbospectrum_integration.create_template_interpolator_script(self.config)
        turbospectrum_integration.generate_one_spectrum(
            self.config, parameters, model_grid
        )
