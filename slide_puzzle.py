# Slide Puzzle
# Auther: G.G.Otto
# Version: 1.3

from tkinter import *
import random
import time
import os
import os.path as path
import tkinter.messagebox as msg
import tkinter.colorchooser as color
import tkinter.filedialog as fileopen
import tkinter.ttk as ttk

class PuzzlePiece(Canvas):
    '''represents one of the puzzle pieces'''

    def __init__(self, master, number, row, column, image=None, clickable=True, bg="#46bf79", numColor="#ecd9a9"):
        '''PuzzlePiece(master, number, row, column, image=None, clickable=True) -> PuzzlePiece
        constructs the puzzle piece'''
        Canvas.__init__(self, master, bg=bg, width=300/4-2, height=300/4-2, highlightthickness=0)
        self.number = number
        self.row = row
        self.column = column
        self.oldRow = row
        self.oldColumn = column
        self.master = master

        # get canvas for piece
        if isinstance(master, Canvas):
            clickable = False
            canvas = master
        else:
            canvas = self.master.get_slide_canvas()

        # draw piece
        canvas.create_window(300*(row + 0.5)/4,300*(column + 0.5)/4, window=self, tags="piece"+str(number))
        if image == None:
            self.create_text(75/2, 37, text=str(number), fill=numColor, font=("Arial",30))
        else:
            # get tkinter image object
            self["bg"] = "white"
            photo = PhotoImage(file=image)
            self.create_image(-(row-2)*int(self["width"]), -(column-2)*int(self["height"]), image=photo)
            self.img = photo # keeps image in place

        # update stats
        self.image = image
        self.numColor = numColor
        self.hints = False

        self.clickable = clickable

    def get_look(self):
        '''PuzzlePiece.get_look() -> tuple
        returns a tuple with the look of the piece'''
        return self["bg"], self.numColor, self.image

    def get_number(self):
        '''PuzzlePiece.get_number() -> int
        returns the number of the piece'''
        return self.number

    def get_pos(self):
        '''PuzzlePiece.get_pos() -> (row, column)
        returns a tuple with the position'''
        return (self.row, self.column)

    def is_clickable(self):
        '''PuzzlePiece.is_clickable() -> None
        returns if the piece is clickable'''
        return self.clickable

    def set_clickable(self, boolean):
        '''PuzzlePiece.set_clickable(boolean) -> None
        sets the clickable state of the piece'''
        self.clickable = boolean

    def move_by(self, moveBy):
        '''PuzzlePiece.move_by(moveBy) -> None
        moves the piece by tuple moveBy'''
        self.column += moveBy[1]
        self.row += moveBy[0]

    def select_piece(self, event=''):
        '''PuzzlePiece.select_piece(event) -> None
        selects the piece for moving'''
        if not self.clickable:
            return
        
        self.master.move_piece((self.row, self.column))

    def change_piece(self, bg=None, fg=None, image=None):
        '''PuzzlePiece.change_piece(bg=None, fg=None, image=None) -> None
        changes the look of the piece'''
        self.delete("all")
        
        if image != None:
            # get tkinter image object
            self["bg"] = "white"
            photo = PhotoImage(file=image)
            self.create_image(-(self.oldRow-2)*int(self["width"]), -(self.oldColumn-2)*int(self["height"]), image=photo)
            self.img = photo # keeps image in place
            self.image = image
        else:
            self.image = None
            self.delete("all")
            self["bg"] = bg
            self.create_text(75/2, 37, text=str(self.number), fill=fg, font=("Arial",30))
            self.numColor = fg

        # draw hint if needed
        if self.hints:
            for i in range(2):
                self.toggle_hints()

    def toggle_hints(self):
        '''PuzzlePiece.toggle_hints() -> None
        toggles the hints on the piece'''
        if self.hints:
            self.hints = False
            self.delete("hint")
        else:
            self.hints = True
            self.create_oval(float(self["width"])-21, 1, float(self["width"])-1, 21, fill="black", tags="hint")
            self.create_text(float(self["width"])-11, 11, text=str(self.number), fill="white", tags="hint")

