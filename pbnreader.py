import json

class PBNReader:
    """ Class to read the content of a .PBN file and return a JSON of it
    """
    def __init__(self):
        self.event = ''
        self.date = ''
        self.boards = None

    def read(self, filename: str):
        """ Reads a .PBN file into class variables.

            Args:
                filename(str): Full pathname of the .PBN file.
        """
        self.boards = {}
        boardNum = 0;
        # Open the PBN file
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                cleanLine = line.strip()
                if len(cleanLine) > 0:
                    if cleanLine[0] == '%':
                        continue
                    elif cleanLine[0] == '[':
                        directive = cleanLine[1:-1].split()
                        for dirIndex in range(1, len(directive)):
                            directive[dirIndex] = directive[dirIndex].replace('"', '')
                        if directive[1] != '#':
                            if directive[0] == "Event":
                                self.event = ' '.join(directive[1:])
                            elif directive[0] == "Date":
                                self.date = ' '.join(directive[1:])
                            elif directive[0] == "Board":
                                boardNum = directive[1]
                                if not boardNum in self.boards:
                                    self.boards[boardNum] = {}
                            elif directive[0] == "Dealer":
                                self.boards[boardNum]["dealer"] = directive[1]
                            elif directive[0] == "Vulnerable":
                                self.boards[boardNum]["vulnerability"] = directive[1]
                            elif directive[0] == "Deal":
                                self.boards[boardNum]["deal"] = []
                                dealer = directive[1][:1]
                                directive[1] = directive[1][2:]
                                directive[4] = directive[4].replace('"', '')
                                allhands = []
                                if dealer == 'N':
                                    allhands = directive[1:5]
                                elif dealer == 'E':
                                    allhands.append(directive[4])
                                    allhands.append(directive[1])
                                    allhands.append(directive[2])
                                    allhands.append(directive[3])
                                elif dealer == 'S':
                                    allhands.append(directive[3])
                                    allhands.append(directive[4])
                                    allhands.append(directive[1])
                                    allhands.append(directive[2])
                                else:
                                    allhands.append(directive[2])
                                    allhands.append(directive[3])
                                    allhands.append(directive[4])
                                    allhands.append(directive[1])
                                self.boards[boardNum]["deal"] = [hand.split('.') for hand in allhands]
                            elif directive[0] == "DoubleDummyTricks":
                                digits = [int(char, 16) for char in directive[1]]
                                self.boards[boardNum]["tricks"] = [digits[i:i+5] for i in range(0, len(digits), 5)]
        return
    
    def getJSON(self) -> str:
        return json.dumps(self.boards)
