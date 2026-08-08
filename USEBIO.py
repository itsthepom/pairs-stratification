###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Class that reads and writes USEBIO files.
# It can read v1.2 and v1.3 files. It always writes v1.3 files.
###############################################################################
from __future__ import annotations
from lxml import etree
import xml.etree.ElementTree as ET
from xml.dom import minidom
import baseclasses
import os
from datetime import datetime
from stratify import UIMPLevels, MPCode

class USEBIO(baseclasses.resultsReader):
    """ Reads/writes USEBIO files

        Args:
            tournamentData(tournament): tournamentData instance holding the event data.
            optionsInstance(options): Options instance holding the current options.
    """
    def __init__(self, tournamentData, optionsInstance):
       self.tournamentData = tournamentData
       self.options = optionsInstance
       pass
   
    def read(self, USEBIOFilename: str):
        """ Reads a USEBIO file. Can handle v1.2 and v1.3 files.

            Args:
                USEBIOFilename(str): Full pathname of USEBIO file to read
        """
        self.fullUSEBIOFilename = USEBIOFilename
        self.USEBIOFilename = os.path.splitext(os.path.basename(USEBIOFilename))[0]

        # Load and parse the XML file
        tree = etree.parse(USEBIOFilename)
        root = tree.getroot()

        # Locate the club tag, then the club name
        club = root.find('.//CLUB')
        clubName = club.find('.//CLUB_NAME').text           # Mandatory element
        clubID = club.find('./CLUB_ID_NUMBER').text         # Mandatory element

        # Locate the event tag
        event = root.find('.//EVENT')                       # Mandatory element
        if event.attrib['EVENT_TYPE'] != 'MP_PAIRS' and event.attrib['EVENT_TYPE'] != 'PAIRS':
            raise Exception("Not an MP Pairs event")
        numWinners = 1
        numWinnersTag = event.find('.//WINNER_TYPE')        # Optional element
        if numWinnersTag != None:
            numWinners = int(numWinnersTag.text)

        date = event.find('.//DATE').text                   # Mandatory element
        try:                                                # Convert to non-ISO format, if needed
            datetime.fromisoformat(date)
            dt = datetime.fromisoformat(date)
            date = dt.strftime("%d/%m/%Y")
        except:
            pass

        description = ''
        descriptionTag = event.find('.//EVENT_DESCRIPTION') # Optional element
        if descriptionTag != None:
            description = descriptionTag.text

        eventID = ''
        eventIDTag = event.find('.//EVENT_ID')              # v1.3 Optional element
        if eventIDTag == None:
            eventIDTag = event.find('.//EVENT_IDENTIFIER')  # v1.2 Optional element
        if eventIDTag != None:
            eventID = eventIDTag.text

        numEWPairs = 0
        ewPairsTag = event.find('.//EW_PAIRS')              # Optional element
        if ewPairsTag != None:
            numEWPairs = int(ewPairsTag.text)
        
        mpsAwarded = 'N'
        eventRating = ''
        mpsAwardedTag = event.find('.//MPS_AWARDED_FLAG')   # Optional element
        if mpsAwardedTag != None:
            mpsAwarded = mpsAwardedTag.text
        if mpsAwarded != 'N':
            eventRatingTag = event.find('.//EVENT_RATING')   # v1.3 Mandatory element if MPs awarded
            if eventRatingTag == None:
                eventRatingTag = event.find('.//MASTER_POINT_SCALE')   # v1.2 Mandatory element if MPs awarded
            if eventRatingTag != None:
                eventRating = eventRatingTag.text

        # Locate any stratification tag
        stratumLabels = [ None, None ]
        stratTag = event.find('.//STRATIFICATION')         # Optional element
        if stratTag != None:
            # Stratified event. Extract the strata
            stratsTag = stratTag.find('.//STRATS')         # Optional element
            if stratsTag != None:
                # Fetch the collection of strat
                try:
                    strats = stratsTag.findall('.//STRAT')
                    for strat in strats:
                        stratNumber = int(strat.find('.//STRAT_NUMBER').text)
                        if stratNumber > 1:
                            upperLimit = int(strat.find('.//UPPER_LIMIT').text)
                            stratumLabels[stratNumber - 2] = UIMPLevels[MPCode.index(upperLimit)]
                except:
                    pass

        # Locate the participants tag
        participants = event.find('.//PARTICIPANTS')

        # Fetch the collections of pairs and boards
        pairs = participants.findall('.//PAIR')             # Mandatory element
        boards = event.findall('.//BOARD')                  # Mandatory element
 
        numPairs = len(pairs)
        numBoards = len(boards)

        self.tournamentData.reset(clubName, clubID, eventID, description, date, eventRating, numPairs, numEWPairs, numBoards, numWinners, stratumLabels[0], stratumLabels[1])

        # Iterate over the pairs
        for pair in pairs:
            self.tournamentData.addResult(pair)

        # Iterate over the travellers
        for board in boards:
            self.tournamentData.addTraveller(board)

        self.tournamentData.processResults()

    def write(self, filename: str=None, outputdir: str=None, usebiov13: bool=False):
        """ Writes a USEBIO file in v1.2 or 1.3 format (https://usebio.org/documentation/usebio-1.3.pdf)

            Args:
                filename(str): Output filename, in interactive mode
                outputdir(str): In batch mode, the directory to output the file to
                usebiov13(bool): Whether to write in v1.3 format
        """
        def remove_whitespace_nodes(node):
            for child in list(node.childNodes):
                if child.nodeType == minidom.Node.TEXT_NODE and not child.data.strip():
                    node.removeChild(child)
                elif child.hasChildNodes():
                    remove_whitespace_nodes(child)

        def createNode(outerNode, tag, value=None):
            innerNode = ET.Element(tag)
            if value is not None:
                innerNode.text = str(value)
            outerNode.append(innerNode)
            return innerNode

        # Create a new XML file
        if usebiov13:
            root = ET.Element('USEBIO', {'Version': '1.3'})
        else:
            root = ET.Element('USEBIO', {'Version': '1.2'})

        # Add the club data
        club = createNode(root, 'CLUB')
        createNode(club, 'CLUB_NAME', self.tournamentData.clubName)
        createNode(club, 'CLUB_ID_NUMBER', self.tournamentData.clubID)

        # Add the event data - note MP_PAIRS is deprecated
        event = ET.SubElement(root, 'EVENT', {'EVENT_TYPE': 'PAIRS'})
        createNode(event, 'PROGRAM_NAME', baseclasses.AppName)
        createNode(event, 'PROGRAM_VERSION', baseclasses.AppVersion)
        if usebiov13:
            createNode(event, 'EVENT_ID', self.tournamentData.eventID)
        else:
            createNode(event, 'EVENT_IDENTIFIER', self.tournamentData.eventID)
        createNode(event, 'EVENT_DESCRIPTION', self.tournamentData.tournamentName)
        if usebiov13:
            createNode(event, 'DATE', datetime.strptime(self.tournamentData.tournamentDate, "%d/%m/%Y").date().isoformat())
        else:
            createNode(event, 'DATE', self.tournamentData.tournamentDate)
        createNode(event, 'BOARDS_PLAYED', self.tournamentData.numBoards)
        createNode(event, 'WINNER_TYPE', self.tournamentData.numWinners)
        createNode(event, 'PAIRS', self.tournamentData.numPairs)
        createNode(event, 'EW_PAIRS', self.tournamentData.numEWPairs)
        if len(self.tournamentData.eventRating) > 0:
            createNode(event, 'MPS_AWARDED_FLAG', 'Y')
            if usebiov13:
                createNode(event, 'EVENT_RATING', self.tournamentData.eventRating)
            else:
                createNode(event, 'MASTER_POINT_SCALE', self.tournamentData.eventRating)
        
        # If the tournament is stratified, add the appropriate XML elements
        if len(self.tournamentData.resultSet.overallRankings[1][0]) > 0:
            stratification = createNode(event, 'STRATIFICATION')
            createNode(stratification, 'STRATIFICATION_TYPE', 'HIGHEST')
            stratsNode = createNode(stratification, 'STRATS')

            # The top stratum is simply the overall results minus the pairs in subordinate strata
            stratNode = createNode(stratsNode, 'STRAT')
            createNode(stratNode, 'STRAT_NUMBER', 1)
            createNode(stratNode, 'STRAT_LABEL', 'A')
            createNode(stratNode, 'UPPER_LIMIT', MPCode[len(MPCode) - 1])
            numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[0][0]))
            if len(self.tournamentData.resultSet.overallRankings[0][1]) > 0:
                numPairsNode.set("DIRECTION", "NS")
                numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[0][1]))
                numPairsNode.set("DIRECTION", "EW")

            # First stratum
            stratNode = createNode(stratsNode, 'STRAT', None)
            createNode(stratNode, 'STRAT_NUMBER', 2)
            createNode(stratNode, 'STRAT_LABEL', 'B')
            createNode(stratNode, 'UPPER_LIMIT', MPCode[UIMPLevels.index(self.tournamentData.resultSet.stratumLabels[0])])
            numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[1][0]))
            if len(self.tournamentData.resultSet.overallRankings[1][1]) > 0:
                numPairsNode.set("DIRECTION", "NS")
                numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[1][1]))
                numPairsNode.set("DIRECTION", "EW")

            # Second stratum
            if len(self.tournamentData.resultSet.overallRankings[2][0]) > 0:
                stratNode = createNode(stratsNode, 'STRAT', None)
                createNode(stratNode, 'STRAT_NUMBER', 3)
                createNode(stratNode, 'STRAT_LABEL', 'C')
                createNode(stratNode, 'UPPER_LIMIT', MPCode[UIMPLevels.index(self.tournamentData.resultSet.stratumLabels[1])])
                numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[2][0]))
                if len(self.tournamentData.resultSet.overallRankings[2][1]) > 0:
                    numPairsNode.set("DIRECTION", "NS")
                    numPairsNode = createNode(stratNode, 'NUMBER_OF_PAIRS', len(self.tournamentData.resultSet.overallRankings[2][1]))
                    numPairsNode.set("DIRECTION", "EW")

        # Add the participants data
        participants = createNode(event, 'PARTICIPANTS')

        # Iterate through the results, creating a new pair tag for each
        for direction in self.tournamentData.resultSet.overallRankings[0]:
            for pairResult in direction:
                pair = createNode(participants, 'PAIR')
                createNode(pair, 'PAIR_NUMBER', pairResult.pairNumber)
                if self.tournamentData.numWinners == 2:
                    if pairResult.orientation == 'NS':
                        directionText = 'NS'
                    else:
                        directionText = 'EW'
                    createNode(pair, 'DIRECTION', directionText)

                createNode(pair, 'PLACE', pairResult.position)

                if self.tournamentData.resultSet.pairData[pairResult.pairNumber].masterpoints > 0:
                    masterPointsOuter = createNode(pair, 'MASTER_POINTS')
                    createNode(masterPointsOuter, 'MASTER_POINTS_AWARDED', self.tournamentData.resultSet.pairData[pairResult.pairNumber].masterpoints)
                    createNode(masterPointsOuter, 'MASTER_POINT_TYPE', 'black')
                createNode(pair, 'STRAT_PLACE', str(self.tournamentData.resultSet.pairData[pairResult.pairNumber].stratPosition))
                createNode(pair, 'STRAT_NUMBER', str(self.tournamentData.resultSet.pairData[pairResult.pairNumber].strat + 1))
            
                createNode(pair, 'PERCENTAGE', "{:.2f}".format(pairResult.percentscore))

                playerOuter = createNode(pair, 'PLAYER')
                createNode(playerOuter, 'PLAYER_NAME', pairResult.player1Name)
                createNode(playerOuter, 'NATIONAL_ID_NUMBER', pairResult.player1SBUNum)

                playerOuter = createNode(pair, 'PLAYER')
                createNode(playerOuter, 'PLAYER_NAME', pairResult.player2Name)
                createNode(playerOuter, 'NATIONAL_ID_NUMBER', pairResult.player2SBUNum)

        # Output the board results
        for currentBoard in self.tournamentData.resultSet.travellerSet.travellers:
            boardTag = createNode(event, 'BOARD')
            createNode(boardTag, 'BOARD_NUMBER', currentBoard.boardNum)
            for traveller in currentBoard.travellerLines:
                travellerLine = createNode(boardTag, 'TRAVELLER_LINE')
                createNode(travellerLine, 'NS_PAIR_NUMBER', traveller.NSPair)
                createNode(travellerLine, 'EW_PAIR_NUMBER', traveller.EWPair)
                createNode(travellerLine, 'CONTRACT', traveller.contract)
                createNode(travellerLine, 'PLAYED_BY', traveller.by)
                createNode(travellerLine, 'LEAD', traveller.lead)
                createNode(travellerLine, 'TRICKS', traveller.tricks)
                createNode(travellerLine, 'SCORE', traveller.score)
                createNode(travellerLine, 'NS_MATCH_POINTS', traveller.NSMPs)
                createNode(travellerLine, 'EW_MATCH_POINTS', traveller.EWMPs)

       
        # Tidy up the XML, removing excess whitespace
        if usebiov13:
            xml_str = b'<!DOCTYPE USEBIO SYSTEM "usebio_v1_3.dtd">\n' + ET.tostring(root, encoding='utf-8')
        else:
            xml_str = b'<!DOCTYPE USEBIO SYSTEM "usebio_v1_2.dtd">\n' + ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        remove_whitespace_nodes(parsed)

        # Pretty-print it and write to the output file. Note - do NOT indent - messes up some poorly written validators
        pretty_xml = parsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
        if filename != None:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
        else:
            with open(outputdir + '\\' + self.tournamentData.getOutputFilename() + '.xml', 'w', encoding='utf-8') as f:
                f.write(pretty_xml)

    class traveller(baseclasses.resultsReader.travellerBase):
        """ Container for classes to read pair results and traveller data from a USEBIO file
        """
        class travellerLine(baseclasses.resultsReader.travellerBase.travellerLineBase):
            """ Reads a traveller block from a USEBIO file

                Args:
                    board(ET.Element): XML element representing a board (BOARD tag).
                    pairData(dict): Dictionary of tournament.pairData
                    resultsMatrix(tournament.matrix): Matrix object populated by this code
            """
            def __init__(self, line, boardNum, pairData, resultsMatrix):
                self.NSPair = int(line.find('.//NS_PAIR_NUMBER').text)      # Mandatory element
                self.EWPair = int(line.find('.//EW_PAIR_NUMBER').text)      # Mandatory element
                self.contract = ''
                contractTag = line.find('.//CONTRACT')                      # Optional element
                if contractTag != None:
                    self.contract = contractTag.text
                playedByTag = line.find('.//PLAYED_BY')                     # Optional element
                self.by = ''
                if playedByTag != None:
                    self.by = playedByTag.text
                cardLed = line.find('.//LEAD')                              # Optional element
                self.lead = ''
                if cardLed != None:
                    self.lead = cardLed.text
                tricksTag = line.find('.//TRICKS')                          # Optional element
                self.tricks = ''
                if tricksTag != None and tricksTag.text != None:
                    self.tricks = int(tricksTag.text)
                self.score = line.find('.//SCORE').text                     # Mandatory element
                # score might be an average (e.g. A5050 or A6040). Deal with it
                if self.score[0] == 'A':
                    pass
                else:
                    self.score = int(self.score)
                self.NSMPs = float(line.find('.//NS_MATCH_POINTS').text)    # Mandatory element
                self.EWMPs = float(line.find('.//EW_MATCH_POINTS').text)    # Mandatory element
                resultsMatrix.addResult(self.NSPair, boardNum, self.NSMPs)
                resultsMatrix.addResult(self.EWPair, boardNum, self.EWMPs)
                # Use an exception catcher, since the first character of the contract might not be numeric
                try:
                    if int(self.contract[0]) >= 6:
                        # Slam contract
                        if self.by == 'S' or self.by == 'N':
                            if int(self.score) > 0:
                                if self.contract[0] == '6':
                                    pairData[self.NSPair].sslams = pairData[self.NSPair].sslams + 1
                                else:
                                    pairData[self.NSPair].gslams = pairData[self.NSPair].gslams + 1
                        else:
                            if int(self.score) < 0:
                                if self.contract[0] == '6':
                                    pairData[self.EWPair].sslams = pairData[self.EWPair].sslams + 1
                                else:
                                    pairData[self.EWPair].gslams = pairData[self.EWPair].gslams + 1
                except:
                    pass

        def __init__(self, board: ET.Element, pairData: dict, resultsMatrix):
            self.boardNum = int(board.find('.//BOARD_NUMBER').text)     # Mandatory element
            tLines = board.findall('.//TRAVELLER_LINE')                 # Mandatory element
            self.travellerLines = []
            for tLine in tLines:
                self.travellerLines.append(self.travellerLine(tLine, self.boardNum, pairData, resultsMatrix))
                playingPair = self.travellerLines[len(self.travellerLines) - 1].NSPair
                pairData[playingPair].boardsPlayed = pairData[playingPair].boardsPlayed + 1
                playingPair = self.travellerLines[len(self.travellerLines) - 1].EWPair
                pairData[playingPair].boardsPlayed = pairData[playingPair].boardsPlayed + 1


    class resultLine(baseclasses.resultsReader.resultLineBase):
        """ Reads a result block from a USEBIO file

            Args:
                pair(ET.Element): XML element representing a board (PAIR tag).
        """
        def __init__(self, pair: ET.Element):
            self.pairNumber = int(pair.find('.//PAIR_NUMBER').text)         # Mandatory element
            self.orientation = ''
            orientationTag = pair.find('.//DIRECTION')                      # Optional element
            if orientationTag != None:
                self.orientation = orientationTag.text
            players = pair.findall('.//PLAYER')                             # Mandatory element
            self.player1Name = players[0].find('.//PLAYER_NAME').text       # Mandatory element
            self.player2Name = players[1].find('.//PLAYER_NAME').text       # Mandatory element
            self.player1SBUNum = ''
            self.player2SBUNum = ''
            natIDTag = players[0].find('.//NATIONAL_ID_NUMBER')             # Optional element
            if natIDTag != None:
                self.player1SBUNum = natIDTag.text
            natIDTag = players[1].find('.//NATIONAL_ID_NUMBER')             # Optional element
            if natIDTag != None:
                self.player2SBUNum = natIDTag.text
            self.gslams = 0
            self.sslams = 0
            self.rawscore = 0
            self.maxscore = 0
            self.position = ''
        
        def setScore(self, total, maxMPs):
            self.rawscore = round(total, 1)
            self.maxscore = maxMPs
            self.percentscore = round(total * 100 / maxMPs, 2)

