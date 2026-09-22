# Configuring for Scorebridge

The default options of this program have been tailored for clubs using Scorebridge as their scoring program. If you use a different scoring program, you will need to configure the options appropriately.

As this program reads the XML results file (USEBIO format) produced by the scoring program, it is best to set the default input USEBIO results directory to the directory that the scoring program will write these files to. Remember - the output USEBIO file from your scoring program is the input to the Pairs Stratification program.

When using Scorebridge, if you tell Scorebridge to upload the file to MEMPAD as soon as it is created, the file is stored in the MasterPointsFiles directory under your club directory. Of course, if you are stratifying results, you would prefer to only upload the stratified USEBIO file.

If you tell Scorebridge to generate the file, but not upload it to MEMPAD, it (weirdly) writes the USEBIO files to a directory named "SBU MP Files". When Scorebridge uploads the file to MEMPAD, it moves the file to MasterPointFiles.

Therefore you want to configure the default input USEBIO results directory to be the "SBU MP Files" directory. By default (and even more weirdly), Scorebridge places the "SBU MP Files" directory on your desktop. You can change this in Scorebridge by selecting the Master Point Settings option from Scorebridge's Club Preferences menu and clicking on the underlined "P2P XML files saved to..." text. I would recommend you change this to be your club's MasterPointFiles directory.

In the Pairs Stratification program Options, set the input USEBIO files directory to be:

   "C:\\BridgeData\\{your club name}\\MasterPointFiles\\SBU MP Files"

so that the output USEBIO files from Scorebridge are the inputs to the scoring program. Then set the default output directory in the Pairs Stratification program options to be:

   "C:\\BridgeData\\{your club name}\\MasterPointFiles.

Doing this means that all files uploaded to MEMPAD are in the same directory, regardless of whether they are stratified or not, and files not uploaded to MEMPAD are in a separate directory underneath the MasterPointFiles directory.

The image in the [options](userif.md#options) configuration section of this help illustrates this for the "Phantom Bridge Club".

Finally Scorebridge has another quirk - when it writes a USEBIO file to SBU MP Files, it deletes every other file in that directory. If you run multiple events in one evening, you therefore need to generate the USEBIO file using Scorebridge and then run the Pairs Stratification program before generating the USEBIO file for another tournament.