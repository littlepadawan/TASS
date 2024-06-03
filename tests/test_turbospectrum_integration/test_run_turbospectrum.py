import unittest
from subprocess import PIPE
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
from source.configuration_setup import Configuration
from source.turbospectrum_integration import utils
from source.turbospectrum_integration.configuration import TurbospectrumConfiguration
from source.turbospectrum_integration.run_turbospectrum import (
    generate_all_spectra,
    generate_one_spectrum,
    run_babsma,
    run_bsyn,
)
from tests.model_atmospheres_data_for_testing import FILENAMES


class TestRunTurbospectrum(unittest.TestCase):

    # TODO: Remove these later
    # Parse the filenames of the model atmospheres used for testing
    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(utils.parse_model_atmosphere_filename(filename))

    MODEL_ATMOSPHERES = pd.DataFrame(PARSED_FILENAMES)

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("source.turbospectrum_integration.run_turbospectrum.run")
    @patch("source.turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("source.turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_babsma_success(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        """Test that run_babsma runs successfully"""
        # Set up the return values for getcwd and run
        mock_getcwd.return_value = "/current/directory"
        mock_run.return_value = MagicMock(stdout="mock stdout", stderr="mock stderr")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_babsma = "path/to/babsma"
        ts_config.file_name = "mock_file_name"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"
        config.path_output_directory = "path/to/output"

        # Call the function
        run_babsma(ts_config, config)

        # Check that getcwd and chdir were called
        mock_getcwd.assert_called_once()
        mock_chdir.assert_any_call("path/to/turbospectrum")
        mock_chdir.assert_any_call("/current/directory")

        # Check that subprocess.run was called with the expected arguments
        mock_run.assert_called_once_with(
            ["path/to/turbospectrum_compiled/babsma_lu"],
            stdin=mock_open(),
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("source.turbospectrum_integration.run_turbospectrum.run")
    @patch("source.turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("source.turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_babsma_failure(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and mock run to raise an error
        mock_getcwd.return_value = "/current/directory"
        mock_run.side_effect = Exception("mock error")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_babsma = "path/to/babsma"
        ts_config.file_name = "mock_file_name"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"
        config.path_output_directory = "path/to/output"

        # Use assertRaises to check for the exception
        with self.assertRaises(Exception) as context:
            run_babsma(ts_config, config)

        # Verify the exception message
        self.assertEqual(str(context.exception), "mock error")

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("source.turbospectrum_integration.run_turbospectrum.run")
    @patch("source.turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("source.turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_bsyn(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and run
        mock_getcwd.return_value = "/current/directory"
        mock_run.return_value = MagicMock(stdout="mock stdout", stderr="mock stderr")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_bsyn = "path/to/bsyn"
        ts_config.file_name = "mock_file_name"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"
        config.path_output_directory = "path/to/output"

        # Call the function
        run_bsyn(ts_config, config)

        # Check that getcwd and chdir were called
        mock_getcwd.assert_called_once()
        mock_chdir.assert_any_call("path/to/turbospectrum")
        mock_chdir.assert_any_call("/current/directory")

        # Check that subprocess.run was called with the expected arguments
        mock_run.assert_called_once_with(
            ["path/to/turbospectrum_compiled/bsyn_lu"],
            stdin=mock_open(),
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("source.turbospectrum_integration.run_turbospectrum.run")
    @patch("source.turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("source.turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_bsyn_raises_error(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and mock run to raise an error
        mock_getcwd.return_value = "/current/directory"
        mock_run.side_effect = Exception("mock error")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_bsyn = "path/to/bsyn"
        ts_config.file_name = "mock_file_name"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"
        config.path_output_directory = "path/to/output"

        # Use assertRaises to check for the exception
        with self.assertRaises(Exception) as context:
            run_bsyn(ts_config, config)

        # Verify the exception message
        self.assertEqual(str(context.exception), "mock error")

    @patch(
        "source.turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "source.turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_TurbospectrumConfiguration,
    ):
        # Set up mock return values
        mock_config_instance = MagicMock()
        mock_TurbospectrumConfiguration.return_value = mock_config_instance
        mock_config_instance.alpha = 0.1
        mock_needs_interpolation.return_value = (True, ["matching_model"])
        mock_generate_interpolated_model_atmosphere.return_value = (
            "path/to/interpolated_model",
            None,
        )

        # Create mock configuration objects
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "path/to/output"
        stellar_parameters = {"teff": 5700, "logg": 4.5, "z": 0.0, "mg": 0.1, "ca": 0.2}
        model_atmospheres = pd.DataFrame(
            {"teff": [5500, 5800], "logg": [4.3, 4.6], "z": [-0.5, 0.0]}
        )

        # Call the function
        generate_one_spectrum(config, stellar_parameters, model_atmospheres)

        # Verify that the mocks were called with the correct arguments
        mock_TurbospectrumConfiguration.assert_called_once_with(
            config, stellar_parameters
        )
        mock_needs_interpolation.assert_called_once_with(
            stellar_parameters, 0.1, model_atmospheres
        )
        mock_generate_interpolated_model_atmosphere.assert_called_once_with(
            stellar_parameters, 0.1, config, model_atmospheres
        )
        mock_create_babsma.assert_called_once_with(
            config, mock_TurbospectrumConfiguration.return_value, stellar_parameters
        )
        mock_run_babsma.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config
        )
        mock_create_bsyn.assert_called_once_with(
            config, mock_TurbospectrumConfiguration.return_value, stellar_parameters
        )
        mock_run_bsyn.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config
        )

    @patch(
        "source.turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "source.turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum_no_interpolation(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_TurbospectrumConfiguration,
    ):
        # Set up mock return values
        mock_config_instance = MagicMock()
        mock_TurbospectrumConfiguration.return_value = mock_config_instance
        mock_config_instance.alpha = 0.1
        mock_needs_interpolation.return_value = (False, ["matching_model"])

        # Create mock configuration objects
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "path/to/output"
        stellar_parameters = {"teff": 5700, "logg": 4.5, "z": 0.0}
        model_atmospheres = ["model1", "model2"]

        # Call the function
        generate_one_spectrum(config, stellar_parameters, model_atmospheres)

        # Verify that the mocks were called with the correct arguments
        mock_TurbospectrumConfiguration.assert_called_once_with(
            config, stellar_parameters
        )
        mock_needs_interpolation.assert_called_once_with(
            stellar_parameters, 0.1, model_atmospheres
        )
        mock_generate_interpolated_model_atmosphere.assert_not_called()
        mock_create_babsma.assert_called_once_with(
            config, mock_TurbospectrumConfiguration.return_value, stellar_parameters
        )
        mock_run_babsma.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config
        )
        mock_create_bsyn.assert_called_once_with(
            config, mock_TurbospectrumConfiguration.return_value, stellar_parameters
        )
        mock_run_bsyn.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config
        )

    # TODO: Clean this up
    @patch(
        "source.turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "source.turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("source.turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("source.turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("source.turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum_multiple_matching_models(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_TurbospectrumConfiguration,
    ):
        # Set up mock return values
        mock_TurbospectrumConfiguration.return_value = MagicMock()
        mock_needs_interpolation.return_value = (False, ["model1", "model2"])

        # Create mock configuration objects
        config = MagicMock(spec=Configuration)
        config.path_output_directory = "path/to/output"
        stellar_parameters = {"teff": 5700, "logg": 4.5, "z": 0.0}
        model_atmospheres = ["model1", "model2"]

        # Use assertRaises to check for the exception
        with self.assertRaises(ValueError) as context:
            generate_one_spectrum(config, stellar_parameters, model_atmospheres)

        # Verify the exception message
        self.assertEqual(str(context.exception), "More than one matching model found")

    @patch("source.turbospectrum_integration.run_turbospectrum.generate_one_spectrum")
    def test_generate_all_spectr(self, mock_generate_one_spectrum):
        """
        Test that generate_all_spectra runs successfully with expected arguments
        """
        # Create a mock Configuration object
        config = MagicMock(spec=Configuration)

        # Create a mock DataFrame for model atmospheres
        model_atmospheres = MagicMock(spec=pd.DataFrame)

        # Define the stellar parameters
        stellar_parameters = (
            {"teff": 5700, "logg": 4.5, "z": 0.0},
            {"teff": 5715, "logg": 4.7, "z": 0.26},
            {"teff": 5800, "logg": 4.6, "z": 0.1},
            {"teff": 5900, "logg": 4.8, "z": 0.2},
            {"teff": 6000, "logg": 4.9, "z": 0.3},
        )

        # Call the function
        generate_all_spectra(config, model_atmospheres, stellar_parameters)

        # Verify that generate_one_spectrum was called with the expected arguments
        expected_calls = [
            unittest.mock.call(config, stellar_parameters[0], model_atmospheres),
            unittest.mock.call(config, stellar_parameters[1], model_atmospheres),
            unittest.mock.call(config, stellar_parameters[2], model_atmospheres),
            unittest.mock.call(config, stellar_parameters[3], model_atmospheres),
            unittest.mock.call(config, stellar_parameters[4], model_atmospheres),
        ]

        mock_generate_one_spectrum.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(mock_generate_one_spectrum.call_count, len(stellar_parameters))
