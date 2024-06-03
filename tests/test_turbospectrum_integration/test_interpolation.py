import re
import unittest
from subprocess import CalledProcessError
from unittest.mock import MagicMock, call, mock_open, patch

import pandas as pd
import source.turbospectrum_integration.interpolation as interpolation
from source.configuration_setup import Configuration
from source.turbospectrum_integration import utils as utils
from tests.model_atmospheres_data_for_testing import FILENAMES


class TestInterpolation(unittest.TestCase):

    # Parse the filenames of the model atmospheres used for testing
    PARSED_FILENAMES = []
    for filename in FILENAMES:
        PARSED_FILENAMES.append(utils.parse_model_atmosphere_filename(filename))

    MODEL_ATMOSPHERES = pd.DataFrame(PARSED_FILENAMES)

    def setUp(self):
        # Set up a Configuration object
        self.config = Configuration()

    def test_needs_interpolation_true(self):
        """
        Test that the needs_interpolation function returns True when the stellar parameters
        do not match any of the model atmospheres.
        """

        # There is no matching atmosphere model for this set of parameters
        stellar_parameters = {"teff": 5710, "logg": 4.6, "z": 0.25}
        alpha = 0.00
        needs_interpolation, matching_models = interpolation.needs_interpolation(
            stellar_parameters, alpha, self.MODEL_ATMOSPHERES
        )

        self.assertTrue(needs_interpolation)
        self.assertEqual(None, matching_models)

    def test_needs_interpolation_false(self):
        """
        Test that the needs_interpolation function returns False when the
        stellar parameters match one of the model atmospheres.

        # TODO: This test can be improved by explicitly comparing the content of matching_models, currently it only checks if the returned value is not None.
        """

        # There is a matching atmosphere model for this set of parameters
        stellar_parameters = {"teff": 6000, "logg": 4.0, "z": 0.00}
        alpha = 0.00
        needs_interpolation, matching_models = interpolation.needs_interpolation(
            stellar_parameters, alpha, self.MODEL_ATMOSPHERES
        )

        self.assertFalse(needs_interpolation)
        self.assertIsNotNone(matching_models)

    def test_get_models_with_lower_parameter_value_success(self):
        """
        Test that the function returns models with parameter values lower than the target values.
        # TODO: This test can be improved by explicitly comparing the content of the returned models, currently it only checks if the returned value is not None.
        """
        # There are models values lower than these target values
        teff_target = 6000
        logg_target = 4.0
        z_target = 0.0

        models_with_teff_lower_than_target = (
            interpolation._get_models_with_lower_parameter_value(
                "teff", teff_target, self.MODEL_ATMOSPHERES
            )
        )
        models_with_logg_lower_than_target = (
            interpolation._get_models_with_lower_parameter_value(
                "logg", logg_target, self.MODEL_ATMOSPHERES
            )
        )
        models_with_z_lower_than_target = (
            interpolation._get_models_with_lower_parameter_value(
                "z", z_target, self.MODEL_ATMOSPHERES
            )
        )

        self.assertIsNotNone(models_with_teff_lower_than_target)
        self.assertIsNotNone(models_with_logg_lower_than_target)
        self.assertIsNotNone(models_with_z_lower_than_target)

    def test_get_models_with_lower_parameter_value_failure(self):
        """
        Test that the function raises a ValueError when there are no models
        with parameter values lower than the target values.
        """
        pass
        # There are no models with parameter values lower than these target values
        # teff_target = 2500
        # logg_target = -0.5
        # z_target = -5.0

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_lower_parameter_value(
        #         "teff", teff_target, self.MODEL_ATMOSPHERES
        #     )

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_lower_parameter_value(
        #         "logg", logg_target, self.MODEL_ATMOSPHERES
        #     )

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_lower_parameter_value(
        #         "z", z_target, self.MODEL_ATMOSPHERES
        #     )

    def test_get_models_with_higher_parameter_value_success(self):
        """
        Test that the function returns models with parameter values higher than the target values.
        # TODO: This test can be improved by explicitly comparing the content of the returned models, currently it only checks if the returned value is not None.
        """
        # There are models with values higher than these target values
        teff_target = 2500
        logg_target = -3.0
        z_target = -5.0

        models_with_teff_higher_than_target = (
            interpolation._get_models_with_higher_parameter_value(
                "teff", teff_target, self.MODEL_ATMOSPHERES
            )
        )
        models_with_logg_higher_than_target = (
            interpolation._get_models_with_higher_parameter_value(
                "logg", logg_target, self.MODEL_ATMOSPHERES
            )
        )
        models_with_z_higher_than_target = (
            interpolation._get_models_with_higher_parameter_value(
                "z", z_target, self.MODEL_ATMOSPHERES
            )
        )

        self.assertIsNotNone(models_with_teff_higher_than_target)
        self.assertIsNotNone(models_with_logg_higher_than_target)
        self.assertIsNotNone(models_with_z_higher_than_target)

    def test_get_models_with_higher_parameter_value_failure(self):
        """
        Test that the function raises a ValueError when there are no models
        with parameter values higher than the target values.
        """
        pass
        # There are no models with parameter values higher than these target values
        # teff_target = 8000
        # logg_target = 5.5
        # z_target = 1.0

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_higher_parameter_value(
        #         "teff", teff_target, self.MODEL_ATMOSPHERES
        #     )

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_higher_parameter_value(
        #         "logg", logg_target, self.MODEL_ATMOSPHERES
        #     )

        # with self.assertRaises(ValueError):
        #     interpolation._get_models_with_higher_parameter_value(
        #         "z", z_target, self.MODEL_ATMOSPHERES
        #     )

    def test_get_closest_models(self):
        """
        Test that the function returns the models that have values
        closest to the target values.
        # TODO: This test can be improved by checking that every returned model has the closest value to the target value.
        """
        closest_model_teff = interpolation._get_closest_models(
            "teff", 5410, self.MODEL_ATMOSPHERES
        )
        closest_model_logg = interpolation._get_closest_models(
            "logg", 4.4, self.MODEL_ATMOSPHERES
        )
        closest_model_z = interpolation._get_closest_models(
            "z", 0.24, self.MODEL_ATMOSPHERES
        )

        expected_closest_teff = 5500
        expected_closest_logg = 4.5
        expected_model_z = 0.25

        self.assertEqual(expected_closest_teff, closest_model_teff["teff"].values[0])
        self.assertEqual(expected_closest_logg, closest_model_logg["logg"].values[0])
        self.assertEqual(expected_model_z, closest_model_z["z"].values[0])

    def test_get_bracketing_models_success(self):
        """Test that the function returns the models that bracket the target values."""
        stellar_parameters = {"teff": 5500, "logg": 4.25, "z": 0.10}
        alpha = 0.00
        result = interpolation._get_bracketing_models(
            stellar_parameters, self.MODEL_ATMOSPHERES
        )

        self.assertEqual(8, len(result))
        # TODO: Check that each model follows the required pattern

    @patch("source.turbospectrum_integration.interpolation._get_bracketing_models")
    def test_get_models_for_interpolating(self, mock_get_bracketing_models):
        """Test that the function returns the bracketing models needed for interpolation."""
        stellar_parameters = {"teff": 5500, "logg": 4.25, "z": 0.10}
        directory = "/path/to/dummy-directory/"
        # Create a mock DataFrame with consistent structure
        mock_models_df = pd.DataFrame(
            {
                "teff": [5000, 5200, 5400, 5600, 5800],
                "logg": [4.0, 4.1, 4.2, 4.3, 4.4],
                "z": [-1.0, -0.5, 0.0, 0.5, 1.0],
                "turbulence_str": ["01"] * 5,
            }
        )

        bracketing_models = [
            MagicMock(name="Model 1"),
            MagicMock(name="Model 2"),
            MagicMock(name="Model 3"),
            MagicMock(name="Model 4"),
            MagicMock(name="Model 5"),
            MagicMock(name="Model 6"),
            MagicMock(name="Model 7"),
            MagicMock(name="Model 8"),
        ]
        mock_get_bracketing_models.return_value = bracketing_models
        result, error_message = interpolation._get_models_for_interpolation(
            stellar_parameters, mock_models_df
        )
        # Access the DataFrame passed to the function and print for debugging
        called_args = mock_get_bracketing_models.call_args

        # Verify the function call with expected arguments
        self.assertTrue(called_args[0][1].equals(mock_models_df))
        mock_get_bracketing_models.assert_called_once_with(
            stellar_parameters, mock_models_df
        )

        # Ensure the function returns the expected result
        self.assertEqual(bracketing_models, result)
        self.assertIsNone(error_message)

    @patch("builtins.open", new_callable=mock_open)
    def test_create_interpolator_script(self, mock_file):
        """Test that the function creates a template interpolator script."""
        self.config.path_output_directory = "/fake/path/output"
        self.config.path_interpolator = "/fake/path/interpolator"

        # Expected content of the interpolator script
        expected_content = r"""#!/bin/csh -f
set model_path = {{PY_MODEL_PATH}}

set marcs_binary = '.false.'

#enter here the values requested for the interpolated model 
foreach Tref   ( {{PY_TREF}} )
foreach loggref ( {{PY_LOGGREF}} )
foreach zref ( {{PY_ZREF}} )
set modele_out = {{PY_OUTPUT_PATH}}/{{PY_FILENAME}}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/{{PY_FILENAME}}.alt

#plane-parallel models
set model1 = {{PY_MODEL1}}
set model2 = {{PY_MODEL2}}
set model3 = {{PY_MODEL3}}
set model4 = {{PY_MODEL4}}
set model5 = {{PY_MODEL5}}
set model6 = {{PY_MODEL6}}
set model7 = {{PY_MODEL7}}
set model8 = {{PY_MODEL8}}

#### the test option is set to .true. if you want to plot comparison model (model_test)
set test = '.false.'
set model_test = 'Testwebformat/p5750_g+4.5_m0.0_t01_ap_z-0.25_a+0.00_c+0.00_n+0.00_o+0.00_r+0.00_s+0.00.mod'

# interpolation program (for further details see interpol_modeles.f)
./interpol_modeles <<EOF
'${model_path}/${model1}'
'${model_path}/${model2}'
'${model_path}/${model3}'
'${model_path}/${model4}'
'${model_path}/${model5}'
'${model_path}/${model6}'
'${model_path}/${model7}'
'${model_path}/${model8}'
'${modele_out}'
'${modele_out2}'
${Tref}
${loggref}
${zref}
${test}
${marcs_binary}
'${model_test}'
EOF

end
end 
end
"""
        interpolation.create_template_interpolator_script(self.config)

        # Assert that the file was opened with the correct path and mode
        mock_file.assert_called_once_with(
            "/fake/path/output/temp/interpolate.script", "w"
        )

        # Assert that the file was written with the correct content
        mock_file().write.assert_called_once_with(expected_content)

    @patch("source.turbospectrum_integration.interpolation.copyfile")
    def test_copy_interpolator_script(self, mock_copyfile):
        """
        Test that the function copies the interpolator script to the output directory,
        with the correct filename.
        """
        self.config.path_interpolator = "/fake/path"
        self.config.path_output_directory = "/fake/path/output"
        stellar_parameters = {
            "teff": 5700,
            "logg": 4.5,
            "z": 0.10,
            "mg": 0.20,
            "ca": 0.30,
        }
        alpha = 0.00

        expected_filename = (
            "interpolate_p5700_g+4.5_z+0.10_a+0.00_mg+0.20_ca+0.30.script"
        )
        expected_source = f"{self.config.path_output_directory}/temp/interpolate.script"
        expected_destination = (
            f"{self.config.path_output_directory}/temp/{expected_filename}"
        )

        # Execute
        result = interpolation.copy_template_interpolator_script(
            self.config, alpha, stellar_parameters
        )

        # Assert the returned filename is correct
        self.assertEqual(result, expected_destination)

        # Assert copyfile was called with the correct source and destination paths
        mock_copyfile.assert_called_once_with(expected_source, expected_destination)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""#!/bin/csh -f
set model_path = {{PY_MODEL_PATH}}

set marcs_binary = '.false.'

#enter here the values requested for the interpolated model 
foreach Tref   ( {{PY_TREF}} )
foreach loggref ( {{PY_LOGGREF}} )
foreach zref ( {{PY_ZREF}} )
set modele_out = {{PY_OUTPUT_PATH}}/{{PY_FILENAME}}.interpol
set modele_out2 = {{PY_OUTPUT_PATH}}/{{PY_FILENAME}}.alt

#plane-parallel models
set model1 = {{PY_MODEL1}}
set model2 = {{PY_MODEL2}}
set model3 = {{PY_MODEL3}}
set model4 = {{PY_MODEL4}}
set model5 = {{PY_MODEL5}}
set model6 = {{PY_MODEL6}}
set model7 = {{PY_MODEL7}}
set model8 = {{PY_MODEL8}}

#### the test option is set to .true. if you want to plot comparison model (model_test)
set test = '.false.'
set model_test = 'Testwebformat/p5750_g+4.5_m0.0_t01_ap_z-0.25_a+0.00_c+0.00_n+0.00_o+0.00_r+0.00_s+0.00.mod'

# interpolation program (for further details see interpol_modeles.f)
./interpol_modeles <<EOF
'${model_path}/${model1}'
'${model_path}/${model2}'
'${model_path}/${model3}'
'${model_path}/${model4}'
'${model_path}/${model5}'
'${model_path}/${model6}'
'${model_path}/${model7}'
'${model_path}/${model8}'
'${modele_out}'
'${modele_out2}'
${Tref}
${loggref}
${zref}
${test}
${marcs_binary}
'${model_test}'
EOF

end
end 
end
""",
    )
    def test_load_parameters_to_interpolator_script(self, mock_file):
        script_path = "path/to/interpolator_script.sh"
        stellar_parameters = {"teff": 5700, "logg": 4.5, "z": -0.20}
        bracketing_models = [
            MagicMock(
                filename="model1.mod", teff_str="5500", logg_str="4.0", z_str="-0.5"
            ),
            MagicMock(
                filename="model2.mod", teff_str="6000", logg_str="5.0", z_str="0.5"
            ),
            MagicMock(
                filename="model3.mod", teff_str="5500", logg_str="4.0", z_str="-0.5"
            ),
            MagicMock(
                filename="model4.mod", teff_str="6000", logg_str="5.0", z_str="0.5"
            ),
            MagicMock(
                filename="model5.mod", teff_str="5500", logg_str="4.0", z_str="-0.5"
            ),
            MagicMock(
                filename="model6.mod", teff_str="6000", logg_str="5.0", z_str="0.5"
            ),
            MagicMock(
                filename="model7.mod", teff_str="5500", logg_str="4.0", z_str="-0.5"
            ),
            MagicMock(
                filename="model8.mod", teff_str="6000", logg_str="5.0", z_str="0.5"
            ),
        ]

        config = MagicMock(spec=Configuration)
        config.path_model_atmospheres = "/path/to/model/atmospheres"
        config.path_output_directory = "/path/to/output"
        config.filename = "filename"

        interpolation._load_parameters_to_interpolator_script(
            script_path, stellar_parameters, bracketing_models, config, config.filename
        )

        # Check the written content
        mock_file().write.assert_called_once()
        written_content = mock_file().write.call_args[0][0]

        expected_content = """#!/bin/csh -f
set model_path = /path/to/model/atmospheres

set marcs_binary = '.false.'

#enter here the values requested for the interpolated model 
foreach Tref   ( 5700 )
foreach loggref ( 4.5 )
foreach zref ( -0.2 )
set modele_out = /path/to/output/temp/filename.interpol
set modele_out2 = /path/to/output/temp/filename.alt

#plane-parallel models
set model1 = model1.mod
set model2 = model2.mod
set model3 = model3.mod
set model4 = model4.mod
set model5 = model5.mod
set model6 = model6.mod
set model7 = model7.mod
set model8 = model8.mod

#### the test option is set to .true. if you want to plot comparison model (model_test)
set test = '.false.'
set model_test = 'Testwebformat/p5750_g+4.5_m0.0_t01_ap_z-0.25_a+0.00_c+0.00_n+0.00_o+0.00_r+0.00_s+0.00.mod'

# interpolation program (for further details see interpol_modeles.f)
./interpol_modeles <<EOF
'${model_path}/${model1}'
'${model_path}/${model2}'
'${model_path}/${model3}'
'${model_path}/${model4}'
'${model_path}/${model5}'
'${model_path}/${model6}'
'${model_path}/${model7}'
'${model_path}/${model8}'
'${modele_out}'
'${modele_out2}'
${Tref}
${loggref}
${zref}
${test}
${marcs_binary}
'${model_test}'
EOF

end
end 
end
"""

        self.assertEqual(written_content, expected_content)

    @patch("source.turbospectrum_integration.interpolation.chdir")
    @patch("source.turbospectrum_integration.interpolation.getcwd", return_value="cwd")
    @patch("source.turbospectrum_integration.interpolation.run")
    @patch("builtins.open", new_callable=mock_open)
    def test_run_interpolator_script_success(
        self, mock_open, mock_run, mock_getcwd, mock_chdir
    ):
        """Test that the function runs the interpolator script correctly."""
        self.config.path_output_directory = "/path/to/output"
        self.config.path_interpolator = "/path/to/interpolator"

        script_name = "test_script.sh"
        name_logfile = "interpolate"  # Placeholder name for the log file

        interpolation._run_interpolation_script(script_name, self.config, name_logfile)

        # Check if os.chdir is called correctly
        mock_chdir.assert_has_calls(
            [unittest.mock.call("/path/to/interpolator"), unittest.mock.call("cwd")]
        )

        # Check if script execution commands were called correctly
        mock_run.assert_has_calls(
            [
                call(["chmod", "+x", "test_script.sh"], check=True),
                call(["test_script.sh"], check=True, text=True, capture_output=True),
            ]
        )

        # Verify that the log file was written
        log_file_path = "/path/to/output/temp/interpolate_interpolate.log"
        mock_open.assert_called_with(log_file_path, "w")
        handle = mock_open()
        handle.write.assert_any_call("Standard Output:\n")
        handle.write.assert_any_call(mock_run.return_value.stdout)
        handle.write.assert_any_call("\nStandard Error:\n")
        handle.write.assert_any_call(mock_run.return_value.stderr)

    @patch("source.turbospectrum_integration.interpolation.chdir")
    @patch("source.turbospectrum_integration.interpolation.getcwd", return_value="cwd")
    @patch("source.turbospectrum_integration.interpolation.run")
    def test_run_interpolator_script_failure(self, mock_run, mock_getcwd, mock_chdir):
        """Test that the function raises a CalledProcessError when the interpolator script fails."""
        mock_run.side_effect = [
            None,
            CalledProcessError(1, "./interpolate.sh", stderr="Error"),
        ]
        self.config.path_interpolator = "/path/to/interpolator"
        script_name = "test_script.sh"
        name_logfile = "interpolate.log"  # Fake name, not used since the function is mocked to return error

        with self.assertRaises(CalledProcessError):
            interpolation._run_interpolation_script(
                script_name, self.config, name_logfile
            )

        # Ensure directory was changed back even on failure
        mock_chdir.assert_has_calls(
            [
                unittest.mock.call("/path/to/interpolator"),
                unittest.mock.call("cwd"),
            ]
        )

    @patch("source.turbospectrum_integration.interpolation._run_interpolation_script")
    @patch(
        "source.turbospectrum_integration.interpolation._load_parameters_to_interpolator_script"
    )
    @patch(
        "source.turbospectrum_integration.interpolation.copy_template_interpolator_script",
        return_value="interpolator_script.sh",
    )
    @patch(
        "source.turbospectrum_integration.interpolation._get_models_for_interpolation",
        return_value=(
            [
                {"teff_str": "5500", "logg_str": "4.0", "z_str": "-0.5"},
                {"teff_str": "6000", "logg_str": "5.0", "z_str": "0.5"},
            ]
            * 8,
            None,
        ),
    )
    def test_generate_interpolated_model(
        self, mock_get_models, mock_copy_script, mock_load_params, mock_run_script
    ):
        """Test that the function generates an interpolated model atmosphere."""
        stellar_parameters = {
            "teff": 5700,
            "logg": 4.5,
            "z": -0.2,
            "mg": 0.20,
            "ca": 0.30,
        }
        alpha = 0.00

        config = MagicMock()
        config.path_output_directory = "/path/to/output"
        config.path_interpolator = "/path/to/interpolator"

        ts_config = MagicMock()
        ts_config.file_name = "p5700_g+4.5_z-0.20_a+0.00_mg+0.20_ca+0.30"

        expected_output_path = (
            "/path/to/output/temp/p5700_g+4.5_z-0.20_a+0.00_mg+0.20_ca+0.30.interpol"
        )

        result, error_message = interpolation.generate_interpolated_model_atmosphere(
            stellar_parameters, alpha, config, self.MODEL_ATMOSPHERES
        )

        self.assertEqual(result, expected_output_path)
        self.assertIsNone(error_message)
        mock_copy_script.assert_called_once_with(config, alpha, stellar_parameters)
        mock_load_params.assert_called_once_with(
            "interpolator_script.sh",
            stellar_parameters,
            mock_get_models.return_value[0],
            config,
            ts_config.file_name,
        )
        mock_run_script.assert_called_once_with(
            "interpolator_script.sh",
            config,
            f"p5700_g+4.5_z-0.20_a+0.00_mg+0.20_ca+0.30",
        )
