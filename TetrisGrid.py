#!/usr/bin/env python3

#This is a pygame Tetris game that connects to a centralized server and another person.
#See the README for more information.
#Authors: Luke Bassett, Dane Bramble, Patrik Kozak, Brendan Warnick
#Pieces of the pygame Tetris were inspired by the Tetris game made by Kevin Chabowski
import random, time, select, os, ast, json
from random import randrange as rand
import pygame, sys
import threading
import requests, socket

playerStatus = '' #Whether the player is hosting or joining the game
URL = '' #The URL of the server
menuGo = True #Whether or not the menu will display after the logo

#ASCII color codes for the logo
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
WHITE = '\033[0m'
BLACK = '\u001b[30;1m'

# The configuration
config = {
    'cell_size':    20,
    'cols':     8,
    'rows':     16,
    'delay':    750,
    'maxfps':   30
}

colors = [
(0,   0,   0  ),
(255, 0,   0  ),
(0,   150, 0  ),
(0,   0,   255),
(255, 120, 0  ),
(255, 255, 0  ),
(180, 0,   255),
(0,   220, 220)
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

def rotate_clockwise(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
        for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for i in range(config['cols'])]] + board

def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy+off_y-1 ][cx+off_x] += val
    return mat1

def new_board():
    board = [ [ 0 for x in range(config['cols']) ]
            for y in range(config['rows']) ]
    board += [[ 1 for x in range(config['cols'])]]
    return board

class TetrisApp(object):
    global URL, playerStatus

    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250,25)
        self.width = config['cell_size']*config['cols'] * 2 + 3*config['cell_size']
        self.height = config['cell_size']*config['rows']
        self.endStatus = ''

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
                                                     # mouse movement
                                                     # events, so we
                                                     # block them.
        self.init_game()

    def new_stone(self):
        self.stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True
            r = requests.post(URL, self.endStatus)
            self.endStatus = r.text

    def init_game(self):
        self.board = new_board()
        self.new_stone()

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image =  pygame.font.Font(
                pygame.font.get_default_font(), 24).render(
                    line, False, (255,255,255), (0,0,0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
              self.width // 2-msgim_center_x,
              self.height // 2-msgim_center_y+i*22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y  = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x+x) *
                              config['cell_size'],
                            (off_y+y) *
                              config['cell_size'],
                            config['cell_size'],
                            config['cell_size']),0)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > config['cols'] - len(self.stone[0]):
                new_x = config['cols'] - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x
    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self):
        if not self.gameover and not self.paused:
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                  self.board,
                  self.stone,
                  (self.stone_x, self.stone_y))
                self.new_stone()
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                              self.board, i)
                            break
                    else:
                        break

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            'ESCAPE':   self.quit,
            'LEFT':     lambda:self.move(-1),
            'RIGHT':    lambda:self.move(+1),
            'DOWN':     self.drop,
            'UP':       self.rotate_stone,
            'p':        self.toggle_pause,
            'SPACE':    self.start_game
        }

        self.gameover = False
        self.paused = False
        if playerStatus == 'host':
            pygame.display.set_caption('Host Game')
            self.endStatus = 'joinwin'
        elif playerStatus == 'join':
            pygame.display.set_caption('Join Game')
            self.endStatus = 'hostwin'

        pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0,0,0))
            if self.gameover:
                self.center_msg("""Game Over!
 {}""".format(self.endStatus))
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0,0))
                    self.draw_matrix(self.stone,
                                     (self.stone_x,
                                      self.stone_y))
                    r = requests.post(URL, "Info _" + playerStatus + "_" + str(self.board) + "_" + str(self.stone) + "_" + str(self.stone_x) + "_" + str(self.stone_y))
                    opponent = json.loads(r.text)
                    if isinstance(opponent["board"], str):
                        newBoard = ast.literal_eval(opponent["board"])
                        newStone = ast.literal_eval(opponent["stone"])
                        self.draw_matrix(newBoard, (11,0))
                        self.draw_matrix(newStone, ((int(opponent["stone_x"])+3+8),(int(opponent["stone_y"]))))
                    q = requests.get(URL)
            #print(q.text == 'none')
                    if not q.text == 'none':
                        self.endStatus = q.text
                        self.gameover = True
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.drop()
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                        +key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(config['maxfps'])

