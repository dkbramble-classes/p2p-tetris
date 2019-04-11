# CIS 457 Project 3: 1-v-1 Tetris
These programs are a Tetris game and a server that allows two players to connect and play against each other. They are primarily designed for Mac OS using pyftpdlib, requests, pygame, and python 3.7. Python 3 is required to run these programs. If you do not have it, you can download it at https://www.python.org/downloads/. The pyftpdlib, pygame, and requests modules will also have to be installed via pip in order to run.

-	The first part is Tetris game. It allows you to host or join a game and to search for other players to play against. Once connected it is a fully functional game of Tetris.

-	The second part of the system is the centralized server which allows for the connection of the two players and passes status information back and forth between them.

## How to Run:
First, download all of the files from this Github to ensure you have all of the necessary files, and install all of the necessary modules. Preferably, this processes is done on at least two devices: One device for the centralized server and the host, and another device for the other player.

### Host (TetrisGrid.py + tetris_server.py):
If you are hosting the Tetris game, then you need to make sure you have the centralized server running on your machine. To start, open a window in Terminal and run the command "python3 (or python if python 3 is natively installed) path/to/repository/p2p-tetris/tetris_server.py". Once that is ran, no other action is needed.

Once the server is running, the game can be started by opening another window in Terminal and run the command "python3 (or python if python 3 is natively installed) path/to/repository/p2p-tetris/TetrisGrid.py". Once it has started, type 'host' to begin searching for another player. If the other player connects, the game will start.

### Joining Player (TetrisGrid.py):

To start, open another window in Terminal and run the command "python3 (or python if python 3 is natively installed) path/to/repository/p2p-tetris/TetrisGrid.py". Once it has started, type 'join' to begin searching for the host machine. If you connect to the host, the game will start.

## Tetris Rules / Controls:

### Rules:
This is the typical game of Tetris: Stack the blocks as best as possible, you lose when your board is filled before your opponents. The goal of this game is to stay alive the longest, so do your best!

### Controls:
Left/Right: Left and right arrow keys
Fast Fall: Down arrow key
Rotate Block: Up arrow key
