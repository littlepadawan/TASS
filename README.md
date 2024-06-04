# TASS - Turbospectrum Automated Synthetic Spectra

This program serves as a wrapper for Turbospectrum, providing an interface that simplifies its use. It automates the invocation of Turbospectrum, enabling users to generate large volumes of synthetic stellar spectra without the need for manual intervention. Additionally, it includes functionality for generating stellar parameter sets needed as input to Turbospectrum, within ranges specified by the user. 

## Prerequisites

- **Turbospectrum**. Ensure Turbospectrum is installed. The program was developed for version Turbospectrum 20.0. It has not been tested on older versions, and compatability with later versions is not guaranteed. Turbospectrum can be downloaded here: [https://github.com/bertrandplez/Turbospectrum_NLTE](https://github.com/bertrandplez/Turbospectrum_NLTE)
- **Python**. The program is developed using Python 3.10
- **Fortran compiler**. To run Turbospectrum, either GFortran or Intel Fortran Compiler is required.
- **Python packages**. Ensure the packages listed in `requirements.txt` are installed.

The program is developed for Unix systems and has not been tested on Windows systems. 

## Supported Features

Turbospectrum accepts many different types of parameters. This program, however, specifically supports inputting the following 5 parameters to Turbospectrum:
- Effective temperature *(T<sub>eff</sub>)*
- Surface gravity *(log g)*
- Metallicity *\[Fe/H], or Z*
- Abundance of magnesium *Mg*
- Abundance of calcium *Ca*

Additionally:
- The program is designed to work with 1D model atmospheres (MARCS). It does not support 3D models.
- For interpolation, the program uses the interpolator provided by Turbospectrum.
- Note that this program only supports LTE and plane parallel geometry.

## Installation and Setup

1. Clone this repository <br>
`git clone https://github.com/littlepadawan/turbospectrum-wrapper.git`
2. Navigate to the root of the project and clone Turbospectrum into the `turbospectrum` directory<br>
`git clone https://github.com/bertrandplez/Turbospectrum_NLTE turbospectrum`
*Skip this step if you already have Turbospectrum installed. You can then choose to either move Turbospectrum to the `turbospectrum`directory or change the file path in the `configuration.cfg` file*
3. Place the MARCS model atmospheres you want to use in the `input/model_atmospheres` directory.
4. Place the linelists you want to use in the `input/linelists` directory.
5. Specify the Fortran compiler in `configuration.cfg` file, `gfortran`is default.
6. Navigate to the root of the project
7. Make sure the Python dependencies are installed. You can either do this manually, or install them using the following command: <br>
`pip install -r requirements.txt`

*You can modify the file paths for Turbospectrum, model atmospheres, and linelists in the `configuration.cfg` file if you prefer not to place them in the default directories*

## Running the Program

To run the program using the default settings in the provided configuration file, navigate to the rote of the project and execute the following command: <br>
`python3 -m source.main`

If no changes are made to the `configuration.cfg` file, the program will generate 10 randomly spaced parameter sets and invoke Turbospectrum once per parameter set.

## Documentation

For details on how to modify the configuration or how the program works, refer to the `docs` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/littlepadawan/TASS/blob/main/docs/LICENSE) file for details.

## Acknowledgments

If you use this software in a publication or presentation, please acknowledge the original author by citing the project.
