# Input

This file contains information about the required input to the program.

## Configuration File
The program is configured through the input/configuration.cfg file. This file follows the structure of a .ini file, meaning it contains sections and keywords. It is read using Python's ConfigParser.

Details for each keyword are provided in the configuration file. Ensure to provide valid file paths and verify that the expected content is present. The program includes checks to ensure minimum values are not greater than maximum values and that temperature values are not negative. However, it does not perform other bounds checking, so be sure to specify reasonable parameter values. Refer to the Turbospectrum documentation for information about its parameter ranges.

The configuration file contains relative file paths. If these causes problems, replace them with absolute paths specific to your machine.

## Model Atmospheres
Model atmospheres provide theoretical frameworks for the temperature, pressure, and chemical composition in a star's atmosphere.

- The program only supports MARCS model atmospheres in 1D.
- MARCS model atmospheres can be found here: [https://marcs.oreme.org/](https://marcs.oreme.org/)
- The program expects a large volume of model atmospheres to bensure suitable ones can be found for interpolation.
  
## Line Lists
Line lists are compilations of atomic and molecular transitions that can occur in stellar atmospheres, detailing the wavelengths at which light is absorbed or emitted.

- The program expects at least one line list to be provided.
- By default, the program expects the line lists to be placed in `input/linelists`. However, you can change this filepath in the configuration file if you prefer to store them somewhere else.
- The program currently loads all files present in the specified directory containing line lists. Therefore, it is advicable to have a separate directory exclusively for these files.
- Ensure that the wavelength parameters in the configuration cover the wavelength range of the line lists for the program to generate valid results.
  
## Stellar Parameters
You can choose to either let the program generate stellar parameters for you, or provide a list with already existing stellar parameters for the program to read. 

If you want the program to read a file with existing stellar parameters:
- Specify the file path in the configuration file
- The file must begin with a header line containing the parameter names. The expected parameter names are `teff`, `logg`, `z`, `mg`, and `ca`.
- After the header line, specify the parameter sets specified row-wise, with each parameter type separated by a space.

An example of how this file can look like is `input/input_parameters.txt`.
