#!/usr/bin/env python
"tetris -- a brand new game written in python by Alfe"

import sys, random, time, select, os, termios
import tetris_server
import threading
import requests

playerStatus = ''
menuGo = True
width = 10
height = 27

blocks = [ [ (0,0), (0,1),  (0,-1),  (1,0)  ],  # T
           [ (0,0), (1,0),  (2,0),   (-1,0) ],  # I
           [ (0,0), (0,1),  (1,1),  (-1,0)  ],  # S
           [ (0,0), (0,-1), (1,-1), (-1,0)  ],  # Z
           [ (0,0), (0,1),  (1,1),   (1,0)  ],  # O
           [ (0,0), (-1,1), (-1,0),  (1,0)  ],  # L
           [ (0,0), (1,1),  (-1,0),  (1,0)  ],  # J
           ]

inverted     = '\033[7;1m'
blue         = '\033[7;34m'
normal       = '\033[0m'
clear_screen = '\033[2J'  # clear the screen
home         = '\033[H'   # goto top left corner of the screen
# (the latter two were found using 'clear | od -c')
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
WHITE = '\033[0m'
BLACK = '\u001b[30;1m'

empty = '  '
black = inverted + '  ' + normal  # two inverted spaces
blue  = blue     + '  ' + normal  # two inverted spaces
floor = '=='

left  = 'left'
right = 'right'
turn  = 'turn'
down  = 'down'
quit  = 'quit'

shaft = None

def play_tetris():
    initialize_shaft()
    next_block = get_next(blocks[0])
    previous_block = next_block
    while True:  # until game is lost
        block = next_block
        next_block = get_next(previous_block)
        previous_block = next_block
        coordinates = (int(width/2-1), 6)  # in the middle at the top
        if not place_block(block, coordinates, blue):  # collision already?
            return  # game is lost!
        next_fall_time = time.time() + fall_delay()
        # ^^^ this is the time when the block will fall automatically
        #     one line down
        while True:  # until block is placed fixedly
            print_shaft()
            remove_block(block, coordinates)
            x, y = coordinates
            try:
                try:
                    command = get_command(next_fall_time)
                except Timeout:  # no command given
                    raise Fall()
                else:  # no exception, so process command:
                    if  command == left:
                        new_coordinates = (x-1, y)
                        new_block = block
                    elif command == right:
                        new_coordinates = (x+1, y)
                        new_block = block
                    elif command == turn:
                        new_coordinates = (x, y)
                        new_block = turn_block(block)
                    elif command == down:
                        raise Fall()
                    elif command == quit:
                        return
                    else:
                        raise Exception("internal error: %r" % command)
                    if place_block(new_block, new_coordinates,
                                   blue):  # command ok?
                        # execute the command:

                        block       = new_block
                        coordinates = new_coordinates
                    else:
                        place_block(block, coordinates, blue)
                        # ignore the command which could not be executed
                        # maybe beep here or something ;->
            except Fall:
                # make the block fall automatically:
                new_coordinates = (x, y+1)
                next_fall_time = time.time() + fall_delay()
                if place_block(block, new_coordinates, blue):  # can be placed?
                    coordinates = new_coordinates
                else:
                    place_block(block, coordinates,
                                black)  # place block there again
                    break               # and bail out
        remove_full_lines()

class Timeout(Exception):  pass
class    Fall(Exception):  pass

def remove_full_lines():
    global shaft, width, height
    def line_full(line):
        global width
        for x in range(width):
            if line[x] == empty:
                return False
        return True

    def remove_line(y):
        global shaft, width
        del shaft[y]  # cut out line
        shaft.insert(5, [ empty ] * width)  # fill up with an empty line

    for y in range(height):
        if line_full(shaft[y]):
            remove_line(y)

def fall_delay():
    return 1.3  # cheap version; implement raising difficulty here

def turn_block(block):
    "return a turned copy(!) of the given block"
    result = []
    for x, y in block:
        result.append((y, -x))
    return result

def get_command(next_fall_time):
    "if a command is entered, return it; otherwise raise the exception Timeout"
    while True:  # until a timeout occurs or a command is found:
        timeout = next_fall_time - time.time()
        if timeout > 0.0:
            (r, w, e) = select.select([ sys.stdin ], [], [], timeout)
        else:
            raise Timeout()
        if sys.stdin not in r:  # not input on stdin?
            raise Timeout()
        key = os.read(sys.stdin.fileno(), 1)
        if  key.decode("utf-8") == 'j':
            return left
        elif key.decode("utf-8") == 'l':
            return right
        elif key.decode("utf-8") == 'k':
            return turn
        elif key.decode("utf-8") == ' ':
            return down
        elif key.decode("utf-8") == 'q':
            print("Come again!")
            return quit
        else:  # any other key:  ignore
            pass

def place_block(block, coordinates, color):
    "if the given block can be placed in the shaft at the given coordinates"\
    " then place it there and return True; return False otherwise and do not"\
    " place anything"
    global shaft, width, height
    block_x, block_y = coordinates
    for stone_x, stone_y in block:
        x = block_x + stone_x
        y = block_y + stone_y
        if (x < 0 or x >= width or
            y < 0 or y >= height or  # border collision?
            shaft[y][x] != empty):   # block collision?
            return False  # cannot be placed there
    # reached here?  ==> can be placed there
    # now really place it:
    for stone_x, stone_y in block:
        x = block_x + stone_x
        y = block_y + stone_y
        shaft[y][x] = color
    return True

def get_next(prev_block):
    for x, y in prev_block:
        shaft[y+2][x+2] = empty
    block = get_random_block()
    for x, y in block:
        shaft[y+2][x+2] = blue
    return block

