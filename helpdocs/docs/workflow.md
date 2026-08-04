# Workflow
The following diagram may help you to understand how the Pairs Stratification program works.

![Workflow Diagram](.\Workflow.png)

Bridgemates provide per-board scores to your scoring program. Once the tournament is finished, your scoring program produces the USEBIO results file. It may well produce other outputs, but the USEBIO file is the only one we're interested in. This is the file that you currently upload to MEMPAD and other sites.

The Pairs Stratification Program can then be run. This reads the USEBIO results file. You can then select the stratification level(s) to be applied and produce a new USEBIO file, printed output and optional webpage based on the stratification. The new USEBIO file is suitable for uploading.

Note that you don't have to stratify the tournament to produce printed output or the webpage. You can choose to just use the program to produce these if their format suits your needs.

However, to produce a new USEBIO file from the program the tournament must first be stratified (otherwise, just use the USEBIO file from your scoring program),

## Options
I strongly recommend you set up the options first (see [User Interface Options](.\userif.md#options)). This will save you time.

The program will then default to the correct directory for your USEBIO and Hand Record files (in blue, above), saving you from browsing for files and reducing the chance of errors.

The output files (in green, above) are written to sub-directories of an "Outputs" directory - setting the location of that directory (in Options) allows you to easily find the output files.

## Player's Database

Clearly, for the program to be able to stratify the tournament, it needs to know the rank of the players. The program reaches out to MEMPAD for these when it starts, therefore **your computer system must be able to access the Internet**.

Once the program has read the players database, it keeps a local "cache" of the information. This allows the program to work using the last read player's database should the Internet become unavailable.