# File Structure
This file contains an overview of the file structure, and as short comment about what each file contains.
.
├── docs                            # Contains documentation about the program
│   ├── configuration_setup.html    # API documentation generated using pdocs
│   ├── file_structure.md           # This file, an overview of the file structure
│   ├── index.html                  # API documentation generated using pdocs
│   ├── instructions.txt            # -"-
│   ├── main.html                   # -"-
│   ├── output_management.html      # -"-
│   ├── parameter_generation.html   # -"-
│   └── turbospectrum_integration   # -"-
│       ├── compilation.html        # -"-
│       ├── configuration.html      # -"-
│       ├── index.html              # -"-
│       ├── interpolation.html      # -"-
│       ├── run_turbospectrum.html  # -"-
│       └── utils.html              # -"-
├── input
│   ├── configuration.cfg           # The configuration file
│   ├── input_parameters.txt        # An example of how a file containing stellar parameters to be read can look
│   ├── linelists                   # The linelists must be placed here if not otherwise specified in the config file
│   └── model_atmospheres           # The model atmospheres must be placed here if not otherwise specified in the config file
├── output                          # The output will end up here if not otherwise specified in the config file
├── requirements.txt                # A list of required libraries, generated with pipreqs
├── source                          # Contains all the sourcecode for the project
│   ├── configuration_setup.py          # Reads and validates information in config file
│   ├── main.py                         # The program runs from here, contains overall program logic
│   ├── output_management.py            # Creates output directory and file for generated stellar parameters
│   ├── parameter_generation.py         # Generates stellar parameters dynamically or reads them from a file
│   └── turbospectrum_integration   # Contains functionality for setting up and running Turbospectrum
│       ├── compilation.py              # Compile Turbospectrum and interpolator
│       ├── configuration.py            # Make all preparations to run Turbospectrum (e.g. create babsma and bsyn scripts)
│       ├── interpolation.py            # Handle interpolation 
│       ├── run_turbospectrum.py        # Run Turbospectrum executables
│       └── utils.py                    # Helper functions, e.g. loading files containing model atmospheres
├── tests                           # Contains test for each module
└── turbospectrum                   # Where Turbospectrum should be placed, if not otherwise specified in the config file