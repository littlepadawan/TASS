from configparser import ConfigParser
import os

class Configuration:
    def __init__(self, config_path = 'input/configuration.cfg'):
        self.config_file = os.path.abspath(config_path)
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"The config file {self.config_file} does not exist.")
       
        self.config_parser = ConfigParser()
        # TODO: Better to initiate to None or to default values?
        self.compiler = None
        self.path_turbospectrum = None
        self.path_turbospectrum_compiled = None
        self.path_linelists = None
        self.path_model_atmospheres = None
        self.path_input_parameters = None
        self.path_output_directory = None
        
        self.wavelength_min = 0
        self.wavelength_max = 0
        self.wavelength_step = 0
        
        
        self._load_configuration_file()
        self._validate_configuration()

    def _load_configuration_file(self):
        # Read configuration file
        self.config_parser.read(self.config_file)
        
        # Set configuration parameters found in the configuration file
        # Parameters in the configuration file must be explicity set here, 
        # so if you add something to the configuration file, you must also add it here
        self.compiler = self.config_parser.get('Turbospectrum_compiler', 'compiler').lower()
        
        self.path_turbospectrum = os.path.abspath(self.config_parser.get('Paths', 'turbospectrum'))
        self.path_linelists = os.path.abspath(self.config_parser.get('Paths', 'linelists'))
        self.path_model_atmospheres = os.path.abspath(self.config_parser.get('Paths', 'model_atmospheres'))
        self.path_input_parameters = os.path.abspath(self.config_parser.get('Paths', 'input_parameters'))
        self.path_output_directory = os.path.abspath(self.config_parser.get('Paths', 'output_directory'))
        
        self.wavelength_min = self.config_parser.getfloat('Atmosphere_parameters', 'wavelength_min')
        self.wavelength_max = self.config_parser.getfloat('Atmosphere_parameters', 'wavelength_max')
        self.wavelength_step = self.config_parser.getfloat('Atmosphere_parameters', 'wavelength_step')

    def _validate_configuration(self):
        # TODO: Improve error messages so user knows how to fix them
        '''
        Check that all required parameters are set and within range
        '''
        # Turbospectrum path
        if not os.path.exists(self.path_turbospectrum):
            raise FileNotFoundError(f"The specified directory containing Turbospectrum {self.config_file} does not exist.")
        
        # Compiler
        if self.compiler == 'intel':
            self.path_turbospectrum_compiled = os.path.join(self.path_turbospectrum, 'exec')
        elif self.compiler == 'gfortran':
            self.path_turbospectrum_compiled = os.path.join(self.path_turbospectrum, 'exec-gf')
        else:
            raise ValueError(f"Compiler {self.compiler} is not supported.")
        
        # Paths - directories
        paths_dir = [self.path_linelists, self.path_model_atmospheres, self.path_output_directory]
        for path in paths_dir:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The specified directory {path} does not exist.")
        
        # Paths - files
        paths_files = [self.path_input_parameters]
        for path in paths_files:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"The specified file {path} does not exist.")
        
        # Wavelength range
        if self.wavelength_min >= self.wavelength_max:
            raise ValueError(f"The minimum wavelength {self.wavelength_min} must be smaller than the maximum wavelength {self.wavelength_max}.")
        
        if self.wavelength_min < 0 or self.wavelength_max < 0 or self.wavelength_step <= 0:
            raise ValueError(f"The wavelength parameters must be positive.")
        
        
    def get(self, key):
        return self.configuration.get(key, None)
