from cmu_graphics import *
import random

################################################################################
#############################    Button Class    ###############################
################################################################################

class Button():
    def __init__(self, message, midX, midY):
        self.message = message
        self.midX = midX
        self.midY = midY
        self.width = 200
        self.height = 50
        self.colour = 'blue' # default
        self.textColour = 'white'
    
    def drawButton(self):
        drawRect(self.midX, self.midY, self.width, self.height, 
                 align = 'center', fill = self.colour)
        drawLabel(self.message, self.midX, self.midY, 
                  fill = self.textColour, size = 16)
    
    def inButton(self, app):
        return inRect(app.mousePosX, app.mousePosY, self.midX - self.width // 2, 
                      self.midY - self.height // 2, self.width, self.height)
    
    def hover(self, app):
        if self.inButton(app):
            self.colour = 'purple'
        else:
            self.colour = 'blue'

################################################################################
############################    Initialization    ##############################
################################################################################

def onAppStart(app):
    # general app information
    app.width = 700
    app.height = 700
    app.mousePosX = 0
    app.mousePosY = 0
    # board information
    app.rows = 15
    app.cols = 15
    app.boardLeft = 25
    app.boardTop = 25
    app.boardWidth = 645
    app.boardHeight = 645
    app.boardColour = None
    app.borderWidth = 1
    app.cellWidth = app.boardWidth // app.cols
    app.cellHeight = app.boardHeight // app.rows
    # game information
    app.mode = 'MEDIUM'
    app.state = 'MENU'
    app.startButton = Button('START', app.width // 2, 3 * app.height // 4)
    # restart
    restart(app)

def restart(app):
    app.reveal = False
    app.board = [[[0, 0, 0] for i in range(app.cols)] for j in range(app.rows)]
    app.mines = 40
    app.flags = 40
    resetDir(app)

################################################################################
############################    General Helpers    #############################
################################################################################

def inRect(pX, pY, x, y, width, height):
    if (x <= pX <= x + width) and (y <= pY <= y + height):
        return True
    return False

def pixelToRowCol(app, pX, pY):
    row = (pY - app.boardTop) // app.cellHeight
    col = (pX - app.boardLeft) // app.cellWidth
    return row, col

def resetDir(app):
    app.dir = [( -1, 1), ( 0, 1), ( 1, 1),
               ( -1, 0),          ( 1, 0),
               (-1, -1), (0, -1), (1, -1)]

################################################################################
#############################    Game Mechanics    #############################
################################################################################

def placeMines(app, row, col):
    for mine in range(app.mines):
        mineRow = random.randint(0, app.rows - 1)
        mineCol = random.randint(0, app.cols - 1)
        while ((row - 1) <= mineRow <= (row + 1) or (col - 1) <= mineCol <= (col + 1)
               or app.board[mineRow][mineCol][1] == 1):
            mineRow = random.randint(0, app.rows - 1)
            mineCol = random.randint(0, app.cols - 1)
        app.board[mineRow][mineCol][1] = 1

def revealAll(app, row, col):
    for drow, dcol in app.dir:
        app.board[row + drow][col + dcol][0] = 1

def revealInitialArea(app, startRow, startCol, dir):
    if dir == []:
        return None
    drow, dcol = dir[0]
    newRow, newCol = startRow + drow, startCol + dcol
    # problem: check grid limits to prevent indexing errors
    if app.board[newRow][newCol][0] == 0 and app.board[newRow][newCol][2] == 0:
        revealAll(app, startRow, startCol)
        return revealInitialArea(app, newRow, newCol, app.dir)
    return revealInitialArea(app, startRow, startCol, dir[1:])
    # problem: doesn't check below once a top end is reached. still have to check all
    # directions instead of ending as soon as an end is reached

def firstClick(app, mouseX, mouseY):
    clickedRow, clickedCol = pixelToRowCol(app, mouseX, mouseY)
    for mine in range(app.mines):
        mineRow = random.randint(0, app.rows - 1)
        mineCol = random.randint(0, app.cols - 1)
        while (((clickedRow - 1) <= mineRow <= (clickedRow + 1) and (clickedCol - 1) <= 
               mineCol <= (clickedCol + 1)) or app.board[mineRow][mineCol][1] == 1):
            mineRow = random.randint(0, app.rows - 1)
            mineCol = random.randint(0, app.cols - 1)
        app.board[mineRow][mineCol][1] = 1
    for row in range(app.rows):
        for col in range(app.cols):
            app.board[row][col][2] = calculateCell(app, row, col, app.dir)
    revealInitialArea(app, clickedRow, clickedCol, app.dir)

def calculateCell(app, row, col, dir):
    # base case
    if dir == []:
        return 0
    drow, dcol = dir[0]
    newRow, newCol = row + drow, col + dcol
    # recursive case 1: newRow, newCol out of bounds, move on
    if newRow < 0 or newRow >= app.rows or newCol < 0 or newCol >= app.cols:
        return calculateCell(app, row, col, dir[1:])
    # recursive case 2: mine in neighbouring cell in direction drow, dcol
    if app.board[newRow][newCol][1] == 1:
        return calculateCell(app, row, col, dir[1:]) + 1
    # recursive case 3: no mine in neighbouring cell in direction drow, dcol
    return calculateCell(app, row, col, dir[1:])

################################################################################
##################################    Draw    ##################################
################################################################################

def drawMenu(app):
    drawLabel('MINESWEEPER', app.width // 2, app.height // 4, size = 50, fill = 'blue')
    app.startButton.drawButton()
    app.startButton.hover(app)

def drawBoard(app):
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, 
             fill = None, border = 'blue', borderWidth = app.borderWidth)
    for row in range(app.rows):
        for col in range(app.cols):
            cellLeft = app.boardLeft + app.cellWidth * col
            cellTop = app.boardTop + app.cellHeight * row
            middleX = cellLeft + app.cellWidth // 2
            middleY = cellTop + app.cellHeight // 2
            if (app.board[row][col][0] == 0):
                if col % 2 == row % 2:
                    drawRect(cellLeft, cellTop, app.cellWidth, app.cellHeight, 
                            fill = rgb(190, 230, 150)) # temp colours
                else:
                    drawRect(cellLeft, cellTop, app.cellWidth, app.cellHeight, 
                            fill = rgb(170, 210, 130)) # temp colours
            else:
                if col % 2 == row % 2:
                    drawRect(cellLeft, cellTop, app.cellWidth, app.cellHeight, 
                            fill = rgb(200, 200, 200)) # temp colours
                else:
                    drawRect(cellLeft, cellTop, app.cellWidth, app.cellHeight, 
                            fill = rgb(180, 180, 180)) # temp colours
                if not app.board[row][col][2] == 0:
                    drawLabel(app.board[row][col][2], middleX, middleY, size = 20, fill = 'red')
            # debug
            if app.reveal:
                if app.board[row][col][1] == 1:
                    drawCircle(middleX, middleY, app.cellWidth // 4, fill = 'red')
                else:
                    if not app.board[row][col][2] == 0:
                        drawLabel(app.board[row][col][2], middleX, middleY, size = 20, fill = 'red')

def drawGameOver(app):
    pass

################################################################################
###########################    User Interactions    ############################
################################################################################

def onMousePress(app, mouseX, mouseY):
    if app.state == 'MENU':
        if app.startButton.inButton(app):
            app.state = 'START'
    elif app.state == 'START':
        firstClick(app, mouseX, mouseY)
        app.state = 'GAME'
    elif app.state == 'GAME':
        cellRow, cellCol = pixelToRowCol(app, mouseX, mouseY)
        if app.board[cellRow][cellCol][1] == 1:
            app.state = 'FAIL'
        else:
            app.board[cellRow][cellCol][0] = 1


def onMouseMove(app, mouseX, mouseY):
    app.mousePosX, app.mousePosY = mouseX, mouseY

def onKeyPress(app, key):
    # debug
    if key == 'r':
        app.reveal = not app.reveal

################################################################################
######################   Tippity Toppest Top Level   ###########################
################################################################################

def redrawAll(app):
    if app.state == 'MENU':
        drawMenu(app)
    elif app.state == 'START':
        drawBoard(app)
    elif app.state == 'GAME':
        drawBoard(app)
    elif app.state == 'FAIL' or app.state == 'WIN':
        drawGameOver(app)

def main():
    runApp()

main()