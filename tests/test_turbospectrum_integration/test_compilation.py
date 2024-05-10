import unittest
from os import getcwd
from subprocess import CalledProcessError
from unittest.mock import MagicMock, call, patch

import pandas as pd
from configuration_setup import Configuration
from tests.model_atmospheres_data_for_testing import FILENAMES
from turbospectrum_integration import compilation, utils


class TestInterpolate(unittest.TestCase):

    # Parse the filenames of the model atmospheres used for testing
    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(utils._parse_model_atmosphere_filename(filename))

    MODEL_GRID = pd.DataFrame(PARSED_FILENAMES)

    def setUp(self):
        # Set up a fresh Configuration object for each test
        self.config = Configuration()

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_compile_turboscpectrum_success(self, mock_run, mock_chdir):
        """Test that Turbospectrum compiles successfully."""

        # Mock subprocess.run to simulate a successful command
        mock_run.return_value = MagicMock(returncode=0)

        compilation.compile_turbospectrum(self.config)

        # Check if subprocess.run was called correclty
        mock_run.assert_called_once_with(
            ["make"], check=True, text=True, capture_output=True
        )
        # Check if os.chdir was called correctly
        mock_chdir.assert_has_calls(
            [call(self.config.path_turbospectrum_compiled), call(getcwd())]
        )

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_compile_turbospectrum_failure(self, mock_run, mock_chdir):
        """Test that an error is raised if Turbospectrum compilation fails."""

        # Mock subprocess.run to simulate a failed command
        mock_run.side_effect = CalledProcessError(1, "make", "Error")

        with self.assertRaises(CalledProcessError):
            compilation.compile_turbospectrum(self.config)

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_return_to_original_directory_after_compile_turbospectrum(
        self, mock_run, mock_chdir
    ):
        """
        Test that the working directory is changed back to the original
        directory after compiling Turbospectrum
        """

        original_directory = "/original/directory"
        with patch(
            "turbospectrum_integration.compilation.getcwd",
            return_value=original_directory,
        ):
            compilation.compile_turbospectrum(self.config)

        # Make sure os.chdir is called to return to the original directory
        mock_chdir.assert_called_with(original_directory)

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_compile_interpolator_success(self, mock_run, mock_chdir):
        """Test that the interpolator is compiled successfully."""
        # Command to compile interpolator (copied from turbospectrum_integration/compilation.py)
        command = ["gfortran", "-o", "interpol_modeles", "interpol_modeles.f"]

        # Mock subprocess.run to simulate a successful command
        mock_run.return_value = MagicMock(returncode=0)

        compilation.compile_interpolator(self.config)

        # Check if subprocess.run was called correclty
        mock_run.assert_called_once_with(
            command, check=True, text=True, capture_output=True
        )

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_compile_interpolator_failure(self, mock_run, mock_chdir):
        """Test that an error is raised if the interpolator compilation fails."""
        # Command to compile interpolator (copied from turbospectrum_integration/compilation.py)
        command = ["gfortran", "-o", "interpol_modeles", "interpol_modeles.f"]

        # Mock subprocess.run to simulate a failed command
        mock_run.side_effect = CalledProcessError(1, command, "Error")

        with self.assertRaises(CalledProcessError):
            compilation.compile_interpolator(self.config)

    @patch("turbospectrum_integration.compilation.chdir")
    @patch("turbospectrum_integration.compilation.run", autospec=True)
    def test_return_to_original_directory_after_compile_interpolator(
        self, mock_run, mock_chdir
    ):
        """
        Test that the working directory is changed back to the original directory after compiling the interpolator
        """
        original_directory = "/original/directory"
        with patch(
            "turbospectrum_integration.compilation.getcwd",
            return_value=original_directory,
        ):
            compilation.compile_interpolator(self.config)

        # Make sure os.chdir is called to return to the original directory
        mock_chdir.assert_called_with(original_directory)