#This function connects to the local server and waits for a connection from the other player.
#Once the other player has connected, this function starts the Tetris game
def joinGame():
    global playerStatus #Whether you host or join the game
    global menuGo #If the player can still return to the menu
    global URL # The URL of the server
    joinwait = True #This boolean is True while the server seeks a connection to the server and the other player
    errorcount = 0 #Don't print more than one error
    os.system('cls' if os.name == 'nt' else 'clear')
    hostname = input("What is the hostname / ip address of the other player?\n") #Ask the player for the name of the host
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Trying to connect to ' + hostname + '...\n')
    URL = "http://" + hostname #get the url for the centralized server
    playerStatus = 'join'
    timeout = time.time() + 30 #The loop will timeout in 30 seconds
    countdown = 0.0 #Countdown until the game starts
	#This loops while the host is searching or it times out
    while joinwait:
        try:
            r = requests.post(URL, data=playerStatus, timeout = 1) #Send the player status to the server, get a time stamp of when the game should start back
            if float(r.text) > time.time(): #If the time given is greater than the current time, then the connection is active
                joinwait = False #Stop looping
                countdown = float(r.text)  #set the time until game start
        except requests.exceptions.ConnectionError: # If the server cannot connect
            if errorcount == 0:
                print("Still searching for host")
            errorcount = 1
        if timeout < time.time():# If the time to search is expired
            print('No host player found, please try again later\n')
            joinwait = False #Stop looping, go back to menu
            timeout = -1 #Status, the search timed out
            try: #Send a message to the server that you are no longer searching for a game
                playerStatus = 'joinreset'
                r = requests.post("http://localhost", data=playerStatus)
            except requests.exceptions.ConnectionError: # If the server cannot connect
                print("")
	#if the search didn't timeout
    if timeout != -1:
        menuGo = False
        os.system('cls' if os.name == 'nt' else 'clear')
        try:# ensure that tty will be reset in the end
            timecount = True
            while countdown > time.time(): #Wait until the same time to start the game
                if timecount:
                    timecount = False
                    print("Host found, playing game in " + str(int(countdown - time.time())) + " seconds")
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Game Started!")
            App = TetrisApp() #Create game object
            App.run() #Start the game
        finally: #once the game is over, reset status
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                playerStatus = 'joinreset'
                r = requests.post("http://localhost", data=playerStatus)
            except requests.exceptions.ConnectionError:
                print("")
#This function connects to the local server and waits for a connection from the other player.
#Once the other player has connected, this function starts the Tetris game
def hostGame():
    global playerStatus #Whether you host or join the game
    global menuGo #If the player can still return to the menu
    global URL # The URL of the server
    hostwait = True #This boolean is True while the server seeks a connection to the server and the other player
    errorcount = 0 #Don't print more than one error
    playerStatus = 'host'
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Hosting a game, waiting for a player to join...\n')
    URL = "http://localhost"
    timeout = time.time() + 30 #The loop will timeout in 30 seconds
    countdown = 0.0 #Countdown until the game starts
	#This loops while the host is searching or it times out
    while hostwait:
        try:
            r = requests.post("http://localhost", data=playerStatus, timeout = 1) #Send the player status to the server, get a time stamp of when the game should start back
            if float(r.text) > time.time(): #If the time given is greater than the current time, then the connection is active
                hostwait = False #Stop looping
                countdown = float(r.text) #set the time until game start
        except requests.exceptions.ConnectionError: # If the server cannot connect
            if errorcount == 0:
                print("Still searching for other players")
            errorcount = 1
        if timeout < time.time(): # If the time to search is expired
            print('No other players connected, please try again later\n')
            hostwait = False #Stop looping, go back to menu
            timeout = -1 #Status, the search timed out
            try: #Send a message to the server that you are no longer searching for a game
                playerStatus = 'hostreset'
                r = requests.post("http://localhost", data=playerStatus)
            except requests.exceptions.ConnectionError:
                print("")
	#if the search didn't timeout
    if timeout != -1:
        menuGo = False
        os.system('cls' if os.name == 'nt' else 'clear')
        try:# ensure that tty will be reset in the end
            timecount = True
            while countdown > time.time(): #Wait until the same time to start the game
                if timecount:
                    timecount = False
                    print("Player found, playing game in " + str(int(countdown - time.time())) + " seconds")
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Game Started!")
            App = TetrisApp() #Create game object
            App.run() #Start the game
        finally: #Once the game is over
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                playerStatus = 'hostreset'
                r = requests.post("http://localhost", data=playerStatus) #Send a message to the server that you are no longer searching for a game
            except requests.exceptions.ConnectionError:
                print("")
#this method is the menu for the player to use. From here the player can choose to host or join a game.
def menu():
    global menuGo #While this is true the menu screen will continue to ask the player to play a game
    os.system('cls' if os.name == 'nt' else 'clear')
    #print the logo
    print(RED + "MMMMMM" + WHITE + " MMMMMM" + YELLOW + "  MMMMMM" + GREEN + " MMMML" + BLUE + "  MMMMM" + PURPLE + " MMMMMM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M   M" + BLUE + "    M" + PURPLE + "   MM")
    print(RED + "  MM" + WHITE + "   MMMM" + YELLOW + "      MM" + GREEN + "   MMMMP" + BLUE + "    M" + PURPLE + "   MMMMMM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M  M" + BLUE + "     M" + PURPLE + "       MM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M   M" + BLUE + "    M" + PURPLE + "       MM")
    print(RED + "  MM" + WHITE + "   MMMMMM" + YELLOW + "    MM" + GREEN + "   M    M" + BLUE + " MMMMM" + PURPLE + " MMMMMM\n" + WHITE)
    print("Welcome!\n\nTo start a game you'll need another player.")
    while menuGo == True:
        text = input("Would you like to host or join a game (Type 'host' for host, 'join' for join, and 'quit' for quit)\n") #prompt for a response
        if  text.lower() == 'join': #if the player types 'join'
            joinGame()
        elif text.lower() == 'host':#if the player types 'host'
            hostGame()
        elif text.lower() == 'quit': #if the player types 'quit', leave the game
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Goodbye!")
            menuGo = False #stop the menu
        else: #if the input was not one of the above options
            print(text + " is not a valid option, please type either 'host' or 'join'\n")
menu() #Run the game
