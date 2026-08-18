1.7 Release Notes
=================

Major changes:
- Added logging to a file to help diagnose issues
- Added an About box to provide a link for error reporting
- Added retries of member data fetch from the Internet to avoid transient issues

Minor changes:
- Forced default response charset to UTF-8

1.6 Release Notes
=================

Major changes:
- Fixed issue where XML output not being generated for X-IMPs and Aggregate events.
- Fixed issue where masterpoints for Area events could be fractional
- Fixed issue where X-IMPs and Aggregate scores were output from internally generated sums, rather than the input file values.

Minor changes:
- Fixed lack of error if the PDF print file was not writable.

1.5 Release Notes
=================

Major changes:
- A new page has been added to allow changing the stratification rank of each pair.
- The program now supports scoring by matchpoints, cross-IMPs (new) and aggregate (new).
- The stratification page rank colouring has changed to match that of BridgeWebs.
- Support has been added to increase the masterpoints scales for National, District and Area events (previously just Club)
- The output of the utility is primarily USEBIO 1.2. However, the stratification XML elements are
  part of the 1.3 standard and not 1.2. So, technically, the output is not 1.2-compliant, but a hybrid.
- Help file updates

Minor changes:
- Icons have been made prettier.
- Spacing of controls on the screen are more uniform.
- An error dialog has been created for a non-existant web template.

1.4 Release Notes
=================

Major changes:
- The Stratification screen has been rewritten to make its use more intuitive and display the effect of stratification
  interactively.
- Strata have been assigned labels (A, B and C), where A is the overall results stratum. B & C are subordinate strata.
- For 3-strata results, stratum B now has stratum C players included.
- The players DB is now read from MEMPAD at the start of the program and cached. So each run now has a fresh DB as
  opposed to every stratification attempt.
- Menu links that are not appropriate for the state the program is in are disabled.
- In a two winner event, when stratification is done, both directions are awarded stratified masterpoints even if
  all masterpoints for one direction are achieved in the overall results (previously stratified masterpoints could
  be awarded to one direction only).
- Printed PDF and webpage now show the stratum that a pair belongs to and the stratum that a pair's masterpoints were awarded in.
- The XML USEBIO output now contains the strata labels and strat position for all pairs.
- The user interface has been polished to give it a more modern feel.
- Added handling for high-DPI screens.

Minor changes:
- The program has been renamed from PairsUtility to PairsStrat and the default installation directory changed.
- Previous branding has been replaced.
- Improvements to the stand-alone web page.
- Improvements to the help docs.
- Avoided windows firewall issues with the help server.
- Various minor bug fixes.