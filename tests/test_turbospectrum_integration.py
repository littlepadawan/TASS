import unittest
from unittest.mock import patch, MagicMock
import subprocess
from configuration_setup import Configuration
import turbospectrum_integration


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
