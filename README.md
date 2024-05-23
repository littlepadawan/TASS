This program serves as a wrapper for Turbospectrum, providing an interface that simplifies its use. It automated the invocation of Turbospectrum, enabling users to generate large volumes of stellar spectra without the need for manual intervention. Additionally, it includes functionality for generating stellar spectra within parameter ranges specified by the user. 

## Prerequisites
- **Turbospectrum**. Ensure Turbospectrum is installed. The program was developed for version Turbospectrum 20.0. It has not been tested on older versions, and compatability with later versions is not guaranteed. Turbospectrum can be downloaded here: [https://github.com/bertrandplez/Turbospectrum_NLTE](https://github.com/bertrandplez/Turbospectrum_NLTE)
- **Python**. The program is developed using Python 3.10
- **Fortran compiler**. To run Turbospectrum, either GFortran or Intel Fortran Compiler is required.
- **Python packages**. Ensure the packages listed in `requirements.txt` are installed (TBI).

The program is developed for Unix systems and has not been tested on Windows systems. 

## Supported Features
Turbospectrum accepts a wide range of parameters. This program, however, specifically supports the following 5 parameters:
- Effective temperature *T<sub>eff</sub>*
- Surface gravity *log g*
- Metallicity *z* (sometimes also referred to as \[Fe/H])
- Abundance of magnesium *mg*
- Abundance of calcium *ca*

Additionally:
- The program is designed to work with 1D model atmospheres (MARCS). It does not support 3D models.
- For interpolation, the program uses the interpolator provided by Turbospectrum.
- Note that this program only supports LTE.

## Installation and Setup
1. Clone this repository <br>
`git clone https://github.com/littlepadawan/turbospectrum-wrapper.git`
2. Clone Turbospectrum into the `turbospectrum` directory of this project <br>
`git clone https://github.com/bertrandplez/Turbospectrum_NLTE turbospectrum`
3. Place the MARCS model atmospheres you want to use in the `input/model_atmospheres` directory.
4. Place the linelists you want to use in the `input/linelists`directory.
5. Navigate to the root of the project
6. Install Python dependencies <br>
`pip install -r requirements.txt`

*You can modify the file paths for Turbospectrum, model atmospheres, and linelists in the `configuration.cfg` file if you prefer not to place them in the default directories*

## Running the Program
To run the program using the default settings in the provided configuration file, navigate to the rote of the project and execute the following command: <br>
`python3 source/main`

## Documentation
For details on how to modify the configuration or how the program works, refer to the `docs` directory (TBI).
