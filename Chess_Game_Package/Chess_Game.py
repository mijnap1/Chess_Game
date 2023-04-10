#******************************************************************************************************
# Final Version of Chess Game | By Jamie Ryu
import pygame as pg
import os
from tkinter import * # call tkinter
from tkinter import messagebox 
import time

#******************************************************************************************************
# Timer for both players



# Classes created for game mechanics. 

class BoardState(): # Called as bs in def main.
    
    'Class to keep track of where the pieces are and other info about current board state'
    
    def __init__(self):
        
        'Initializes board and pertinant info about the state of the game based on where pieces are placed'
        
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],    # 2D-List representation of board that updates with each move and is drawn on screen at 60fps.
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    ]
        self.white_turn = True # initialized white to move first.
        
        self.log = [] # Keeps track of every move made, used for undoing moves.
        
        # King location markers.
        self.whiteKing = (7, 4) # Position on board row, col
        self.blackKing = (0, 4)
        
        self.checkMate = False # Initializes checkmate as false, changes when criteria is met.
        self.staleMate = False # Initializes stalemate/draw as false, changes when criteria is met.
        
        self.posEnpassant = () # Square of possible en passant capture, keeps track for adding to moves list.
        
        self.validCastlingRights = CastlingRights(True, True, True, True)  # initializes Castling rights.
        
        self.CastlingRights_log = [CastlingRights(self.validCastlingRights.wkscr, self.validCastlingRights.bkscr,  # Keeps track of castling rights for every move made.
                                                  self.validCastlingRights.wqscr, self.validCastlingRights.bqscr)]

    def makeMove(self, move):
        'Makes moves'
            
        self.board[move.startRow][move.startCol] = "--" # Replace moved piece with empty square
        self.board[move.endRow][move.endCol] = move.moved # Replace empty square with piece moved.
        self.log.append(move) # Adds move to log.
        self.white_turn = not self.white_turn # Switch turns. 
            
        # Updates king location markers. 
        if move.moved == 'wK':
                
            self.whiteKing = (move.endRow, move.endCol)
                
        elif move.moved == 'bK':
                
            self.blackKing = (move.endRow, move.endCol)          
            
        if move.pawnPromotion:
                
            self.board[move.endRow][move.endCol] = move.moved[0] + 'Q' # If a pawn reaches either end of the board it becomes a queen.
            
        if move.isEnpassant:
            
            self.board[move.startRow][move.endCol] = '--' # When enpassant capture is made, pawn captured replace with empty square.
            
        # Update enpassant.
        if move.moved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.posEnpassant = ((move.startRow + move.endRow)//2, move.startCol) # Stores square behind pawn that moved +2 as pos enpassant capture square.
        else:
            self.posEnpassant = () # resets value if not +2 pawn advance.
        
        # Castling Move
        
        if move.isCastling:
            if move.endCol - move.startCol == 2: # Moves king side rooks when a Castling move is made.
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
                
            else: # Moves queen side rooks when a Castling move is made.
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'
                                        
        # Updates Castling Rights after every move.
        self.updateCastlingRights(move)
        self.CastlingRights_log.append(CastlingRights(self.validCastlingRights.wkscr, self.validCastlingRights.bkscr,
                                                      self.validCastlingRights.wqscr, self.validCastlingRights.bqscr)) 
    
    def undoMove(self):
        
        'Undoes last move made when backspace key is pressed'
        
        if len(self.log) != 0: # Makes sure there is a move to undo.
            
            move = self.log.pop() # Removes move from list and stores move
            self.board[move.startRow][move.startCol] = move.moved # replace moved piece.
            self.board[move.endRow][move.endCol] = move.captured # replaces captures piece (or empty square)
            self.white_turn = not self.white_turn # swtiches back turn.           
            
     
            # Returns king location markers to previous location. 
            if move.moved == 'wK':
                
                self.whiteKing = (move.startRow, move.startCol)            
                
            elif move.moved == 'bK':
                
                self.blackKing = (move.startRow, move.startCol) 
            
            # undo 2 square pawn advance effect on posEnpassant.
            if move.moved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                   
                self.posEnpassant = () # resets pos enpassant square tuple to empty. 
                    
            # Undo En passant move.
            if move.isEnpassant:
                
                self.board[move.endRow][move.endCol] = '--' # replaces blank square
                self.board[move.startRow][move.endCol] = move.captured # replaces captured pawn
                self.posEnpassant = (move.endRow, move.endCol) # resets pos enpassant tuple to square behind replaced pawn.
                
            # Undo Castling Rights
            self.CastlingRights_log.pop() # removes valid castle rights from log.
            popedRights = self.CastlingRights_log[-1] # Stores last rights.
            self.validCastlingRights = CastlingRights(popedRights.wkscr, popedRights.bkscr,  # Sets valid castle rights to last rights.
                                                      popedRights.wqscr, popedRights.bqscr)
            
            # Undo Castling Move (king is handled by regular undo, rooks use this)
            if move.isCastling:
                if move.endCol - move.startCol == 2: # Moves king side rooks back.
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] # Returns rook to first position.
                    self.board[move.endRow][move.endCol-1] = '--' # Replaces captured square with empty square.
                else: # Moves queenside rooks back.
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] # Returns rook to first position.
                    self.board[move.endRow][move.endCol+1] = '--' # Replaces captured square with empty square.
                    
            
            
                        
    def updateCastlingRights(self, move):
        
        'Helper function to update castle rights when specific moves are made'
        
        if move.moved == 'wK': # If the white king is moved
            self.validCastlingRights.wkscr = False
            self.validCastlingRights.wqscr = False
            
        elif move.moved == 'bK': # If the black king is moved
            self.validCastlingRights.bkscr = False
            self.validCastlingRights.bqscr = False
            
        elif move.moved == 'wR': # If a white rook is moved
            if move.startRow == 7:
                if move.startCol == 0: # Queen side rook.
                    self.validCastlingRights.wqscr = False
                elif move.startCol == 7: # King side rook.
                    self.validCastlingRights.wkscr = False
                    
        elif move.moved == 'bR': # If a black rook is moved
            if move.startRow == 0:
                if move.startCol == 0: # Queen side rook.
                    self.validCastlingRights.bqscr = False
                elif move.startCol == 7: # King side rook.
                    self.validCastlingRights.bkscr = False
                    
        if move.captured == 'wR': # If a white rook is captured
            if move.endRow == 7:
                if move.endCol == 0:  # Queen side rook.
                    self.validCastlingRights.wqscr = False
                elif move.endCol == 7: # King side rook.
                    self.validCastlingRights.wkscr = False
                    
        elif move.captured == 'bR': # If a black rook is captured
            if move.endRow == 0:
                if move.endCol == 0:  # Queen side rook.
                    self.validCastlingRights.bqscr = False
                elif move.endCol == 7: # King side rook.
                    self.validCastlingRights.bkscr = False        

        
    def validMoves(self): 
        
        'Creates list of legal moves of peices for current turn'
        
        tempEP = self.posEnpassant # stores copy of pos enpassant square
        tempCR = CastlingRights(self.validCastlingRights.wkscr, self.validCastlingRights.bkscr, # stores copy of castle rights.
                                self.validCastlingRights.wqscr, self.validCastlingRights.bqscr)
        
        moves = self.allMoves() # makes a list of all possible moves.
        
        if self.white_turn:
            self.CastlingMoves(self.whiteKing[0], self.whiteKing[1], moves) # Adds castling moves for white king.
            
        else:
            self.CastlingMoves(self.blackKing[0], self.blackKing[1], moves) # Adds castling moves for black king.
         
        
        for i in range(len(moves)-1, -1, -1): # iterates backward in list.
            
            self.makeMove(moves[i]) # Makes all possible moves for player's turn. Swaps turn.
            
            self.white_turn = not self.white_turn # Switches turn back again so that correct king is checked for check.
            
            if self.inCheck(): # calls inCheck to see if move will make the player's king in check.
                
                moves.remove(moves[i]) # Removes all moves that will put player in check.             
                
            self.white_turn = not self.white_turn # Swaps back turn. 
            
            self.undoMove() # undoes all moves made in this process, also cancels out turn for every move made in process.
        
        if len(moves) == 0: # If there are no legal moves that can be made.
            
            if self.inCheck():
                self.checkMate = True  # Checkmate if in check.
            else:
                self.staleMate = True # Stalemate if not.
        else:
            self.checkMate = False
            self.staleMate = False
        
        counter = 0 # Counter for number of peices on board.
        
        bnCount = False #shows whether the last piece remaining, aside from the kings, is just bishop or a knight, either case will result in a stalemate
        
        for row in self.board:
            for square in row:
                if square != '--':
                    counter = counter + 1
        
        if counter <= 4:  # If total pieces on board is 4 or less and only kings and bishops or kings and knights, bncount is true.
            for row in self.board:
                for square in row:
                    if (square == 'bB' or square == 'wB') or (square == 'wN' or square == 'bN'):
                        bnCount = True
                        
        if counter == 2: # if only kings left on board triggers stalemate.
            self.staleMate = True
        
        if bnCount == True: # If insuficient material is detected triggers stalemate.
            self.staleMate = True               
            
       
        self.posEnpassant = tempEP # resets pos enpassant from copy.
        self.validCastlingRights = tempCR # resets castle rights from copy. 
        
        return moves # returns updated list of all legal moves. 
    
    def allMoves(self):
        
        'Creates list of moves without checks taken into account'
        
        moves = [] # Creates list for moves.
        
        for row in range(len(self.board)): # For every row.
            
            for col in range(len(self.board[row])): # for every column.
                
                turn = self.board[row][col][0] # turn is equal to w or b depending on piece name first letter on square.
                piece = self.board[row][col][1] # Piece type is determained by second letter in name.
                
                if (turn == 'w' and self.white_turn) or (turn == 'b' and not self.white_turn): # For white and black, moves for each color.
                    
                    if piece == 'P':
                        self.pawnMoves(row, col, moves) # Adds pawn moves.
                    if piece == 'R':
                        self.rookMoves(row, col, moves) # Adds rook moves.
                    if piece == 'N':
                        self.knightMoves(row, col, moves) # Adds knight moves.
                    if piece == 'B':
                        self.bishopMoves(row, col, moves) # Adds bishop moves.
                    if piece == 'K':
                        self.kingMoves(row, col, moves) # Adds king moves.
                    if piece == 'Q':
                        self.queenMoves(row, col, moves) # Adds queen moves.
                        
        return moves # Returns list of all moves that can be made.

    def inCheck(self):
        
        'Returns true for all squares where king would be in check'
        
        if self.white_turn:
            
            return self.squareAttacked(self.whiteKing[0], self.whiteKing[1])
        
        else:
            
            return self.squareAttacked(self.blackKing[0], self.blackKing[1])    
    
    def squareAttacked(self, row, col):
        
        'Helper function that checks if  certain square is attacked'
        
        self.white_turn = not self.white_turn # Temp switch turns.
        enemyMoves = self.allMoves() # Generates all possible enemy moves. 
        self.white_turn = not self.white_turn # Return turn order.
       
        for move in enemyMoves:
            
            if move.endRow == row and move.endCol == col: # If square of king, or possible move square, is attacked returns true. 
                return True
            
        return False # Else returns false.
        
    
    def pawnMoves(self, row, col, moves):
        
        'Pawn moves'
        
        if self.white_turn: # White pawn moves.
            
            if self.board[row-1][col] == '--': # 1 square advance.
                
                moves.append(Move((row, col), (row-1,col), self.board)) # Adds moves to moves list.
                
                if row == 6 and self.board[row-2][col] == "--": # 2 square advance. 
                    
                    moves.append(Move((row, col), (row-2,col), self.board)) # Adds moves to moves list.
                    
            if col - 1 >= 0: # Attack to the left of the board from whites perspective.
                
                if self.board[row-1][col-1][0] == 'b':
                    
                    moves.append(Move((row, col), (row-1,col-1), self.board)) # Adds moves to moves list.
                
                elif (row-1, col-1) == self.posEnpassant:
                    
                    moves.append(Move((row, col), (row-1,col-1), self.board, isEnpassant=True)) # Adds moves to moves list, sets isEnpassant to true. 
                    
            if col + 1 <= 7: # Attack to the right of the board from whites perspective.
                
                if self.board[row-1][col+1][0] == 'b':
                    
                    moves.append(Move((row, col), (row-1,col+1), self.board)) # Adds moves to moves list.
                    
                elif (row-1, col +1) == self.posEnpassant:
                    
                    moves.append(Move((row, col), (row-1,col+1), self.board, isEnpassant=True))  # Adds moves to moves list, sets isEnpassant to true.             
                    
        else: # Black pawn moves.
            
            if self.board[row+1][col] == '--': # 1 square advance.
                
                moves.append(Move((row, col), (row+1,col), self.board))
                
                if row == 1 and self.board[row+2][col] == "--": # 2 square advance. 
                    
                    moves.append(Move((row, col), (row+2,col), self.board)) # Adds moves to moves list.
                    
            if col - 1 >= 0: # Attack to the left of the board from whites perspective.
                
                if self.board[row+1][col-1][0] == 'w':
                    
                    moves.append(Move((row, col), (row+1,col-1), self.board)) # Adds moves to moves list.
                
                elif (row+1, col -1) == self.posEnpassant:
                    
                    moves.append(Move((row, col), (row+1,col-1), self.board, isEnpassant=True))  # Adds moves to moves list, sets isEnpassant to true.              
                    
            if col + 1 <= 7: # Attack to the right of the board from whites perspective.
                
                if self.board[row+1][col+1][0] == 'w':
                    
                    moves.append(Move((row, col), (row+1,col+1), self.board))  # Adds moves to moves list.
                
                elif (row+1, col +1) == self.posEnpassant:
                    
                    moves.append(Move((row, col), (row+1,col+1), self.board, isEnpassant=True))  # Adds moves to moves list, sets isEnpassant to true.                 
            
         
                    
    def rookMoves(self, row, col, moves):
        
        'Rook moves'
        
        direction = ((-1,0), (0,-1), (1,0), (0,1)) # Directions in row, col notation.
        enemy = 'b' if self.white_turn else 'w' # sets enemy color.
        friend = 'w' if self.white_turn else 'b' # sets friend color.
        
        for d in direction: #Iterate over direction.
            
            for i in range(1,8): # For a possible of 1-8 square advance.
                
                endRow = row + d[0] * i 
                endCol = col + d[1] * i
                
                if 0 <= endRow < 8 and 0 <= endCol < 8: # Only checks squares on board. 
                    
                    endPiece = self.board[endRow][endCol]
                    
                    if endPiece[0] == friend: # If end is friend color stop adding squares to moves list.
                        break
                    
                    elif endPiece == '--': # If empty add sqaure to move list.
                        
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        
                    elif endPiece[0] == enemy: # if empty add enemy square to list and stop checking further squares.
                        
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    
                else:
                    break
            
    def knightMoves(self, row, col, moves):
        
        'Knight moves'
        
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # Directions in row, col notation.
        friend = 'w' if self.white_turn else 'b' # sets friend color.
        
        for km in knight_moves: # Iterates over possible moves.
            
            endRow = row + km[0]
            endCol = col + km[1]
            
            if 0 <= endRow < 8 and 0 <= endCol < 8: # Only check squares on board.
                
                endPiece = self.board[endRow][endCol]
                
                if endPiece[0] != friend: # If square to move to is not a friendly color (meaning other color or empty), add to moves list.
                    
                    moves.append(Move((row, col), (endRow, endCol), self.board))
    
    def bishopMoves(self, row, col, moves):
        
        'Bishop moves'
        
        direction = ((-1,-1), (-1,1), (1,-1), (1,1)) # Directions in row, col notation.
        enemy = 'b' if self.white_turn else 'w' # sets enemy color.
        friend = 'w' if self.white_turn else 'b' # sets friend color.
        
        for d in direction: #Iterate over direction.
            
            for i in range(1,8): # For a possible of 1-8 square advance.
                
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                
                if 0 <= endRow < 8 and 0 <= endCol < 8: # Only checks squares on board. 
               
                    endPiece = self.board[endRow][endCol]
                    
                    if endPiece[0] == friend: # If end is friend color stop adding squares to moves list.
                        break
                    
                    elif endPiece == '--': # If empty add sqaure to move list.
                        
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        
                    elif endPiece[0] == enemy:  # if empty add enemy square to list and stop checking further squares.
                        
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    
                else:
                    break        
        
    def kingMoves(self, row, col, moves):
        
        'King moves'
        
        direction = ((-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (0,-1), (1,0), (0,1)) # Directions in row, col notation.
        friend = 'w' if self.white_turn else 'b'   
        
        for d in direction: # Iterates over possible moves.
            
            endRow = row + d[0]
            endCol = col + d[1]
            
            if 0 <= endRow < 8 and 0 <= endCol < 8: # Only check squares on board.
              
                endPiece = self.board[endRow][endCol]
                
                if endPiece[0] != friend:  # If square to move to is not a friendly color (meaning other color or empty), add to moves list.
                    
                    moves.append(Move((row, col), (endRow, endCol), self.board))
                    
            
    def CastlingMoves(self, row, col, moves):
        
        'Castling Moves (king only, rook is handled specially whenever castle move is made'
        
        if self.squareAttacked(row, col): # If square is attacked no castling can be done.
            return
        
        if (self.white_turn and self.validCastlingRights.wkscr) or (not self.white_turn and self.validCastlingRights.bkscr): # If correct turn and castle rights are valid.
            if self.board[row][col+1] == '--' and self.board[row][col+2] == '--': # If in between sqaures are empty.
                if not self.squareAttacked(row, col+1) and not self.squareAttacked(row, col+2): # If inbetween sqaures are not attacked.
                    moves.append(Move((row, col), (row, col+2), self.board, isCastling=True))     # Moves the king to the kingside.           
            
        if (self.white_turn and self.validCastlingRights.wqscr) or (not self.white_turn and self.validCastlingRights.bqscr): # If correct turn and castle rights are valid.
            if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--': # If in between sqaures are empty.
                if not self.squareAttacked(row, col-1) and not self.squareAttacked(row, col-2): # If inbetween sqaures are not attacked.
                    moves.append(Move((row, col), (row, col-2), self.board, isCastling=True))     # Moves the king to the queenside.                       
        
    def queenMoves(self, row, col, moves):
        'Queen moves'
        
        # Combination of rook and bishop moves
        self.rookMoves(row, col, moves)
        self.bishopMoves(row, col, moves)
    
class Move():
    
    'Class to keep track of move elements'
    
    def __init__(self, start, end, board, isEnpassant=False, isCastling=False): # Initializes a move with two optional variables.
        
        # Actual mechanics of def makeMove in class GameState.
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.moved = board[self.startRow][self.startCol]
        self.captured = board[self.endRow][self.endCol]
        
        # Pawn promotion.
        self.pawnPromotion = False # Initializes as false, changes when criteria is met.
        
        if (self.moved == 'wP' and self.endRow == 0) or (self.moved == 'bP' and self.endRow == 7): # Criteria for pawn promotion.
            
            self.pawnPromotion = True # Returns true once Criteria is met.
        
        # En passant.
        
        self.isEnpassant = isEnpassant # Initializes move as enpassant move to be false.
        
        if self.isEnpassant: # Tells the computer what color captured pawn is for an en passant capture.
            if self.moved == 'bP':
                self.captured = 'wP'
            if self.moved == 'wP':
                self.captured = 'bP'
                
        # Castling Move
        self.isCastling = isCastling # Initializes move as castling move to be false.
        
        # Move ID
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # Unique move ID 0000 - 7.777, used to make moves unique from each other.
        
    def __eq__(self, other): # Compares an object to other object.
        
        if isinstance(other, Move): # Checks if object is an instance of the Move class.
            
            return self.moveID == other.moveID # Makes move equal to other.
        
        return False
    
class CastlingRights():
    'Class that keeps track of the four different castling rights'
    
    def __init__(self, wkscr, bkscr, wqscr, bqscr):
        'Initializes castling rights to be set either to True or False, updated when certain moves are made'
        self.wkscr = wkscr # white king side castling rights
        self.bkscr = bkscr # black king side castling rights
        self.wqscr = wqscr # white queen side castling rights
        self.bqscr = bqscr # black queen side castling rights
    

#******************************************************************************************************

# Window Variables.

WIDTH, HEIGHT = 800, 800 # Set to be consistant with piece png file dimensions.
SQUARE_SIZE = HEIGHT // 8 # Sets size of each sqaure on board.
FPS = 60 # Frame rate of game.

#******************************************************************************************************

# Loads the PNG images of the pieces from the folder labeled 'Pieces'. Called in def main. 

IMAGES = {}

def loadImages():
    
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK'] # List of piece names.
    
    for piece in pieces:
        IMAGES[piece] = pg.image.load(os.path.join('Pieces', piece + '.png'))

#******************************************************************************************************

# Colors in RGB notation. Exact copy of my Chess.com color scheme. 

WHITE = (234, 233, 210)
BLUE = (75, 115, 153)
HIGHLIGHT_WHITE = (117, 199, 232)
HIGHLIGHT_BLUE = (38, 140, 204)


#******************************************************************************************************

# Mechanics of drawing the pieces, board, and highlight on the screen.

def draw_board(WINDOW, selected): # Creates the checkboared pattern on the screen. 
    
    colors = [WHITE, BLUE]
    colors_highlight = [HIGHLIGHT_WHITE, HIGHLIGHT_BLUE]
    
    for row in range(8):
        
        for col in range(8): # iterates over range of 2D 8x8 list.
            
            color = colors[(row+col) % 2] # Switches between color if row + col or square is even or odd.
            color_highlight = colors_highlight[(row+col) % 2] # Switches between highlight color if row + col is even or odd.
            
            if (row,col) == selected: #Highlights the selected square.
                pg.draw.rect(WINDOW, color_highlight, pg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else: # draws every other square with normal colors.
                pg.draw.rect(WINDOW, color, pg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    

def draw_pieces(WINDOW, board): # Places the images of the pieces on top of the checkerboard. 
    
    for row in range(8):
        
        for col in range(8):
            
            piece = board[row][col]
            
            if piece != "--": # If square is not supposed to be empty.
                
                WINDOW.blit(IMAGES[piece], pg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)) # Places png of piece on square.
    

def draw_BoardState(WINDOW, selected, bs): # Combines previous two functions. Called in def main.
    
    draw_board(WINDOW, selected)
    
    draw_pieces(WINDOW, bs.board)
    
#******************************************************************************************************

# Main Function of the Game

def main():
        
    pg.init() # Initializes pygame
    
    pg.display.set_caption("Chess") # Sets window name
    
    WINDOW = pg.display.set_mode((WIDTH, HEIGHT)) # Creates the window
    
    clock = pg.time.Clock() # Creates a clock for the FPS function
    
    loadImages() # Loads png images of pieces. 
    
    bs = BoardState() # Sets boardState class to bs for ease of use.
    
    validMoves = bs.validMoves() # Creates variable of valid moves.
    
    moveMade = False # Flag for when a valid move is made.
    
    selected = () # Tuple of row, col selected
    
    clicks = [] # List of tuples that contain first and second click (row,col). 
    
    running = True # Sets running variable to true when program is run.
    
    while running: # While loop that runs while game is running.
        
        # Game event queue. 
        
        for event in pg.event.get():
            
            if event.type == pg.QUIT: # If x button is pressed exit game.
                
                running = False
            
            # Mouse Presses.    
            elif event.type == pg.MOUSEBUTTONDOWN: #When the left mouse button is pressed...
                
                location = pg.mouse.get_pos() # Returns (x,y) pixel value of board.
                
                # Stores location values in row and col variables which are turned into our notation by integer division. 
                col = location[0]//SQUARE_SIZE 
                row = location[1]//SQUARE_SIZE
                
                
                if selected == (row,col): # Deselect. 
                    
                    selected = ()
                    clicks = []
                    
                else: # Select. 
                    
                    selected = (row,col)
                    clicks.append(selected)
              
                    
                if len(clicks) == 2: # Makes the move once a piece has been selected and the square the piece is moving to has been selected.
                    
                    move = Move(clicks[0], clicks[1], bs.board) # Creates variable of move.
                    
                    for i in range(len(validMoves)): # iterates over range of valid moves.
                        
                        if move == validMoves[i]: # If move trying to make is a valid move.        
                            
                            bs.makeMove(validMoves[i]) # Makes the move.
                            moveMade = True #Sets flag to true.
                            
                            # Resets value of move variables once a piece is moved. 
                            selected = ()
                            clicks = []
                        
                    if not moveMade: # Allows user to click on another piece without having to re-click to reset selected in clicks. 
                        
                        clicks = [selected]
        
            #Key Presses
            
            elif event.type == pg.KEYDOWN:
                
                if event.key == pg.K_BACKSPACE: # undo a move when backspace is pressed.

                    bs.undoMove() # undoes the last move made.
                    moveMade = True # Resets flag.
                    
                if event.key == pg.K_r: # Resets the game when r is pressed.
                    main()
                    
        if moveMade: # Generates new set of valid moves if a valid move has been made.
            
            validMoves = bs.validMoves()
            moveMade = False # Resets flag.
                
        draw_BoardState(WINDOW, selected, bs) # Draws the board state at the beginning and after each move. 
        clock.tick(FPS) # Sets frame rate of window at 60 FPS.
        pg.display.flip() # Updates the display so gamestate is current.
        
        if bs.checkMate== True: # If checkmate is detected.
            messagebox.showinfo('CHECKMATE!',('CHECKMATE! ' + ('WHITE' if not bs.white_turn else 'BLACK') + ' WINS'))  # Shows new window with winner info.              
            confirm = messagebox.askquestion("Confirm","Do you want to play one more game?") # Asks if they want to play another game.
            if confirm == "yes":
                main() # If yes restarts game.
            else:
                pg.quit() # If no ends game and closes windows.
                return
            
        if bs.staleMate==True: # If stalemate is detected.
            Tk().wm_withdraw()
            messagebox.showinfo('DRAW!',("DRAW DUE TO STALEMATE OR INSUFFICIENT MATERIAL")) # Displays draw info.
            confirm = messagebox.askquestion("Confirm","Do you want to play one more game?") # Asks if they want to play another game.
            if confirm == "yes":
                main() # If yes restarts game.
            else:
                pg.quit() # If no ends game and closes windows.
                return
        
    pg.quit() # Quits game and closes windows when running is false.


if __name__ == "__main__": # Calls the main function when the program is run. 
    
    main()
