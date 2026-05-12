# Automation Concentration Analysis
This script will automatically do a concentration analysis on the Ensight computer. It was created to simplify the analysis and estimation of concentration in an experiment. It takes raw absorbance data from an Ensight machine in `CSV` format and determines the concentration function using three variables defined at the beginning of the code.

## Requirement
For this code to work, is required:
- An output file from the Ensight plate analysis in `.csv` format. 
- Libraries : pandas, matplotlib, string, os and argparse

## Feature
- Reads and automatically detects the plate size (6, 12, 24, 96, 384-well plates)
- Generates a data frame with only relevant data from the file
- Calculates the slope and y-intercept to build a function (y-axis: absorbance, x-axis: concentration)
- Applies the calculation to all cells in the data frame (concentration table)
- Removes all unusable data and generates a plot of the function using two points
- Outputs: an Excel file with the cleaned data and a CSV list of all well positions with their corresponding concentrations

## Usage
On terminal run the tool

```
concentration_analysis.exe /path/to/file
```

The tools will request three variables:

`blank_well` : the concentration of that well is always 0

`sample_well` : a well that will have a precalculated concentration

`sample_concentration` : concentration of that sample

This script requires the input of the three wells defined earlier, as well as the path of the file being analysed. Once all information is entered, running the process will output a calibration curve and generate a `results` folder containing a data table of the calculated concentrations in `.xlsx` and a `.csv` list of all the wells with their individual concentrations.

## Automation on Momentum

When setting up a protocol on Momentum, add the `.exe` file to the computer and ensure it is named with the correct version for easy identification. As you run the protocol, the code will ask you to input the `blank_well`, the `sample_well`, and the `sample_concentration`. Then on momentum, add the argument of the file path of the file being analysed, but only once, as the script is designed to automatically find the path of the other files on its own. Once this information is entered, the code will run the analysis and display a calibration curve image, which will not be saved. It will also generate a `results` folder containing a `.csv` list of all the wells and their calculated concentrations, as well as an `.xlsx` data table of the original data provided by Ensight, with concentrations replacing the raw fluorescence values. 
