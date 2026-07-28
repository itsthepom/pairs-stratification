###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Local loopback web server that serves up the help files
###############################################################################
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading
import webbrowser
import os
import sys
import socket
from functools import partial
from tkinter import messagebox

class helpserver:
    """ Runs a local help server.

        Args:
            port(int): Port to run the server on. Default 8080.
            directory(str): Directory holding the pre-built help site.
    """
    def __init__(self, port: int=8080, directory: str="helpdocs/site"):
        def isPortInUse(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(("127.0.0.1", port)) == 0
                
        foundPort = False
        portBase = port
        while not foundPort:
            if isPortInUse(port):
                port = port + 1
                if port > portBase + 10:
                    break
            else:
                foundPort = True
        if not foundPort:
            messagebox.showerror(title="Error", message="Unable to start Help server")
            self.helpAvailable = False
        else:
            self.helpAvailable = True
            self.port = port
            if hasattr(sys, "_MEIPASS"):
                self.sitepath =  os.path.join(sys._MEIPASS, directory)  # PyInstaller temp dir
            else:
                self.sitepath = os.path.join(os.getcwd(), directory);
            # Run the server in a separate thread
            server_thread = threading.Thread(target=self.serve_mkdocs_site, daemon=True)
            server_thread.start()

    def serve_mkdocs_site(self):
        handler = partial(SimpleHTTPRequestHandler, directory=self.sitepath)
        port = self.port
        with socketserver.TCPServer(("127.0.0.1", self.port), handler) as httpd:
            print(f"Serving MkDocs site at http://localhost:{port}")
            httpd.serve_forever()

    def serveHelp(self):
        if self.helpAvailable:
            webbrowser.open(f"http://localhost:{self.port}")
