import unittest
from subprocess import PIPE
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
from configuration_setup import Configuration
from tests.model_atmospheres_data_for_testing import FILENAMES
from turbospectrum_integration import utils
from turbospectrum_integration.configuration import TurbospectrumConfiguration
from turbospectrum_integration.run_turbospectrum import (
    generate_one_spectrum,
    run_babsma,
    run_bsyn,
)


class TestRunTurbospectrum(unittest.TestCase):

    # TODO: Remove these later
    # Parse the filenames of the model atmospheres used for testing
    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(utils.parse_model_atmosphere_filename(filename))

    MODEL_ATMOSPHERES = pd.DataFrame(PARSED_FILENAMES)

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("turbospectrum_integration.run_turbospectrum.run")
    @patch("turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_babsma_success(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        """Test that run_babsma runs successfully"""
        # Set up the return values for getcwd and run
        mock_getcwd.return_value = "/current/directory"
        mock_run.return_value = MagicMock(stdout="mock stdout", stderr="mock stderr")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_babsma = "path/to/babsma"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"

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
    @patch("turbospectrum_integration.run_turbospectrum.run")
    @patch("turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_babsma_failure(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and mock run to raise an error
        mock_getcwd.return_value = "/current/directory"
        mock_run.side_effect = Exception("mock error")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_babsma = "path/to/babsma"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"

        # Use assertRaises to check for the exception
        with self.assertRaises(Exception) as context:
            run_babsma(ts_config, config)

        # Verify the exception message
        self.assertEqual(str(context.exception), "mock error")

    @patch("builtins.open", new_callable=mock_open, read_data="mock data")
    @patch("turbospectrum_integration.run_turbospectrum.run")
    @patch("turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_bsyn(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and run
        mock_getcwd.return_value = "/current/directory"
        mock_run.return_value = MagicMock(stdout="mock stdout", stderr="mock stderr")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_bsyn = "path/to/bsyn"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"

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
    @patch("turbospectrum_integration.run_turbospectrum.run")
    @patch("turbospectrum_integration.run_turbospectrum.getcwd")
    @patch("turbospectrum_integration.run_turbospectrum.chdir")
    def test_run_bsyn_raises_error(self, mock_chdir, mock_getcwd, mock_run, mock_open):
        # Set up the return values for getcwd and mock run to raise an error
        mock_getcwd.return_value = "/current/directory"
        mock_run.side_effect = Exception("mock error")

        # Create mock configuration objects
        ts_config = MagicMock(spec=TurbospectrumConfiguration)
        ts_config.path_bsyn = "path/to/bsyn"

        config = MagicMock(spec=Configuration)
        config.path_turbospectrum = "path/to/turbospectrum"
        config.path_turbospectrum_compiled = "path/to/turbospectrum_compiled"

        # Use assertRaises to check for the exception
        with self.assertRaises(Exception) as context:
            run_bsyn(ts_config, config)

        # Verify the exception message
        self.assertEqual(str(context.exception), "mock error")

    @patch("turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_model_opac")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_result_file")
    @patch("turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_generate_path_result_file,
        mock_generate_path_model_opac,
        mock_TurbospectrumConfiguration,
    ):
        # Set up mock return values
        mock_TurbospectrumConfiguration.return_value = MagicMock()
        mock_needs_interpolation.return_value = (True, ["matching_model"])
        mock_generate_interpolated_model_atmosphere.return_value = (
            "path/to/interpolated_model"
        )

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
        mock_generate_path_model_opac.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config, stellar_parameters
        )
        mock_generate_path_result_file.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config, stellar_parameters
        )
        mock_needs_interpolation.assert_called_once_with(
            stellar_parameters, model_atmospheres
        )
        mock_generate_interpolated_model_atmosphere.assert_called_once_with(
            stellar_parameters, config
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

    @patch("turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_model_opac")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_result_file")
    @patch("turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum_no_interpolation(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_generate_path_result_file,
        mock_generate_path_model_opac,
        mock_TurbospectrumConfiguration,
    ):
        # Set up mock return values
        mock_TurbospectrumConfiguration.return_value = MagicMock()
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
        mock_generate_path_model_opac.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config, stellar_parameters
        )
        mock_generate_path_result_file.assert_called_once_with(
            mock_TurbospectrumConfiguration.return_value, config, stellar_parameters
        )
        mock_needs_interpolation.assert_called_once_with(
            stellar_parameters, model_atmospheres
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
    @patch("turbospectrum_integration.run_turbospectrum.TurbospectrumConfiguration")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_model_opac")
    @patch("turbospectrum_integration.run_turbospectrum.generate_path_result_file")
    @patch("turbospectrum_integration.run_turbospectrum.needs_interpolation")
    @patch(
        "turbospectrum_integration.run_turbospectrum.generate_interpolated_model_atmosphere"
    )
    @patch("turbospectrum_integration.run_turbospectrum.create_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.run_babsma")
    @patch("turbospectrum_integration.run_turbospectrum.create_bsyn")
    @patch("turbospectrum_integration.run_turbospectrum.run_bsyn")
    def test_generate_one_spectrum_multiple_matching_models(
        self,
        mock_run_bsyn,
        mock_create_bsyn,
        mock_run_babsma,
        mock_create_babsma,
        mock_generate_interpolated_model_atmosphere,
        mock_needs_interpolation,
        mock_generate_path_result_file,
        mock_generate_path_model_opac,
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

    def test_generate_one_spectrum_actual(self):
        config = Configuration()
        stellar_parameters = {
            "teff": 5715,
            "logg": 4.7,
            "z": 0.26,
            "Mg": 0.0,
            "Ca": 0.0,
        }

        generate_one_spectrum(config, stellar_parameters, self.MODEL_ATMOSPHERES)
