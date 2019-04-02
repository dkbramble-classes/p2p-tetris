class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    BLACK = '\u001b[30;1m'

    def disable(self):
        self.PURPLE = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.WHITE = ''
        self.RED = ''

def printBoard(board):
    count = 0
    for i in board:
        for j in i:
            count = (count + 1) % 10
            if j == 0:
                print(bcolors.BLACK, end=' ')
                print(" ", end='', flush = True)
            else:
                if j == 1:
                    print(bcolors.RED, end=' ')
                elif j == 2:
                    print(bcolors.BLUE, end=' ')
                elif j == 3:
                    print(bcolors.GREEN, end=' ')
                elif j == 4:
                    print(bcolors.PURPLE, end=' ')
                print('*', end='', flush = True)
            if count == 0:
                print('')
    print(bcolors.WHITE, end='')


#tetris boards are typically 10 X 20
board = [[0,1,3,1,1,4,1,0,1,0],[1,0,0,4,1,0,1,0,1,3],[1,2,0,2,1,0,1,3,1,0],[1,0,2,0,1,3,1,0,1,0],[1,0,0,3,1,0,1,0,1,0],[1,4,0,0,1,0,1,0,1,0],[1,0,0,3,1,0,1,0,1,0],[1,0,0,2,1,0,1,0,1,0],[1,0,0,3,1,0,1,0,1,0],[1,0,4,2,1,0,1,0,1,0],[1,0,0,0,1,0,1,4,1,0],[1,4,0,2,1,0,1,3,1,0],[1,0,0,0,1,0,1,0,1,0],[1,0,4,0,1,3,1,0,1,0],[1,0,2,2,1,2,1,0,1,0],[1,0,0,0,1,0,1,0,1,0],[1,0,0,0,1,0,1,0,1,0],[1,0,0,0,1,0,1,0,1,0]]
printBoard(board)