class PuzzleStats(Frame):
    '''represents the bar for teh stats'''

    def __init__(self, master):
        '''PuzzleStats(master) -> Frame
        constructs the frame for the stat bar'''
        # labels for scores
        self.moveLabel = Label(master, text="Moves: 0", font=("calibri", 14), bg="white")
        self.moveLabel.grid(row=3, column=0)
        self.timeLabel = Label(master, text="Time: 0:0.0", font=("calibri", 14), bg="white")
        self.timeLabel.grid(row=3, column=1)

        # attributes
        self.master = master
        self.bestShown = False
        self.bestScores = self.retrieve_best()
        self.moves = 0

        # time attributes
        self.timeRecord = 0
        self.startTime = time.time()
        self.last = self.startTime
        self.stopped = False
        
        # labels for best scores
        self.bestMoves = Label(master, text=f"Best: {self.bestScores[0]}", font=("calibri", 14), bg="white")
        if self.bestScores[0] != "NA":
            self.bestTime = Label(master, text=f"Best: {int(self.bestScores[1]//60)}:{int(self.bestScores[1]%60*10)/10}", font=("calibri", 14), bg="white")
        else:
            self.bestTime = Label(master, text="Best: NA", font=("calibri", 14), bg="white")

    def is_best_shown(self):
        '''PuzzleStats.is_best_shown() -> bool
        returns if the best scores are shown or not'''
        return self.bestShown

    def update_best(self):
        '''PuzzleStats.update_best() -> str
        updates the best scores. returns a str with message if updated'''
        if self.bestScores == ["NA","NA"]:
            self.bestScores = [10000, 10000]
        
        output = "\n"
        
        # update best moves
        if self.moves < self.bestScores[0]:
            self.bestScores[0] = self.moves
            self.bestMoves["text"] = "Best:" + self.moveLabel["text"][6:]
            output += "\nNew best moves!"

        # update timer
        if self.timeRecord < self.bestScores[1]:
            self.bestScores[1] = self.timeRecord
            self.bestTime["text"] = "Best:" + self.timeLabel["text"][5:]
            output += "\nNew best time!"

        self.save_best()
        return output
    
    def update_moves(self, movesToAdd=1):
        '''PuzzleStats.update_moves(moveToAdd=1) -> None
        updates the current moves'''
        self.moves += movesToAdd
        self.moveLabel["text"] = f"Moves: {self.moves}"

    def start_timer(self, startTime=None):
        '''PuzzleStats.start_timer(time.time()) -> None
        starts the timer to record current time'''
        if startTime != None:
            self.stopped = False
            self.startTime = startTime

        if not self.stopped:
            self.last = time.time()
            record = self.timeRecord + self.last - self.startTime # time since start

            # update timer
            self.timeLabel["text"] = "Time: " + str(int(record//60)) + ":" + str(int(record%60*10)/10)
            self.master.after(100, self.start_timer)

    def stop_timer(self): 
        '''PuzzleStats.stop_timer() -> None
        stops the timer that records current time'''
        self.timeRecord += self.last - self.startTime
        self.stopped = True

    def clear_stats(self):
        '''PuzzleStats.clear_stats() -> None
        clears all the stats for the game'''
        self.stopped = True
        self.timeRecord = 0
        self.startTime = time.time()
        self.last = self.startTime
        self.moves = 0

        # clear out labels
        self.timeLabel["text"] = "Time: 0:0.0"
        self.moveLabel["text"] = "Moves: 0"

    def toggle_best(self):
        '''PuzzleStats.toggle_best() -> None
        shows or hides the best scores'''
        if self.bestShown:
            self.bestMoves.grid_remove()
            self.bestTime.grid_remove()
            self.bestShown = False
        else:
            self.bestMoves.grid(row=4, column=0)
            self.bestTime.grid(row=4, column=1)
            self.bestShown = True

    def retrieve_best(self):
        '''PuzzleStats.retrieve_best() -> tuple
        return the best scores as (moves, time)'''
        if not path.isfile("slide_puzzle_best_scores.txt"):
            return ["NA","NA"]

        # retrieve from file
        inFile = open("slide_puzzle_best_scores.txt", "r")
        scores = inFile.read().split()
        inFile.close()

        return [int(scores[0]), float(scores[1])]

    def save_best(self):
        '''PuzzleStats.save_best() -> None
        saves the best high score'''
        outFile = open("slide_puzzle_best_scores.txt", "w")
        outFile.write(f"{self.bestScores[0]} {self.bestScores[1]}")
        outFile.close()

class PuzzleCustomize(Frame):
    '''represents the root for the new window for customizing'''

    def __init__(self, master):
        '''PuzzleCustomize(master) -> Tk
        constructs the window for the custom root'''
        Frame.__init__(self, bg="white")
        self.master = master

        # title label and instructions
        Label(self, text="Customize Puzzle", width=25, font=("times new roman", 15, "bold"), fg="red", bg="white").grid(row=0, column=0, columnspan=4)
        Label(self, text="Change puzzle colors:", bg="white", font=("times new roman", 10)).grid(row=2, column=0, sticky=W, columnspan=2)
        Label(self, text="Get a photo for puzzle:", bg="white", font=("times new roman", 10)).grid(row=2, column=2, sticky=W, columnspan=2)

        # separators
        ttk.Separator(self).grid(row=1, column=0, columnspan=4, sticky=W+E)
        ttk.Separator(self, orient=VERTICAL).grid(row=2, column=1, rowspan=5, sticky=N+S)   
        
        # buttons to get colors
        self.bgColor = self.master.get_slide_canvas()["bg"]
        Button(self, text=" Background Color", command=lambda: self.change_puzzle("bg"), width=15,
            relief=FLAT, bg="white", activebackground="white", fg="#0000aa", anchor=W).grid(row=3, column=0, sticky=W)
        Button(self, text=" Piece Color", command=lambda: self.change_puzzle("pc"), width=15,
            relief=FLAT, bg="white", activebackground="white", fg="#0000aa", anchor=W).grid(row=4, column=0, sticky=W)
        Button(self, text=" Number Color", command=lambda: self.change_puzzle("nc"), width=15,
            relief=FLAT, bg="white", activebackground="white", fg="#0000aa", anchor=W).grid(row=5, column=0, sticky=W)

        # file
        self.fileChoice = StringVar(value="")
        fileOption = ttk.Combobox(self, values=self.get_puzzles(), width=10, textvariable=self.fileChoice)
        fileOption.grid(row=3, column=2, sticky=W)
        ttk.Button(self, text="Import", command=self.export, width=7).grid(row=3, column=3, sticky=W)
        Button(self, text="Browse Files ", command=lambda: self.export(True),
            relief=FLAT, bg="white", activebackground="white", fg="#0000aa", anchor=W, width=10).grid(row=4, column=2, sticky=W)
        Button(self, text="Clear file ", command=self.clear_photo,
            relief=FLAT, bg="white", activebackground="white", fg="#0000aa", anchor=W, width=10).grid(row=5, column=2, sticky=W)
        
        # shuffle length
        ttk.Separator(self).grid(row=6, column=0, columnspan=4, sticky=W+E)
        self.shuffleLength = Scale(self, orient=HORIZONTAL, length=270, label="Shuffle Length", showvalue=0,
            bg="white", sliderrelief=GROOVE, sliderlength=18, highlightthickness=5, 
            highlightbackground="white", from_=5, to=55, activebackground="#a0ffff")
        self.shuffleLength.grid(row=7, column=0, columnspan=4)
        self.shuffleLength.set(master.get_shuffle_length().get())
        
        # cancel and apply buttons and frame for buttons
        buttonFrame = Frame(self, bg="white")
        buttonFrame.grid(row=8, column=0, columnspan=4)
        ttk.Button(buttonFrame, text="Cancel", command=self.cancel).grid(row=3, column=1, sticky=W)
        ttk.Button(buttonFrame, text="Apply", command=self.apply).grid(row=3, column=0, sticky=E)

        # canvas to preview the picture
        self.previewCanvas = Canvas(buttonFrame, bg=master.get_slide_canvas()["bg"], width=298, height=298)
        self.previewCanvas.grid(row=1, column=0, columnspan=2)

        # add puzzle pieces
        num = 1
        self.pieces = {}
        for row in range(4):
            for column in range(4):
                looks = master.get_pieces()[0].get_look()
                newPiece = PuzzlePiece(self, num, row, column, None, False)
                newPiece.change_piece(looks[0], looks[1], looks[2])
                self.pieces[row, column] = newPiece
                num += 1
        self.pieceBg = self.pieces[0,0].get_look()[0]

    def get_slide_canvas(self):
        '''PuzzleCustomize.get_slide_canvas() -> Canvas
        returns the canvas for the pieces to slide on'''
        return self.previewCanvas

    def cancel(self):
        '''PuzzleCustomize.cancel() -> None
        cancels the customization'''
        self.master.toggle_customize()
        self.destroy()
        PuzzleCustomize.__init__(self, self.master)

    def apply(self):
        '''PuzzleCustomize.apply() -> None
        applies the customization'''
        if self.shuffleLength.get() < 25 and \
           not msg.askyesno(message="If the shuffle length is set to less than normal, best scores will not be counted. Do you want to continue?"):
            return
        
        self.master.get_shuffle_length().set(self.shuffleLength.get())
        self.master.get_slide_canvas()["bg"] = self.previewCanvas["bg"]
        
        # change piece look
        for piece in self.master.get_pieces():
            look = self.pieces[0,0].get_look()
            piece.change_piece(look[0], look[1], look[2])
        self.master.toggle_customize()

    def change_puzzle(self, key):
        '''PuzzleCustomize.change_puzzle(key) -> None
        changes the background of the canvas
        keys: can be "bg", "pc", "nc"'''
        # background of canvas
        if key == "bg":
            self.previewCanvas["bg"] = color.askcolor("#ecd9a9")[1]
        # piece background
        elif key == "pc":
            self.pieceBg = color.askcolor("#46bf79")[1]
            for piece in self.pieces:
                self.pieces[piece]["bg"] = self.pieceBg
        elif key == "nc":
            # get color
            numColor = color.askcolor("#ecd9a9")[1]
            if numColor == None:
                return
            for piece in self.pieces:
                self.pieces[piece].change_piece(self.pieceBg, numColor)

    def is_valid_file(self, file):
        '''PuzzleCustomize.is_valid_file(file) -> bool
        returns if the file is valid or not'''
        return isinstance(file, str) and len(file) > 4 and (file[-4:].lower() == ".png" or file[-4:].lower() == ".gif")

    def export(self, choose=False):
        '''PuzzleCustomize.export(choose) -> None
        exports the file in combobox'''
        # get file name
        if choose:
            file = fileopen.askopenfilename(title="Optimal Picture Size: 300x300")
            if file == "":
                return
        else:
            file = self.fileChoice.get()
        
        # check if valid
        if not choose and not path.exists(file):
            msg.showerror(message="File not found. Please choose a different file.")
            return
        elif not self.is_valid_file(file):
            msg.showerror(message="Invalid file. Please choose a different file.")
            return

        # change pieces
        for piece in self.pieces:
            # make sure the file is readable
            try:
                self.pieces[piece].change_piece(image=file)
            except:
                look = self.pieces[0,1].get_look()
                self.pieces[0,0].change_piece(look[0], look[1], look[2])
                msg.showerror(message="This file cannot be read. Please choose a new file.")
                return

    def get_puzzles(self):
        '''PuzzleCustomize.get_puzzles() -> tuple
        returns a tuple of all files in current folder'''
        output = []
        for file in os.listdir(path.dirname(path.realpath(__file__))):
            if self.is_valid_file(file):
                output.append(file)
        return tuple(output)

    def clear_photo(self):
        '''PuzzleCustomize.get_puzzle() -> tuple
        clears the photo from the pieces'''
        for piece in self.pieces:
            look = self.pieces[0,0].get_look()
            self.pieces[piece].change_piece(self.pieceBg, look[1])
                
class PuzzleFrame(Frame):
    '''represents the frame of the puzzle'''

    def __init__(self, master, image=None):
        '''PuzzleFrame(master, image=None) -> PuzzleFrame
        constructs the puzzle frame'''
        Frame.__init__(self, master, bg="white")
        self.grid()

        # canvas for pieces to slide on
        self.slideCanvas = Canvas(self, width=298, height=298, bg="#ecd9a9")
        self.slideCanvas.grid(row=1, column=0, columnspan=2)
        
        # create pieces
        pieceNum = 1
        self.pieces = {}
        self.pieceList = []
        self.empty = (3,3)
        for column in range(4):
            for row in range(4):
                # stop if enough
                if pieceNum == 16:
                    break
                # add pice
                newPiece = PuzzlePiece(self, pieceNum, row, column, image)
                self.pieces[row,column] = newPiece
                self.pieceList.append(newPiece)
                pieceNum += 1
        self.pieceList.append(PuzzlePiece(self, 16, 3, 3, image))

        # information for puzzle
        self.aWait = StringVar()
        self.isWin = True
        self.image = image
        self.shuffleLength = IntVar(value=30)
        
        # stats
        self.stats = PuzzleStats(self)
        self.customize = PuzzleCustomize(self)
        self.customShown = False
        self.hints = False
        self.paused = False

        # buttons
        buttonFrame = Frame(self)
        buttonFrame.grid(row=0, column=0, sticky=W, columnspan=2)
        self.shuffleButton = Button(buttonFrame, text="Shuffle", command=self.shuffle, bg="white", activebackground="white", relief=FLAT)
        self.shuffleButton.grid(row=0, column=1)
        self.solveButton = Button(buttonFrame, text="Solve", bg="white", activebackground="white", relief=FLAT, command=self.solve)
        self.solveButton.grid(row=0, column=2)
        self.pauseButton = Button(buttonFrame, text="Pause", bg="white", activebackground="white", relief=FLAT, command=self.toggle_pause, state=DISABLED)
        self.pauseButton.grid(row=0, column=3)
        self.previewButton = Button(buttonFrame, text="Preview", bg="white", activebackground="white", relief=FLAT, command=self.open_preview)
        self.previewButton.grid(row=0, column=4)

        # option menu
        options = Menubutton(buttonFrame, text="Options", relief=FLAT, bg="white", activebackground="white")
        options.grid(row=0, column=0)
        self.optionBar = Menu(options, tearoff=0)
        options['menu'] = self.optionBar

        # create option menu
        self.optionBar.add_command(label="Quit", command=master.destroy)
        self.optionBar.add_command(label="Clear", command=self.complete_restart)
        self.optionBar.add_command(label="Customize", command=self.toggle_customize)
        self.optionBar.add_checkbutton(label="Hints", command=self.toggle_hints)
        self.optionBar.add_checkbutton(label="Best Stats", command=self.stats.toggle_best)

        self.buttons = (self.shuffleButton, self.solveButton, self.pauseButton, self.previewButton, options)
            
    def get_slide_canvas(self):
        '''PuzzleFrame.get_slide_canvas() -> Canvas
        returns teh slide canvas'''
        return self.slideCanvas

    def get_pieces(self):
        '''PuzzleFrame.get_pieces() -> dict
        returns the pieces of the game'''
        return self.pieceList

    def get_shuffle_length(self):
        '''PuzzleFrame.get_shuffle_length() -> int
        returns the shuffle length of the game'''
        return self.shuffleLength

    def get_stats(self):
        '''PuzzleFrame.get_stats() -> PuzzleStats
        returns the stats for the puzzle'''
        return self.stats

    def get_direction_to_move(self, piece):
        '''PuzzleFrame.get_direction_to_move(piece, divideBy=20) -> tuple
        returns a tuple with the direction the piece must move'''
        direction = (0,0)
        num = 1
        # get direction
        if piece[0] < self.empty[0]:
            direction = (num, 0)
        elif piece[0] > self.empty[0]:
            direction = (-num, 0)
        elif piece[1] < self.empty[1]:
            direction = (0, num)
        elif piece[1] > self.empty[1]:
            direction = (0, -num)

        return direction

    def get_pieces_to_move(self, piece):
        '''PuzzleFrame.get_direction_to_move(piece) -> list
        returns a list of the pieces to move'''
        output = []
        # loop through all pieces
        for otherPiece in self.pieces:
            if ((self.empty[0] < otherPiece[0] <= piece[0] or piece[0] <= otherPiece[0] < self.empty[0]) and otherPiece[1] == self.empty[1]) or \
               ((self.empty[1] < otherPiece[1] <= piece[1] or piece[1] <= otherPiece[1] < self.empty[1]) and otherPiece[0] == self.empty[0]):
                output.append(self.pieces[otherPiece])

        return output

    def toggle_button_disable(self):
        '''PuzzleFrame.toggle_button_disable() -> None
        sets the disable of the buttons'''
        for button in self.buttons:
            if button["state"] == DISABLED:
                button["state"] = ACTIVE
            else:
                button["state"] = DISABLED

    def toggle_piece_clickable(self, setTo=None):
        '''PuzzleFrame.toggle_piece_clickable(setTo) -> None
        sets the clickableness of the piece'''
        for piece in self.pieceList:
            if setTo == None:
                piece.set_clickable(not piece.is_clickable())
            else:
                piece.set_clickable(setTo)

    def toggle_customize(self):
        '''PuzzleFrame.toggle_customize() -> None
        shows or hides the customize window'''
        # if already shown
        if self.customShown:
            self.customize.grid_remove()
            self.grid()
            self.customShown = False
            if not self.isWin and not self.paused:
                self.stats.start_timer(time.time())

        # if hidden
        else:
            if not self.isWin and not self.paused:
                self.stats.stop_timer()
            self.grid_remove()
            self.customize.grid()
            self.customShown = True
        self.focus_set()

    def toggle_hints(self):
        '''PuzzleFrame.toggle_hints() -> None
        shows or hides the hints'''
        for piece in self.pieceList:
            piece.toggle_hints()
        self.hints = not self.hints
        
    def toggle_pause(self):
        '''PuzzleFrame.toggle_pause() -> None
        plays or pauses the game'''
        # play 
        if self.paused:
            self.slideCanvas.delete("pause")
            self.paused = False
            self.pauseButton["text"] = "Pause"
            # start up
            self.stats.start_timer(time.time())
            self.toggle_piece_clickable()
            self.previewButton["state"] = ACTIVE
        # pause
        else:
            self.slideCanvas.create_window(298/2, 151, window=Label(text="Paused", font=("calabri",39), height=5, width=10), tags="pause")
            self.paused = True
            self.pauseButton["text"] = "Play"
            # stop
            self.stats.stop_timer()
            self.toggle_piece_clickable()
            self.previewButton["state"] = DISABLED
           
    def move_piece(self, piece, checkWin=True, isSolving=False):
        '''PuzzleFrame.move_piece(piece, checkWin, isSolving) -> None
        moves piece if possible
        checkWin: bool to tell code to check for win or not'''
        if piece[0] != self.empty[0] and piece[1] != self.empty[1]:
            return
        
        # animate the move
        direction = self.get_direction_to_move(piece)
        pieces = self.get_pieces_to_move(piece)
        self.animate_move((direction, pieces), checkWin)
        self.master.wait_variable(self.aWait)

        # move all internally
        for pieceToMove in pieces:
            pieceToMove.move_by(direction)
            self.pieces[pieceToMove.get_pos()] = pieceToMove
        self.empty = piece

        # check for win
        if checkWin and not self.isWin:
            if not isSolving:
                self.stats.update_moves()
            self.check_win()
        
    def animate_move(self, info=None, toggle=True):
        '''PuzzleFrame.animate_move(info, toggle) -> None
        animates a single frame of the move'''
        # set up animation attributes
        if info != None:
           # set up animation attributes
           self.aDirection = info[0]
           self.aPieces = info[1]
           self.aCount = 0
           self.aWait.set("yes")
           self.aToggle = toggle

           # disable all buttons that are being moved
           if self.aToggle:
               self.toggle_piece_clickable(False)

        # move all pieces
        for piece in self.aPieces:
            self.slideCanvas.move("piece"+str(piece.get_number()), self.aDirection[0]/2, self.aDirection[1]/2)
        self.aCount += 1

        # end if needed
        if self.aCount == 150:
            # enable pieces
            if self.aToggle:
                self.toggle_piece_clickable(True)
            self.aWait.set("no")
            return

        # do over again
        self.master.after(1, self.animate_move)

    def shuffle(self):
        '''PuzzleFrame.shuffle() -> None
        shuffles the puzzle for amount of times'''
        # reset up if win
        if self.isWin:
            self.isWin = False
            self.pieceList.pop(-1)
            self.slideCanvas.delete("piece16")
            self.pauseButton["state"] = ACTIVE
            # bind all pieces
            for piece in self.pieces:
                self.pieces[piece].bind("<Button-1>", self.pieces[piece].select_piece)

        # unpause game
        if self.paused:
            self.toggdle_pause()
            
        self.toggle_button_disable()
        self.toggle_piece_clickable(False)
        self.stats.clear_stats()
        
        indexToUse = random.randint(0,1)
        # loop until finished
        for i in range(self.shuffleLength.get()):
            # get random piece info
            indexToUse = (indexToUse + 1) % 2 # index to be using on self.empty
            listToUse = [n for n in range(4) if n != self.empty[(indexToUse+1)%2]] # list to choose new coord from

            # get random piece
            randomPos = [0, 0]
            randomPos[indexToUse] = self.empty[indexToUse]
            randomPos[(indexToUse+1)%2] = random.choice(listToUse)

            # move piece
            self.move_piece(randomPos, False)

        if self.aWait.get() == "yes":
            self.master.wait_variable(self.aWait)
            
        self.toggle_button_disable()
        self.toggle_piece_clickable(True)
        self.stats.start_timer(time.time())

    def open_preview(self):
        '''PuzzleFrame.open_preview() -> None
        opens the preview window'''
        canvas = Canvas(self, width=298, height=298, bg=self.slideCanvas["bg"])

        # get look
        if self.empty != (0,0):
            look = self.pieces[0,0].get_look()
        else:
            look = self.pieces[0,1].get_look()

        # create pieces    
        num = 1
        for column in range(4):
            for row in range(4):
                PuzzlePiece(canvas, num, row, column, look[2], False, look[0], look[1])
                num += 1

        # disable preview button
        self.previewButton["state"] = DISABLED
        self.slideCanvas.grid_remove()
        canvas.grid(row=1, column=0, columnspan=2)

        # remove canvas
        wait = StringVar()
        self.master.after(2000, lambda: wait.set("go"))
        self.master.wait_variable(wait)
        canvas.destroy()
        self.slideCanvas.grid()
        self.previewButton["state"] = ACTIVE

    def is_win(self):
        '''PuzzleFrame.is_win() -> bool
        returns if the game is won or not'''
        if self.empty != (3,3):
            return False

        # loop and check if false
        last = 0
        for column in range(4):
            for row in range(4):
                if (row, column) == (3,3):
                    break
                # get if false
                if self.pieces[row, column].get_number() - last != 1:
                    return False
                last = self.pieces[row, column].get_number()
        return True

    def check_win(self):
        '''PuzzleFrame.is_win() -> None
        returns if the player has won or not'''
        # check for a win
        if self.is_win():
            look = self.pieces[0,0].get_look()
            finalPiece = PuzzlePiece(self, 16, 3, 3, look[2], bg=look[0], numColor=look[1])
            self.pieceList.append(finalPiece)

            # add hint if needed
            if self.hints:
                finalPiece.toggle_hints()

            self.pauseButton["state"] = DISABLED
            self.stats.stop_timer()

            # get best
            bests = "\n"
            if self.shuffleLength.get() >= 25:
                bests = self.stats.update_best()
            
            msg.showinfo(message="Congratulations! You won!"+bests)
            self.isWin = True
            
            # unbind all
            for piece in self.pieces:
                self.pieces[piece].unbind("<Button-1>")

    def complete_restart(self):
        '''PuzzleFrame.complete_restart() -> None
        clears the entire puzzle settings'''
        if self.hints:
            self.optionBar.invoke(3)
        if self.stats.is_best_shown():
            self.optionBar.invoke(4)
        self.customize.destroy()
        self.destroy()
        PuzzleFrame.__init__(self, self.master)

    def solve(self):
        '''PuzzleFrame.solve() -> None
        solves the puzzle'''
        look = self.pieceList[0].get_look()
        self.slideCanvas.delete("all")

        # reset attributes
        self.isWin = True
        self.stats.clear_stats()
        self.pieceList.clear()
        self.pieces = {}
        self.pauseButton["state"] = DISABLED
        
        # create pieces
        num = 1
        for column in range(4):
            for row in range(4):
                newPiece = PuzzlePiece(self, num, row, column, look[2], False, look[0], look[1])
                self.pieceList.append(newPiece)
                self.pieces[row, column] = newPiece
                num += 1

                # deal with hints
                if self.hints:
                    newPiece.toggle_hints()
        self.empty = (3,3)
        
root = Tk()
root.title("Slide Puzzle")
PuzzleFrame(root)
mainloop()
