# import subprocess
# import unittest
# from unittest.mock import MagicMock, patch

# import turbospectrum_integration.turbospectrum_integration as turbospectrum_integration
# from configuration_setup import Configuration
# from model_atmospheres_data_for_testing import FILENAMES


# class TestTurbospectrumIntegration(unittest.TestCase):


#     def setUp(self):
#         # Set up a Configuration object
#         self.config = Configuration()

#     def test_parse_model_atmosphere_filename_match(self):
#         """
#         Test that the model atmosphere filename is parsed correctly and returns the expected parameters if the filename matches the pattern
#         """
#         filename = "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
#         expected_output = {
#             "teff": "6000",
#             "logg": "+4.0",
#             "feh": "-2.00",
#             "filename": "p6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod",
#         }

#         output = turbospectrum_integration._parse_model_atmosphere_filename(filename)
#         # print(output)
#         self.assertEqual(output, expected_output)

#     def test_parse_model_atmosphere_filename_no_match(self):
#         """
#         Test that the model atmosphere filename is parsed correctly and returns None if the filename does not match the pattern
#         """
#         filename = "s6000_g+4.0_m0.0_t02_st_z-2.00_a+0.40_c+0.00_n+0.00_o+0.40_r+0.00_s+0.00.mod"
#         expected_output = None

#         output = turbospectrum_integration._parse_model_atmosphere_filename(filename)
#         self.assertEqual(output, expected_output)

#     @patch("turbospectrum_integration.os.listdir")
#     @patch("turbospectrum_integration._parse_model_atmosphere_filename")
#     def test_extract_parameters_from_filenames(self, mock_parse, mock_listdir):
#         FILENAMES.append("random_file.doc")

#         # Mock the directory content
#         mock_listdir.return_value = FILENAMES

#         # Expected grid
#         expected_grid = self.PARSED_FILENAMES

#         # Set up the mock to return a different directory for each file
#         mock_parse.side_effect = lambda x: next(
#             (item for item in expected_grid if item["filename"] == x), None
#         )

#         result = turbospectrum_integration._extract_parameters_from_filenames(
#             "dummy_directory"
#         )

#         self.assertEqual(result, expected_grid)
#         FILENAMES.remove("random_file.doc")

#     def test_create_model_grid(self):
#         pass

#     def test_find_bracketing_models(self):
#         parameters = {"teff": 5210, "logg": 4.3, "feh": 0.05}
#         models = turbospectrum_integration._find_bracketing_models(
#             parameters, self.MODEL_GRID
#         )
#         # for model in models:
#         #     print(model)

#     def test_needs_interpolation(self):
#         pass

#     def test_create_template_interpolator_script(self):
#         parameters = {"teff": 5710, "logg": 4.6, "feh": 0.25}
#         turbospectrum_integration.compile_interpolator(self.config)
#         turbospectrum_integration.create_template_interpolator_script(self.config)
#         turbospectrum_integration.generate_interpolated_model_atmosphere(
#             self.config, parameters
#         )

#     def test_create_babsma(self):
#         parameters = {"teff": 5710, "logg": 4.6, "feh": 0.25}
#         turbospectrum_integration.compile_turbospectrum(self.config)
#         turbospectrum_integration.compile_interpolator(self.config)
#         all_models = turbospectrum_integration._extract_parameters_from_filenames(
#             self.config.path_model_atmospheres
#         )
#         model_grid = turbospectrum_integration._create_model_grid(all_models)
#         turbospectrum_integration.create_template_interpolator_script(self.config)
#         turbospectrum_integration.generate_one_spectrum(
#             self.config, parameters, model_grid
#         )
