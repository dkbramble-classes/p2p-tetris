#multithreaded http server needed for a host and guest
#Authors Luke Bassett, Dane Bramble, Patrik Kozak, Brendan Warnick

from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from socketserver import ThreadingMixIn
import json
from urllib.parse import urlparse
import threading
import time

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

playerBoards = {}
joined = False
hosted = False
joinWin = False
hostWin = False
response = "0.0"
class Database(BaseHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
 
    def do_GET(self):
        global hostWin
        global joinWin
        if hostWin == True:
            responseStr = 'Host wins!'
        elif joinWin == True:
            responseStr = 'Join wins!'
        else:
            responseStr = 'none'
        self.send_response(200)
        self.end_headers()
        self.wfile.write(responseStr.encode("utf-8"))

    #receive requests from TetrisGrid
    def do_POST(self):
        # Doesn't do anything with posted data
        global joined
        global hosted
        global response
        global hostWin, joinWin
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        strBody = str(body, 'utf-8')
        #parsedBody = strBody.split("_")
        # After a server is running, a player must delcare as the host.
        # The host is kept track of by the server.
        if strBody == 'host':
            print("host")
            if joined and response != "0.0":
                response = str(time.time() + 6)
            hosted = True
            hostWin = False
            joinWin = False
            playerBoards[1] = {}
            playerBoards[1]["board"] = []
            playerBoards[1]["stone"] = []
            playerBoards[1]["stone_x"] = []
            playerBoards[1]["stone_y"] = []
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
        #print("User " + strBody + " connected to the server.")
        # Once a host is declared, a second player must 'join' the host to play the game.
        # Once joined, the server keeps track of this player too.
        elif strBody == 'join':
            if hosted and response != 0.0:
                response = str(time.time() + 6)
            joined = True
            playerBoards[2] = {}
            playerBoards[2]["board"] = []
            playerBoards[2]["stone"] = []
            playerBoards[2]["stone_x"] = []
            playerBoards[2]["stone_y"] = []
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
        #host time out
        elif strBody == 'hostreset':
            hosted = False
            self.send_response(200)
            self.end_headers()
        #joining player time out
        elif strBody == 'joinreset':
            joined = False
            self.send_response(200)
            self.end_headers()
        #set up player boards and blocks
        elif "Info" in strBody:
            parsedBody = strBody.split("_")
            board = parsedBody[2]
            stone = parsedBody[3]
            if parsedBody[1] == "host":
                playerBoards[1]["board"] = board
                playerBoards[1]["stone"] = stone
                playerBoards[1]["stone_x"] = parsedBody[4]
                playerBoards[1]["stone_y"] = parsedBody[5]
                opponent = json.dumps(playerBoards[2])
            else:
                playerBoards[2]["board"] = board
                playerBoards[2]["stone"] = stone
                playerBoards[2]["stone_x"] = parsedBody[4]
                playerBoards[2]["stone_y"] = parsedBody[5]
                opponent = json.dumps(playerBoards[1])

            self.send_response(200)
            self.end_headers()
            self.wfile.write(opponent.encode("utf-8"))
        #end game functions
        elif strBody == 'hostwin':
            if hostWin == False and joinWin == False:
                hostWin = True
                text = "Host wins!"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(text.encode("utf-8"))
        elif strBody == 'joinwin':
            if joinWin == False and hostWin == False:
                joinWin = True
                text = "Join wins!"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(text.encode("utf-8"))
        #invalid request given
        else:
            print("Didn't receive proper request. Request given: " + strBody)
            self.send_response(400)
            self.end_headers()
#run server
def run(server_class=HTTPServer, handler_class=Database, port=80):
    server_address = '0.0.0.0'
    httpd = ThreadingSimpleServer((server_address, port), handler_class)
    httpd.serve_forever()
run()
