###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Generates a stand-alone webpage from a template
###############################################################################
from bs4 import BeautifulSoup
from datetime import datetime
from baseclasses import baseUIClass
from uiparts import UIParts
import ttkbootstrap as tb
from tkinter import messagebox
import json
import os
from pathlib import Path
import pbnreader
import filehandling
from dateutil import parser

CompleteColor = "#44880C"

class webpage(baseUIClass):
    """ Runs a UI to allow th user to produce a standalone webpage file containing the event results.
        Uses an HTML template and populates a marked area with JSON that JavaScript in the
        page can read to display the results.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame: tb.Frame, tournamentData, uiparts: UIParts):
        self.frame = frame
        self.tournamentData = tournamentData
        self.uiparts = uiparts
        uiparts.webpageDisplay = self
        self.inputFile = None
        self.dealInfo = None
        self.numLoads = 0
        self.eventNameVar = tb.StringVar()
        self.inputFileVar = tb.StringVar()
        self.dateVar = tb.StringVar()
        self.outputFileVar = tb.StringVar()
        self.outputFileVar.trace_add("write", self.fileSelected)
        self.inputFileVar = tb.StringVar()
        self.inputFileVar.trace_add("write", self.inputFileSelected)

    def getName(self):
        return 'webpage'
    
    def construct(self, pagebgnd: str):
        self.pagebgnd = pagebgnd
        if self.numLoads != self.tournamentData.numLoads:
            self.numLoads = self.tournamentData.numLoads
            outputFilename = self.tournamentData.getOutputFilename()
            if len(outputFilename) > 0:
                self.outputFileVar.set(self.uiparts.options.getDirectory('outputsdir') + self.uiparts.options.getDirectory('webpagesdir') + self.tournamentData.getOutputFilename() + ".html")
            else:
                self.outputFileVar.set("")

        self.spacerLabel5 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel5.grid(row=0, column=0, columnspan=2, sticky="nw")

        self.outputFileLabel1 = tb.Label(self.frame, text="Select the new webpage file to be created.", font=("Arial", 10, "bold"), justify='left')
        self.outputFileLabel1.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.outputFileLabel2 = tb.Label(self.frame, text="This file can be uploaded to your website.", font=("Arial", 10), justify='left')
        self.outputFileLabel2.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton1 = tb.Button(self.frame, text="Browse", bootstyle="Primary", command=lambda: self.pickOutputFile())
        self.browseButton1.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.outputFileEntry = tb.Entry(self.frame, textvariable=self.outputFileVar, width=95, font=("Arial", 10))
        self.outputFileEntry.grid(row=3, column=0, sticky="w", padx=100)

        self.spacerLabel4 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel4.grid(row=4, column=0, columnspan=2, sticky="nw")

        self.inputFileLabel1 = tb.Label(self.frame, text="Select a hand record file to include in the webpage.", font=("Arial", 10, "bold"), justify='left')
        self.inputFileLabel1.grid(row=5, column=0, columnspan=2, sticky="w", padx=20)
        self.inputFileLabel2 = tb.Label(self.frame, text="This must be a PBN (Portable Bridge Notation) format file.", font=("Arial", 10), justify='left')
        self.inputFileLabel2.grid(row=62, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton2 = tb.Button(self.frame, text="Browse", bootstyle="Primary", command=lambda: self.pickInputFile())
        self.browseButton2.grid(row=7, column=0, pady=10, padx=20, sticky="w")
        self.inputFileEntry = tb.Entry(self.frame, textvariable=self.inputFileVar, width=95, font=("Arial", 10))
        self.inputFileEntry.grid(row=7, column=0, sticky="w", padx=100)

        self.spacerLabel3 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel3.grid(row=8, column=0, columnspan=2, sticky="nw")

        self.detailTitleLabel = tb.Label(self.frame, text="Hand Record Details:", font=("Arial", 10, "bold"), justify='left')
        self.detailTitleLabel.grid(row=9, column=0, columnspan=2, sticky="w", padx=20)
        self.eventNameLabel1 = tb.Label(self.frame, text='Event:', font=("Arial", 10), justify='left')
        self.eventNameLabel1.grid(row=10, column=0, sticky="w", padx=20)
        self.eventNameLabel2 = tb.Label(self.frame, textvariable=self.eventNameVar, font=("Arial", 10), justify='left')
        self.eventNameLabel2.grid(row=10, column=0, sticky="w", padx=100)
        self.dateLabel1 = tb.Label(self.frame, text='Date:', font=("Arial", 10), justify='left')
        self.dateLabel1.grid(row=11, column=0, sticky="w", padx=20)
        self.dateLabel2 = tb.Label(self.frame, textvariable=self.dateVar, font=("Arial", 10), justify='left')
        self.dateLabel2.grid(row=11, column=0, sticky="w", padx=100)

        self.spacerLabel2 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel2.grid(row=12, column=0, columnspan=2, sticky="nw")

        self.createButton = tb.Button(self.frame, text="Create", bootstyle="Primary", command=lambda: self.createWrapper())
        self.createButton.grid(row=13, column=0, sticky="w", padx=20, pady=10)

        self.spacerLabel1 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel1.grid(row=14, column=0, columnspan=2, sticky="nw")

        self.messageLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), justify='left', foreground=CompleteColor)
        self.messageLabel.grid(row=15, column=0, columnspan=2, sticky="w", padx=20)

        self.spacerLabel = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel.grid(row=16, column=0, columnspan=2, sticky="nw", padx=420, pady=250)
        self.showDetail()
        
    def clearContent(self):
        self.spacerLabel.destroy()
        self.messageLabel.destroy()
        self.spacerLabel1.destroy()
        self.createButton.destroy()
        self.spacerLabel2.destroy()
        self.dateLabel2.destroy()
        self.dateLabel1.destroy()
        self.eventNameLabel2.destroy()
        self.eventNameLabel1.destroy()
        self.detailTitleLabel.destroy()
        self.spacerLabel3.destroy()
        self.inputFileEntry.destroy()
        self.browseButton2.destroy()
        self.inputFileLabel2.destroy()
        self.inputFileLabel1.destroy()
        self.spacerLabel4.destroy()
        self.outputFileEntry.destroy()
        self.browseButton1.destroy()
        self.outputFileLabel2.destroy()
        self.outputFileLabel1.destroy()
        self.spacerLabel5.destroy()

    def setInputFile(self, filename):
        self.inputFile = filename
        self.showDetail()

    def pickInputFile(self):
        filename = filehandling.openHandRecordFile(self.uiparts.options.config["handrecordsdir"])
        self.inputFileVar.set(filename)
        self.setInputFile(filename)

    def inputFileSelected(self, name, index, mode):
        self.setInputFile(None)

    def pickOutputFile(self):
        filename = filehandling.openWebpageFile(self.uiparts.options.getDirectory("outputsdir") + self.uiparts.options.config["webpagesdir"])
        if len(filename) > 0:
            self.outputFileVar.set(filename)

    def fileSelected(self, name, index, mode):
        try:
            self.messageLabel.config(text='')
            if len(self.outputFileVar.get()) > 0:
                self.createButton.config(state="normal")
            else:
                self.createButton.config(state="disabled")
        except:
            pass
   
    def showDetail(self):
        self.messageLabel.config(text='')
        if self.inputFile != None and len(self.inputFile) > 0:
            self.dealInfo = pbnreader.PBNReader()
            self.dealInfo.read(self.inputFile)
            self.eventNameVar.set(self.dealInfo.event)
            self.dateVar.set(self.dealInfo.date)

        else:
            self.dealInfo = None
            self.eventNameVar.set('')
            self.dateVar.set('')

    def createWrapper(self):
        self.messageLabel.config(text='')
        OKToCreate = True
        if self.dealInfo == None:
            response = messagebox.askyesno(title="No hand record", message="No deal file selected.\nAre you sure you wish to create the webpage?")
            OKToCreate = response
        else:
            # Try and parse the date from the deal file
            try:
                dealDate = parser.parse(self.dealInfo.date).date()
                eventDate = parser.parse(self.tournamentData.tournamentDate).date()
                if dealDate != eventDate:
                    response = messagebox.askyesno(title="Deal date does not match", message="Different deal date selected.\nAre you sure you wish to create the webpage?")
                    OKToCreate = response
            except:
                OKToCreate = False
        if OKToCreate:
            self.create()
        
    def create(self):
        self.uiparts.options.getDirectory("outputsdir")
        def createRanking(results, stratumNumber):
            data = []
            for result in results:
                pairData = self.tournamentData.resultSet.pairData[result.pairNumber]
                masterpoints = str(pairData.masterpoints) if pairData.masterpoints != 0 else ""
                if len(masterpoints) > 0 and pairData.awardedStratum != None and pairData.awardedStratum != stratumNumber:
                    masterpoints = masterpoints + '(' + chr(ord('A') + pairData.awardedStratum - 1) + ')'
                ranking = {
                    "pos": result.position,
                    "pairnum": result.pairNumber,
                    "strat": "A" if pairData.strat == 0 else "B" if pairData.strat == 1 else "C",
                    "pair": result.player1Name + " & " + result.player2Name,
                    "score": "{:.1f}".format(result.rawscore),
                    "max": "{:.0f}".format(result.maxscore),
                    "percent": "{:.2f}".format(result.percentscore),
                    "mps": str(masterpoints),
                    "ss": pairData.sslams,
                    "gs": pairData.gslams
                }
                data.append(ranking)
            return data
        
        # Load HTML content
        webfilePath = Path(self.uiparts.options.config['webfiletemplate'])
        if webfilePath.is_file():
            with open(self.uiparts.options.config['webfiletemplate'], "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
        
            # Find the script tag where we store our data
            scriptTag = soup.find(id="resultdata")
            if not scriptTag is None:
                # Looks like a valid template file. Build the JSON to drop into the resultData script tag
                # Event data first
                dateObj = datetime.strptime(self.tournamentData.tournamentDate, "%d/%m/%Y")
                isTwoWinner = self.tournamentData.numWinners > 1
                data = {
                    "clubname": self.tournamentData.clubName,
                    "eventname": self.tournamentData.tournamentName + ' - ' + dateObj.strftime("%A") + ' ' + dateObj.strftime("%d") + ' ' + dateObj.strftime("%b") + ' ' + dateObj.strftime("%Y"),
                    "istwowinner": isTwoWinner,
                    "boardsperround": self.tournamentData.boardsPerRound,
                    "numboards": self.tournamentData.numBoards
                }
                JSONString = "\nlet eventInfo = " + json.dumps(data) + ";"

                # Then the results - single winner or N/S first, then E/W
                JSONString = JSONString + '\nlet rankings = {"heading": "Stratum A - Overall Rankings", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[0][0], 1)) + "};"
                if len(self.tournamentData.resultSet.overallRankings[0][1]) > 0:
                    JSONString = JSONString + '\nlet rankingsew = {"heading": "", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[0][1], 1)) + "};"
                # Stratum 1
                if len(self.tournamentData.resultSet.overallRankings[1][0]) > 0:
                    if len(self.tournamentData.resultSet.overallRankings[2][0]) > 0:
                        heading = "Stratum B - " + self.tournamentData.resultSet.stratumLabels[0] + " to above " + self.tournamentData.resultSet.stratumLabels[1]
                    else:
                        heading = "Stratum B - " + self.tournamentData.resultSet.stratumLabels[0] + " and lower"
                    JSONString = JSONString + '\nlet rankings1 = {"heading": "' + heading + '", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[1][0], 2)) + "};"
                    if len(self.tournamentData.resultSet.overallRankings[1][1]) > 0:
                        JSONString = JSONString + '\nlet rankingsew1 = {"heading": "", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[1][1], 2)) + "};"
                    if len(self.tournamentData.resultSet.overallRankings[2][0]) > 0:
                        heading = "Stratum C - " + self.tournamentData.resultSet.stratumLabels[1] + " and lower"
                        JSONString = JSONString + '\nlet rankings2 = {"heading": "' + heading + '", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[2][0], 3)) + "};"
                        if len(self.tournamentData.resultSet.overallRankings[2][1]) > 0:
                            JSONString = JSONString + '\nlet rankingsew2 = {"heading": "", "data": ' + json.dumps(createRanking(self.tournamentData.resultSet.overallRankings[2][1], 3)) + "};"

                # Now add the pair scorecards
                JSONString = JSONString + "\nlet scorecards = "
                scorecards = []
                for key, pair in self.tournamentData.resultSet.pairData.items():
                    data = {
                        "pairnum": key,
                        "pair": '',
                        "board": []
                    }
                    for key, board in pair.scorecard.items():
                        boardData = {
                            "boardNum": key,
                            "isNS": board.isNS,
                            "versus": board.versus,
                            "contract": board.contract,
                            "by": board.by,
                            "lead": board.lead,
                            "tricks": board.tricks,
                            "plus": board.plus,
                            "minus": board.minus * -1,
                            "pts": board.pts,
                            "percent": "{:.0f}".format(board.percent)
                        }
                        data["board"].append(boardData)
                    scorecards.append(data)
                JSONString = JSONString + json.dumps(scorecards) + ";"

                if not self.dealInfo is None:
                    # Add the deals
                    JSONString = JSONString + "\nlet deals = " + self.dealInfo.getJSON()  + ";"

                # Add the travellers
                JSONString = JSONString + "\nlet travellers = ";
                travellers = {}
                for traveller in self.tournamentData.resultSet.travellerSet.travellers:
                    data = []
                    for line in traveller.travellerLines:
                        linedata = {
                            "ns": line.NSPair,
                            "ew": line.EWPair,
                            "contract": line.contract,
                            "by": line.by,
                            "lead": line.lead,
                            "tricks": line.tricks,
                            "plus": line.score,
                            "minus": '',
                            "nsmps": line.NSMPs,
                            "ewmps": line.EWMPs
                        }
                        if isinstance(line.score, int):
                            if line.score < 0:
                                linedata['plus'] = ''
                                linedata['minus'] = line.score * -1
                        else:
                            line.score = linedata['plus']
                        data.append(linedata)
                    travellers[traveller.boardNum] = data
                JSONString = JSONString + json.dumps(travellers) + ";\n"

                # Assign the string to the HTML element
                scriptTag.string = JSONString

            # Save changes
            with open(self.outputFileVar.get(), "w", encoding="utf-8") as file:
                file.write(str(soup))
            
            self.messageLabel.config(text='Webpage file generation complete.')
            self.messageLabel.config(foreground=CompleteColor)

            # Display the Webpage
            os.startfile(self.outputFileVar.get().replace("/", "\\"))
        else:
            self.messageLabel.config(text='Error - cannot load webpage template file.')
            self.messageLabel.config(foreground="red")
