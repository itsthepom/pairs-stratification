# Pairs Stratification Program
First things first - this program is not a scoring program.

It is used after you have scored a pairs tournament using whatever scoring program your club uses.

The results from your scoring program must be in a USEBIO format file. USEBIO stands for Universal Scoring Exchange for Bridge Information and Output. It is a standard XML file format developed and maintained by the English Bridge Union and is in widespread use by many bridge scoring systems. It is also the format of the file that is used to upload your club results to MEMPAD or BridgeWebs.

This program reads the USEBIO file produced by your scoring program and can perform the following functions:

* Allow you to stratify the pairs tournament. Stratification is explained later.
* Produce a Portable Document Format (PDF) file of the results that can be printed for display on your club notice board. This is also useful as an on-screen display of the results of stratification before uploading.
* Produce a new USEBIO file that contains stratified awards for upload to MEMPAD or other websites.
* Produce a stand-alone results webpage, intended for clubs that have their own website (as distinct from using a hosted system, like BridgeWebs).

## Before You Start
We recommend you read through this guide first to explain the operation of this program.

If you're one of those people that can't be bothered reading it all, please at least read the [Workflow](workflow.md) section and, **IMPORTANTLY, set up the [options](userif.md#options) for the program** to make life easier for yourself.

## Stratification Basics
Stratification is the process of splitting the overall tournament results into one or more sections (strata) that contain only those pairs that are below a certain masterpoints rank. You could think of it as playing the same boards on the same night in different, rank-restricted sections.

Many clubs play "open" tournaments, where there are no rank restrictions. You may have a number of, say, silver or gold pairs playing against bronze-level opponents. In such a field, you would expect the higher ranked pairs to regularly take most of the masterpoints. While it's good for aspiring players to compete against higher ranked players to gain experience and learn, rank promotion is hampered by their inability to accrue masterpoints in such a field. As a result, the lower-ranked pairs may become reluctant to play against higher-ranked players.

Clubs that have a sufficient membership will often offer rank-restricted tournaments. While this provides a better chance to gain masterpoints, the players lose the advantage of learning from more experienced players.

Stratification takes a non-rank restricted tournament and divides the overall results into "strata", where pairs below a certain rank are placed into a stratum that is then awarded masterpoints using the standard award scales (actually, they are slightly different - we'll explain that later).

Score and award wise, it's similar to playing the same boards in rank-restricted sections, but gives lower ranked pairs experience of playing against higher ranked pairs. It also allows the generation of results tables allowing the pairs in each stratum to see how well they have performed against their peers of a similar rank.
