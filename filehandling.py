###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# File handling helper functions
###############################################################################
from tkinter import filedialog as fd
from tkinter import messagebox
import requests
import csv
import io
import os
import applogger

def openResultsFile(startingDir: str, forWriting: bool):
    """ Displays a file chooser dialog for input and output USEBIO results files.

        Args:
            startingDir(str): directory to open the file chooser at.

        Returns:
            str: Full filename of picked file or None.
    """
    filetypes = (
        ('Results files', '*.xml'),
        ('All files', '*.*')
    )
    if startingDir == None or startingDir == "":
        startingDir = '/'
    fileObject = None
    if forWriting:
        fileObject = fd.asksaveasfilename(title='Save results file', initialdir=startingDir, filetypes=filetypes, defaultextension='.xml')
    else:
        fileObject = fd.askopenfilename(title='Open results file', initialdir=startingDir, filetypes=filetypes)
    return fileObject
    
def findResultsFileDirectory():
    """ Displays a directory chooser dialog for input USEBIO results files.
    
        Returns:
            str: Full pathname of picked directory or None.
    """
    return(fd.askdirectory(title='Locate results directory', initialdir='/', mustexist=True))

def findOutputsFileDirectory():
    """ Displays a directory chooser dialog for output USEBIO results files.
    
        Returns:
            str: Full pathname of picked directory or None.
    """
    return(fd.askdirectory(title='Locate outputs directory', initialdir='/', mustexist=True))

def findHandRecordsFileDirectory():
    """ Displays a directory chooser dialog for input hand records (PBN) files.
    
        Returns:
            str: Full pathname of picked directory or None.
    """
    return(fd.askdirectory(title='Locate hand records directory', initialdir='/', mustexist=True))

def openWebfileTemplate(startingDir):
    """ Displays a file chooser dialog for input web template files.

        Args:
            startingDir(str): directory to open the file chooser at.

        Returns:
            str: Full filename of picked file or None.
    """
    filetypes = (
        ('Results files', '*.html'),
        ('All files', '*.*')
    )
    if startingDir == None or startingDir == "":
        startingDir = '/'
    return(fd.askopenfilename(title='Locate web file template file', initialdir=startingDir, filetypes=filetypes))

def openHandRecordFile(startingDir):
    """ Displays a file chooser dialog for input hand record (PBN) files.

        Args:
            startingDir(str): directory to open the file chooser at.

        Returns:
            str: Full filename of picked file or None.
    """
    filetypes = (
        ('Hand record files', '*.pbn'),
        ('All files', '*.*')
    )
    if startingDir == None or startingDir == "":
        startingDir = '/'
    return(fd.askopenfilename(title='Locate hand record file', initialdir=startingDir, filetypes=filetypes))

def openPDFFile(startingDir):
    """ Displays a file chooser dialog for output PDF files.

        Args:
            startingDir(str): directory to open the file chooser at.

        Returns:
            str: Full filename of picked file or None.
    """
    filetypes = (
        ('Portable Document Format files', '*.pdf'),
        ('All files', '*.*')
    )
    if startingDir == None or startingDir == "":
        startingDir = '/'
    return(fd.asksaveasfilename(title='Locate PDF print file', initialdir=startingDir, filetypes=filetypes, defaultextension='.pdf'))

def openWebpageFile(startingDir):
    """ Displays a file chooser dialog for a output web page file.

        Args:
            startingDir(str): directory to open the file chooser at.

        Returns:
            str: Full filename of picked file or None.
    """
    filetypes = (
        ('Results files', '*.html'),
        ('All files', '*.*')
    )
    if startingDir == None or startingDir == "":
        startingDir = '/'
    return(fd.asksaveasfilename(title='Locate webpage output file', initialdir=startingDir, filetypes=filetypes, defaultextension='.html'))

def readPlayersDB(writeCacheFile: bool, optionsInstance) -> dict:
    """ Reads the players CSV DB from MEMPAD, failing which the local cache file.

        Args:
            writeCacheFile(bool): True to enable local cache file writing.
        Returns:
            Players CSV DB as an io.StringIO
    """
    # Get the name of the cache file for the players DB from mempad
    if writeCacheFile:
        cachedir = optionsInstance.getDirectory('outputsdir') + 'cache/'
        cachefile = cachedir + 'MPData.csv'

    # Read the players DB so we can look up player ranks
    exceptionOccurred = False
    url = "https://www.mempad.co.uk/sites/default/files/~integration/members.csv"
    try:
        applogger.applog.info("Fetching member data")
        response = requests.get(url)
        if response.status_code == 200:
            # Got the response OK. Get the data and cache it
            applogger.applog.info(f"HTTP Success: Status Code: {response.status_code}")
            # Set the encoding explicitly (usually 'utf-8') to avoid chardet getting it wrong
            response.encoding = 'utf-8'
            data = io.StringIO(response.text)
            if writeCacheFile:
                if not os.path.exists(cachedir):
                    os.makedirs(cachedir)
                with open(cachefile, 'w') as file:
                    file.write(data.read())
        else:
            raise Exception('Bad HTTP status')
    except requests.exceptions.HTTPError as errh:
        # Captures 4xx/5xx HTTP errors, including response status and body
        applogger.applog.error(f"HTTP Error: {errh} | Status Code: {response.status_code} | Response Text: {response.text[:200]}")
        exceptionOccurred = True

    except requests.exceptions.ConnectionError as errc:
        # Captures DNS failures, refused connections, or network drops
        applogger.applog.error(f"Error Connecting to server: {errc}")
        exceptionOccurred = True

    except requests.exceptions.Timeout as errt:
        # Captures request timeouts
        applogger.applog.error(f"Timeout Error: {errt}")
        exceptionOccurred = True

    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests-related issue
        applogger.applog.error(f"Requests Exception: {err}")
        exceptionOccurred = True

    except OSError as io_err:
        # Captures permission errors, missing directory path errors, or disk full errors
        applogger.applog.error(f"File I/O Error writing cache file to '{cachefile}': {io_err}")
        exceptionOccurred = True

    except Exception as e:
        # Log unexpected Python exceptions along with the full stack trace
        applogger.applog.exception(f"Exception fetching member data: {e}")
        exceptionOccurred = True

    if exceptionOccurred:
        # Can't get rankings CSV. Use the last cached one instead
        if not writeCacheFile or not os.path.exists(cachefile):
            messagebox.showerror("Error", "Unable to read member data from Internet and no cached copy.\n\nStratification will not be available.")
            return 1
        else:
            messagebox.showwarning("Warning", "Unable to read member data from Internet - using cached copy.\n\nMember ranks may be out of date.")
            with open(cachefile, 'r') as file:
                data = io.StringIO(file.read(-1))

    memberDict = {}
    try:
        # Read the CSV into a dictionary, keyed by masterpoint number, with rank as value
        data.seek(0)
        reader = csv.DictReader(data)
        for row in reader:
            memberDict[row['Master Point Number']] = row['Postcode and Rank'].split(" - ",1)[-1]
    except Exception as e:
        applogger.applog.exception(f"Exception reading member data from file: {e}")
        pass
    
    return memberDict

