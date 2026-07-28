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