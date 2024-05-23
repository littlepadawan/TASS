This program serves as a wrapper for Turbospectrum, providing an interface that simplifies its use. It automated the invocation of Turbospectrum, enabling users to generate large volumes of stellar spectra without the need for manual intervention. Additionally, it includes functionality for generating stellar spectra within parameter ranges specified by the user. 

## Prerequisites
- **Turbospectrum**. Ensure Turbospectrum is installed. The program was developed for version X.X. It has not been tested on older versions, and compatability with later versions is not guaranteed. Turbospectrum can be downloaded here: XXX
- **Python**. The program is developed using Python 3.XXX
- **Fortran compiler**. To run Turbospectrum, either gfortran or Intel Fortran is required.
- **Python packages**. Ensure the packages listen in XXX is installed.

The program is developed for Unix systems and has not been tested on Windows systems. 

## Supported Features
Turbospectrum accepts a wide range of parameters. This program, however, specifically supports the following 5 parameters:
- Effective temperature *T~eff~*
- Surface gravity *log g*
- Metallicity *z* (sometimes also referred to as \[Fe/H])
- Abundance of magnesium *mg*
- Abundance of calcium *ca*

The program only manages 1D model atmospheres (MARCS) in this format: XXX.
For interpolation, it uses the interpolator provided by Turbospectrum.
It only supports LTE, not NLTE.

## Installation and Setup
1. Clone this repository `git clone https://github.com/littlepadawan/turbospectrum-wrapper.git`
2. Clone Turbospectrum into the `turbospectrum` directory of this project
INSERT CLONE COMMAND
3. Place the MARCS model atmospheres you want to use in the `input/model_atmospheres` directory.
4. Place the linelists you want to use in the `input/linelists`directory.
5. Navigate to the root of the project
6. Install Python dependencies `pip install -r requirements.txt`

*It is possible to change file paths to Turbospectrum, model atmospheres, and linelists in `configuration.cfg` if you prefer to not place them in these directories*

## Running the Program
To run the program using the default settings in the provided configuration file, navigate to the rote of the project and execute the following command:
`python3 source/main`

## Documentation
For details on how to modify the configuration or how the program works, refer to the `docs` directory. (The docs directory is currently under implementation)