def remove_block(block, coordinates):
    global shaft
    block_x, block_y = coordinates
    for stone_x, stone_y in block:
        x = block_x + stone_x
        y = block_y + stone_y
        shaft[y][x] = empty

def get_random_block():
    # if random.randint(1, 10) == 1:
    #     return random.choice(blocks)
    return random.choice(blocks)

def initialize_shaft():
    global width, height, shaft, empty
    shaft = [ None ] * height
    for y in range(height):
        shaft[y] = [ empty ] * width

def print_shaft():
    # cursor-goto top left corner:
    sys.stdout.write(home)
    for y in range(height):
        if y == 0:
            sys.stdout.write('Next Block:')
        if y > 7:  # does this line have a border?  (the topmost ones do not)
            sys.stdout.write('|')
        else:
            sys.stdout.write(' ')
        for x in range(width):
            sys.stdout.write(shaft[y][x])
        if y > 7:  # does this line have a border?  (the topmost ones do not)
            sys.stdout.write('|\n')
        else:
            sys.stdout.write('\n')

    # print bottom:
    sys.stdout.write('|' + floor * width + '|\n')

def prepare_tty():
    "set the terminal in char mode (return each keyboard press at once) and"\
    " switch off echoing of this input; return the original settings"
    stdin_fd = sys.stdin.fileno()  # will most likely be 0  ;->
    old_stdin_config = termios.tcgetattr(stdin_fd)
    [ iflag, oflag, cflag, lflag, ispeed, ospeed, cc ] = \
        termios.tcgetattr(stdin_fd)
    cc[termios.VTIME] = 1
    cc[termios.VMIN] = 1
    iflag = iflag & ~(termios.IGNBRK |
                      termios.BRKINT |
                      termios.PARMRK |
                      termios.ISTRIP |
                      termios.INLCR |
                      termios.IGNCR |
                      #termios.ICRNL |
                      termios.IXON)
    #  oflag = oflag & ~termios.OPOST
    cflag = cflag | termios.CS8
    lflag = lflag & ~(termios.ECHO |
                      termios.ECHONL |
                      termios.ICANON |
                      # termios.ISIG |
                      termios.IEXTEN)
    termios.tcsetattr(stdin_fd, termios.TCSANOW,
                      [ iflag, oflag, cflag, lflag, ispeed, ospeed, cc ])
    return (stdin_fd, old_stdin_config)

def cleanup_tty(original_tty_settings):
    "restore the original terminal settings"
    stdin_fd, old_stdin_config = original_tty_settings
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_stdin_config)

def joinGame():
    global playerStatus
    global menuGo
    joinwait = True
    playerStatus = 'join'
    hostname = input("What is the hostname / ip address of the other player?\n")
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Trying to connect to ' + hostname + '...\n')
    URL = "http://" + hostname #get hostname for centralized server
    timeout = time.time() + 15
    while joinwait:
        joinwait = False
        if timeout < time.time():
            print('Couldn''t find a host player, please try again later \n')
            joinwait = False
            timeout = -1
    if timeout != -1:
        menuGo = False
        original_tty_settings = prepare_tty()  # switch off line buffering etc.
        os.system('cls' if os.name == 'nt' else 'clear')
        try:# ensure that tty will be reset in the end
            play_tetris()
        finally:
            cleanup_tty(original_tty_settings)
def hostGame():
    global menuGo
    hostwait = True
    playerStatus = 'host'
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Hosting a game, waiting for a player to join...\n')
    host_server = tetris_server.serverRun()
    srv = threading.Thread(target=host_server.run, daemon = True)
    srv.start()
    timeout = time.time() + 15
    while hostwait:
        hostwait = False
        if timeout < time.time():
            print('No other players connected, please try again later\n')
            hostwait = False
            timeout = -1
    if timeout != -1:
        menuGo = False
        original_tty_settings = prepare_tty()  # switch off line buffering etc.
        os.system('cls' if os.name == 'nt' else 'clear')
        try:# ensure that tty will be reset in the end
            play_tetris()
        finally:
            cleanup_tty(original_tty_settings)
def menu():
    global menuGo
    #print the logo
    print(RED + "MMMMMM" + WHITE + " MMMMMM" + YELLOW + "  MMMMMM" + GREEN + " MMMML" + BLUE + "  MMMMM" + PURPLE + " MMMMMM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M   M" + BLUE + "    M" + PURPLE + "   MM")
    print(RED + "  MM" + WHITE + "   MMMM" + YELLOW + "      MM" + GREEN + "   MMMMP" + BLUE + "    M" + PURPLE + "   MMMMMM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M  M" + BLUE + "     M" + PURPLE + "       MM")
    print(RED + "  MM" + WHITE + "   MM" + YELLOW + "        MM" + GREEN + "   M   M" + BLUE + "    M" + PURPLE + "       MM")
    print(RED + "  MM" + WHITE + "   MMMMMM" + YELLOW + "    MM" + GREEN + "   M    M" + BLUE + " MMMMM" + PURPLE + " MMMMMM\n" + WHITE)
    print("Welcome!\n\nTo start a game you'll need another player.")
    while menuGo == True:
        text = input("Would you like to host or join a game (Type 'host' for host, 'join' for join, and 'quit' for quit)\n")
        if  text.lower() == 'join':
            joinGame()
        elif text.lower() == 'host':
            hostGame()
        elif text.lower() == 'quit':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Goodbye!")
            menuGo = False
        else:
            print(text + " is not a valid option, please type either 'host' or 'join'\n")

os.system('cls' if os.name == 'nt' else 'clear')
menu()
