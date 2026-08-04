# Batch Mode

"Batch mode" is really intended for testing, but you can use it to process a number of existing USEBIO files and generate strata so you can see
the effect of the stratification levels you've chosen over a set of past events.

Batch mode reads each file from an input directory, applies one or two stratification levels to the event and produces a stratified, output USEBIO
file and a PDF results page for each event.

The output USEBIO files and PDF results files are written to two new directories you specify.

To use this:

- Start a command prompt or PowerShell shell (WindowsKey+R) and type 'cmd' or 'powershell' (omit the quotes) and hit enter.
- Change directory to the program's installation folder (e.g. type 'cd C:\PairsStrat' - no quotes again).
- type '.\PairsStrat.exe' (no quotes) and you will get a useful reminder of the parameters to the command.

Each parameter is introduced by a double pair of dashes (e.g. - -dir), followed by a space and then the string for the parameter.
Note that it is wise to enclose the parameter in double quotes, so that spaces in the parameter don't confuse the program.

| Parameter | Description |
|-|-|
| - -help | Displays a useful reminder of the parameters |
| - -dir | Directory containing input USEBIO files for batch processing. Mandatory. |
| - -out | Directory to write output USEBIO files to when batch processing. Optional. No USEBIO files will be written without this parameter being present. The directory will be created if necessary. |
| - -pdf | Directory to write PDF print file to when batch processing. Optional. No PDF files will be written without this parameter being present. The directory will be created if necessary. |
| - -strat1 | Masterpoints rank name for stratum 1. Refer to the table below for a list of these names. |
| - -strat2 | Masterpoints rank name for stratum 2. Refer to the table below for a list of these names. |

Example:

C:\PairsUtility> **.\PairsStrat.exe --dir "C:\BridgeData\MyClub\MasterpointFiles" --out "C:\temp\MPFiles" --pdf "C:\temp\PDFOut" --strat1 "Regional Master" --strat2 "None"**

The names of the masterpoint levels that can be used for stratification are listed in the [Stratification](stratification.md#ranking-reference) section (remember to add quotes around names with a space).
