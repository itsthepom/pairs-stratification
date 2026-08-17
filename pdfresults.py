###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Class to write a PDF results file
###############################################################################
import os
from datetime import datetime
import ttkbootstrap as tb
from reportlab.platypus import BaseDocTemplate, Paragraph, KeepTogether, Table, TableStyle, Frame, PageTemplate, NextPageTemplate, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from baseclasses import baseUIClass
from uiparts import UIParts
import filehandling
from appcolours import *

mainFont = "Helvetica"
boldFont = "Helvetica-Bold"

class pdfresults(baseUIClass):
    """ Produces a PDF file containing the event results and runs the UI.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame: Frame, tournamentData, uiparts: UIParts):
        self.frame = frame
        self.tournamentData = tournamentData
        self.uiparts = uiparts
        uiparts.pdfResultsDisplay = self
        self.numLoads = 0
        if frame is not None:
            self.outputFileVar = tb.StringVar()
            self.outputFileVar.trace_add("write", self.fileSelected)
            self.outputMatrix = tb.BooleanVar()

    def getName(self):
        return 'print'
    
    def construct(self, pagebgnd: str):
        self.pagebgnd = pagebgnd
        if self.numLoads != self.tournamentData.numLoads:
            self.numLoads = self.tournamentData.numLoads
            outputFilename = self.tournamentData.getOutputFilename()
            if len(outputFilename) > 0:
                self.outputFileVar.set(self.uiparts.options.getDirectory('outputsdir') + self.uiparts.options.getDirectory('pdfsdir') + self.tournamentData.getOutputFilename() + ".pdf")
            else:
                self.outputFileVar.set("")

        self.labels = []

        label = tb.Label(self.frame, text="Select the new PDF file to be created.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="The results PDF will be written to this file.", font=("Segoe UI", 10), justify='left')
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="Primary", command=lambda: self.pickInputFile())
        label.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.labels.append(label)   
        label = tb.Entry(self.frame, textvariable=self.outputFileVar, width=102, font=("Segoe UI", 10))
        label.grid(row=3, column=0, sticky="w", padx=100)
        self.labels.append(label)   

        label = tb.Label(self.frame, text="Check this box to include the matchpoints matrix.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))
        self.labels.append(label)
        label = tb.Checkbutton(self.frame, text="Include Matrix", variable=self.outputMatrix, bootstyle="Primary")
        label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5))
        self.labels.append(label)

        self.createButton = tb.Button(self.frame, text="Create", bootstyle="Primary", state="disabled", command=lambda: self.createPDF())
        self.createButton.grid(row=6, column=0, sticky="w", padx=20, pady=(20, 10))
        self.labels.append(self.createButton)

        self.completeLabel = tb.Label(self.frame, text="", font=("Segoe UI", 10, "bold"), foreground=msg_completeColor, justify='left')
        self.completeLabel.grid(row=7, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        self.labels.append(self.completeLabel)

        self.backButton = tb.Button(self.frame, text="< Back", bootstyle="primary", width=10, command=self.backPressed)
        self.nextButton = tb.Button(self.frame, text="Next >", bootstyle="primary", width=10, command=self.nextPressed)
        self.labels.append(self.backButton)
        self.labels.append(self.nextButton)

        self.backButton.place(x=630, y=650)
        self.nextButton.place(x=730, y=650)
        
        self.fileSelected('', '', '')
        
    def backPressed(self):
        self.uiparts.root.showPage('stratify')

    def nextPressed(self):
        if self.uiparts.mainMenu.mpfileEnabled:
            self.uiparts.root.showPage('write')
        else:
            self.uiparts.root.showPage('webpage')

    def clearContent(self):
        """Safely destroys all PDF generator widgets, breaks lambda bindings, and resets references."""
        # Clear button command callbacks (breaks lambda closure references)
        if hasattr(self, 'createButton') and self.createButton:
            try:
                self.createButton.configure(command="")
            except Exception:
                pass

        # Iterate through labels list to clear any command callbacks on dynamic buttons
        if hasattr(self, 'labels') and self.labels:
            for widget in self.labels:
                if isinstance(widget, tb.Button):
                    try:
                        widget.configure(command="")
                    except Exception:
                        pass

        # Destroy the frame child entries, buttons, labels
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()

        # Clear list of widget references
        self.labels = []

        # Reset attribute references for Garbage Collection
        self.createButton = None
        self.completeLabel = None

    def pickInputFile(self):
        filename = filehandling.openPDFFile(self.uiparts.options.getDirectory("outputsdir") + self.uiparts.options.config["pdfsdir"])
        if len(filename) > 0:
            self.outputFileVar.set(filename)

    def fileSelected(self, name, index, mode):
        try:
            self.completeLabel.config(text="")
            if len(self.outputFileVar.get()) > 0:
                self.createButton.config(state="normal")
            else:
                self.createButton.config(state="disabled")
        except:
            pass
            
    def createPDF(self, outputFilename=None):
        """ Creates a PDF of the current event results.

            Args:
                outputFilename(str): Optional filename to write to. Used in batch mode.
        """
        # We are in batch mode if an outputFilename is provided
        batchMode = False
        if outputFilename is not None:
            batchMode = True
            pdfFilename = outputFilename
        else:
            # Make sure the output dirs are created
            self.uiparts.options.getDirectory("outputsdir")
            pdfFilename = self.outputFileVar.get()

        if len(pdfFilename) > 0:
            # Sets the title used for page headings and metadata
            dateObj = datetime.strptime(self.tournamentData.tournamentDate, "%d/%m/%Y")
            tournamentTitle = self.tournamentData.tournamentName + ' - ' + dateObj.strftime("%A") + ' ' + dateObj.strftime("%d") + ' ' + dateObj.strftime("%b") + ' ' + dateObj.strftime("%Y")

            # Create our output styles
            styles = getSampleStyleSheet()
            # Create a centered heading style
            centeredHeading = ParagraphStyle(
                'CenteredHeading',
                parent=styles['Heading1'],
                alignment=TA_CENTER,
                fontSize=16,
                fontName=boldFont,
                spaceAfter=1)
            # Create a left-justified section style
            sectionHeading = ParagraphStyle(
                'LeftSection',
                parent=styles['Heading3'],
                alignment=TA_LEFT,
                fontSize=14,
                fontName=boldFont,
                spaceAfter=1)
            # Create a left-justified direction style
            directionHeading = ParagraphStyle(
                'DirectionHeading',
                parent=styles['Heading3'],
                alignment=TA_LEFT,
                fontSize=12,
                fontName=boldFont,
                spaceAfter=1)
            # Create a left-justified table column heading style
            tableHeading = ParagraphStyle(
                'TableHeading',
                parent=styles['Heading4'],
                alignment=TA_LEFT,
                fontSize=10,
                fontName=boldFont,
                spaceAfter=0)
            # Create the score table styles
            tableStyles = TableStyle([
                ('BACKGROUND', (0,0), (-1,1), colors.toColor('rgb(238,238,238)')),  # header row
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (3,0), (4,-1), 'LEFT'),
                ('FONTNAME', (0,2), (-1,-1), mainFont),     # All table cells
                ('FONTNAME', (0,0), (-1,1), boldFont),      # Top 2 rows
                ('SPAN', (6,0), (7,0)),
                ('GRID', (0,2), (-1,-1), 0.5, colors.grey),
                ('BOX', (0,0), (-1,-1), 1, colors.grey),
                ('BOTTOMPADDING', (0,0), (-1,1), 0),
                ('BOTTOMPADDING', (0,1), (-1,1), 2),
                ('TOPPADDING', (0,1), (-1,1), 0),
                ('TOPPADDING', (0,0), (-1,0), 2)
            ])
            # Create the rankings table column widths
            tableColWidths = [35, 35, 35, 200, 110 if self.tournamentData.eventType == 0 else 45, 50, 22, 22]

            # Create the document template
            class MyDocTemplate(BaseDocTemplate):
                def beforeDocument(self):
                    c = self.canv
                    c.setTitle(tournamentTitle)
            doc = MyDocTemplate(pdfFilename,
                                pagesize=A4,
                                leftMargin=36,        # points (1 point = 1/72 inch)
                                rightMargin=36,
                                topMargin=36,
                                bottomMargin=36)

            # Set our two headings and calculate their height
            heading1 = Paragraph(self.tournamentData.clubName, centeredHeading)
            w, heading1Height = heading1.wrap(doc.width, doc.topMargin)
            heading2 = Paragraph(tournamentTitle, centeredHeading)
            w, heading2Height = heading2.wrap(doc.width, doc.topMargin)
            totalHeadingHeight = heading1Height + heading2Height

            # Create two frames - one portrait and one landscape
            portraitFrame = Frame(x1=36, y1=36,
                                    width=A4[0] - 72,
                                    height=A4[1] - 72 - totalHeadingHeight)
            landscapeFrame = Frame(x1=36, y1=36,
                                    width=landscape(A4)[0] - 72,
                                    height=landscape(A4)[1] - 72 - totalHeadingHeight)

            # Create a callback to draw the page headings
            def drawPageHeading(canvas, doc):
                canvas.saveState()
                # Draw near the top edge of the page, regardless of orientation
                frame = doc.pageTemplate.frames[0]
                center_x = frame._width / 2
                y = frame._y1 + frame._height + 25
                w, headingHeight = heading1.wrap(doc.width, doc.topMargin)
                heading1.drawOn(canvas, center_x - w / 2 + frame._x1, y)
                w, headingHeight = heading2.wrap(doc.width, doc.topMargin)
                heading2.drawOn(canvas, center_x - w / 2 + frame._x1, y - headingHeight)
                canvas.restoreState()

            # Create two page templates for the frames
            portraitTemplate = PageTemplate(id="resultPortrait",
                                            frames=[portraitFrame],
                                            pagesize=A4,
                                            onPage=drawPageHeading)
            landscapeTemplate = PageTemplate(id="resultLandscape",
                                                frames=[landscapeFrame],
                                                pagesize=landscape(A4),
                                                onPage=drawPageHeading)
            doc.addPageTemplates([portraitTemplate, landscapeTemplate])

            # We build a "story" out of a set of "blocks"
            story = []
            block = []

            def printResults(eventType, rankingSet, pairData, heading, stratumNumber):
                nonlocal block
                tableRows = []
                def drawResultHeadings(directionString):
                    # Draw the results table headings
                    block.append(Paragraph(directionString, directionHeading))
                    headingData = ["", "", "", "", "",
                                    Paragraph("Master", tableHeading),
                                    Paragraph("Slams", tableHeading),
                                    ""]
                    tableRows.append(headingData)
                    headingData = [Paragraph("Pos", tableHeading),
                                    Paragraph("Pair", tableHeading),
                                    Paragraph("Strat", tableHeading),
                                    Paragraph("Pair", tableHeading),
                                    Paragraph("Score", tableHeading) if eventType == 0 or eventType == 2 else Paragraph("IMPs", tableHeading),
                                    Paragraph("Points", tableHeading),
                                    Paragraph("S", tableHeading),
                                    Paragraph("G", tableHeading)]
                    tableRows.append(headingData)

                def printResultRows(eventType, results, pairData):
                    # Draw each results row
                    for result in results:
                        pair = pairData[result.pairNumber]
                        masterpoints = str(pair.masterpoints) if pair.masterpoints != 0 else ""
                        if len(masterpoints) > 0 and pair.awardedStratum != None and pair.awardedStratum != stratumNumber:
                            masterpoints = masterpoints + '(' + chr(ord('A') + pair.awardedStratum - 1) + ')'
                        resultRowData = [str(result.position),
                                         str(result.pairNumber),
                                         "A" if pair.strat == 0 else "B" if pair.strat == 1 else "C",
                                         result.player1Name + " & " + result.player2Name,
                                         "",
                                         masterpoints,
                                         str(pair.sslams) if pair.sslams != 0 else "",
                                         str(pair.gslams) if pair.gslams != 0 else ""]
                        if eventType == 0:
                            resultRowData[4] = "{:.1f}".format(result.rawscore) + "/" + "{:.0f}".format(result.maxscore) + "  =  " + "{:.2f}".format(result.score) + "%"
                        elif eventType == 1:
                            resultRowData[4] = "{:>+7.2f}".format(result.score)
                        else:
                            resultRowData[4] = "{:>+7.0f}".format(result.score)
                        tableRows.append(resultRowData)
                    resultRowTable = Table(tableRows, colWidths=tableColWidths)
                    resultRowTable.setStyle(tableStyles)
                    block.append(resultRowTable)

                block.append(Paragraph(heading, sectionHeading))
                # Either single winner rankings or N/S rankings first
                directionString = ''
                if self.tournamentData.numWinners == 2:
                    directionString = "North/South"
                drawResultHeadings(directionString)
                printResultRows(self.tournamentData.eventType, rankingSet[0], pairData)
                if self.tournamentData.numWinners == 2:
                    tableRows = []
                    drawResultHeadings("East/West")
                    printResultRows(self.tournamentData.eventType, rankingSet[1], pairData)
            
            # Print the ranking lists - first the overall ranking
            printResults(self.tournamentData.eventType, self.tournamentData.resultSet.overallRankings[0], self.tournamentData.resultSet.pairData, "Stratum A - Overall Rankings", 1)
            story.append(KeepTogether(block))

            # Add strata rankings
            block = []
            if len(self.tournamentData.resultSet.overallRankings[1][0]) + len(self.tournamentData.resultSet.overallRankings[1][1])> 0:
                heading = "Stratum B - " + self.tournamentData.resultSet.stratumLabels[0] + " and lower"
                printResults(self.tournamentData.eventType, self.tournamentData.resultSet.overallRankings[1], self.tournamentData.resultSet.pairData, heading, 2)
                story.append(KeepTogether(block))
                if len(self.tournamentData.resultSet.overallRankings[2][0]) > 0:
                    block = []
                    heading = "Stratum C - " + self.tournamentData.resultSet.stratumLabels[1] + " and lower"
                    printResults(self.tournamentData.eventType, self.tournamentData.resultSet.overallRankings[2], self.tournamentData.resultSet.pairData, heading, 3)
                    story.append(KeepTogether(block))

            # Add matrix, if requested. Not enabled in batch mode, but could be.
            block = []
            if not batchMode and self.outputMatrix.get():
                # Create the matrix table styles
                matrixTableStyles = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.toColor('rgb(238,238,238)')),  # header row
                    ('BACKGROUND', (0,0), (0,-1), colors.toColor('rgb(238,238,238)')),  # left column
                    ('ALIGN', (0,0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0,0), (0,-1), 'CENTER'),
                    ('ALIGN', (1,1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0,1), (-1,-1), mainFont),     # All table cells
                    ('FONTNAME', (0,0), (-1,0), boldFont),      # Top row
                    ('FONTNAME', (0,0), (0,-1), boldFont),      # Left column
                    ('FONTNAME', (-1,0), (-1,-1), boldFont),    # Right column
                    ('BOX', (0,0), (-1,-1), 1, colors.grey),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.toColor('rgb(221,221,221)')),
                    ('LEFTPADDING', (0,0), (-1,-1), 1),
                    ('RIGHTPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 1)
                ])
                matrixHeading = ParagraphStyle(
                    'TableHeading',
                    parent=styles['Heading4'],
                    alignment=TA_CENTER,
                    fontSize=10,
                    fontName=boldFont,
                    spaceAfter=2)
                # Switch to landscape orientation to accommodate a wide matrix
                story.append(NextPageTemplate("resultLandscape"))
                story.append(PageBreak())
                # Heading and board numbers rows
                block.append(Paragraph("Boards", matrixHeading))
                matrixKeys = list(self.tournamentData.resultSet.resultsMatrix.matrixLine.keys())
                matrixTableRows = [''] * (max(matrixKeys) + 1)
                matrixRowData = [''] + list(str(i) for i in range(1, self.tournamentData.numBoards + 1)) + ["Total"]
                matrixTableRows[0] = matrixRowData
                # Each line of the matrix
                keyNum = 0
                for matrixLine in self.tournamentData.resultSet.resultsMatrix.matrixLine.values():
                    matrixTableRows[matrixKeys[keyNum]] = [str(matrixKeys[keyNum])]
                    for i in range(len(matrixLine.score)):
                        scorestr = ""
                        score = matrixLine.score[i]
                        if score != None:
                            scorestr = str(int(score)) if self.tournamentData.eventType != 1 else f"{score:.2f}"
                        matrixTableRows[matrixKeys[keyNum]].append(scorestr)
                    score = matrixLine.total
                    scorestr = str(int(score)) if self.tournamentData.eventType != 1 else f"{score:.2f}"
                    matrixTableRows[matrixKeys[keyNum]].append(scorestr)
                    keyNum = keyNum + 1
                # If there were missing pairs, their row will be empty. Fill the pair number
                for matrixLine in range(1, len(matrixTableRows)):
                    if not isinstance(matrixTableRows[matrixLine], list):
                        matrixTableRows[matrixLine] = [str(matrixLine)]
                # Convert the list of lists into an output Table
                matrixTable = Table(matrixTableRows)
                matrixTable.setStyle(matrixTableStyles)
                block.append(matrixTable)
                story.append(KeepTogether(block))

            # Pass the assembled story into build. This assembles the blocks into a PDF
            doc.build(story)

            if not batchMode:
                # Display UI message that the operation is complete
                self.completeLabel.config(text="PDF file generation complete.")

                # Display the PDF
                os.startfile(pdfFilename.replace("/", "\\"))
