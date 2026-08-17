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
import logging

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
    # Define a specific path for the log file
    log_dir = os.path.expanduser("~/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(__name__)

    # Get the name of the cache file for the players DB from mempad
    if writeCacheFile:
        cachedir = optionsInstance.getDirectory('outputsdir') + 'cache/'
        cachefile = cachedir + 'MPData.csv'

    # Read the players DB so we can look up player ranks
    url = "https://www.mempad.co.uk/sites/default/files/~integration/members.csv"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Got the response OK. Get the data and cache it
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
        logger.error(
            f"HTTP Error: {errh} | Status Code: {response.status_code} | Response Text: {response.text[:200]}"
        )

    except requests.exceptions.ConnectionError as errc:
        # Captures DNS failures, refused connections, or network drops
        messagebox.showerror("Error", f"Error Connecting to server: {errc}")
        logger.error(f"Error Connecting to server: {errc}")

    except requests.exceptions.Timeout as errt:
        # Captures request timeouts
        messagebox.showerror("Error", f"Timeout Error: {errt}")
        logger.error(f"Timeout Error: {errt}")

    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests-related issue
        messagebox.showerror("Error", f"Requests Exception: {err}")
        logger.error(f"Requests Exception: {err}")

    except OSError as io_err:
        # Captures permission errors, missing directory path errors, or disk full errors
        messagebox.showerror("Error", f"File I/O Error writing cache file to '{cachefile}': {io_err}")
        logger.error(f"File I/O Error writing cache file to '{cachefile}': {io_err}")

    except Exception as e:
        # Log unexpected Python exceptions along with the full stack trace
        logger.exception(f"An unexpected error occurred: {e}")        # Can't get rankings CSV. Use the last cached one instead
        if not writeCacheFile or not os.path.exists(cachefile):
            messagebox.showerror("Error", "Unable to read member data from Internet and no cached copy.\n\nStratification will not be available.")
            return 1
        else:
            with open(cachefile, 'r') as file:
                data = io.StringIO(file.read(-1))
            messagebox.showwarning("Warning", "Unable to read member data from Internet - using cached copy.\n\nMember ranks may be out of date.")
    # Read the CSV into a dictionary, keyed by masterpoint number, with rank as value
    data.seek(0)
    reader = csv.DictReader(data)
    memberDict = {}
    for row in reader:
        memberDict[row['Master Point Number']] = row['Postcode and Rank'].split(" - ",1)[-1]
    return memberDict

