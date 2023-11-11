from tkinter import *
import tkinter.font as font
from icecream import ic


class Transformations2D:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformations 2D Piotr Szumowski")
        self.bigFont = font.Font(size=12, weight="bold")
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.frame = LabelFrame(self.root, padx=0, pady=0, labelanchor="w")
        self.frame.pack(side="left", fill="both")
        # Button to add figure
        self.addFigureButton = Button(self.frame, text="Add figure", command=self.addFigure)
        self.addFigureButton.grid(row=0, column=0, columnspan=2, sticky="WE")
        self.addFigureButton['font'] = self.bigFont
        # Button to delete figure
        self.deleteFigureButton = Button(self.frame, text="Delete figure", command=self.deleteFigure)
        self.deleteFigureButton.grid(row=1, column=0, columnspan=2, sticky="WE")
        self.deleteFigureButton['font'] = self.bigFont
        # Validation
        self.vcmd = (self.frame.register(self.validateEntry))
        # White space to draw Bezier Curve
        self.drawSpace = Canvas(self.root, bg="white")
        self.drawSpace.pack(fill="both", expand=True)
        # Binding of mouse click and drag
        self.drawSpace.bind("<ButtonPress-1>", self.drawOrMoveVertex)
        self.drawSpace.bind("<B1-Motion>", self.movePointByMouse)
        self.drawSpace.bind("<ButtonRelease-1>", self.endMovePointByMouse)
        self.figureEntries = {}
        self.figureVertexes = {}
        self.lastFigureNumber = 0
        self.selectedFigure = 0
        self.selectedFigureLabel = None
        self.offsetX, self.offsetY = 0, 0
        self.selectedVertex = None

    def addFigure(self):
        ic("OK")
        number = self.lastFigureNumber = self.lastFigureNumber + 1
        self.figureEntries[number] = []
        self.figureVertexes[number] = []
        figureLabel = LabelFrame(self.frame, text=f"Figure {number}", labelanchor="nw")
        figureLabel.grid(row=number+1, column=0, columnspan=2, sticky="WE")
        self.onFigureSelect(figureLabel, number)
        # Frame for vertexes
        vertexesLabel = LabelFrame(figureLabel, text="Vertexes positions", labelanchor="nw")
        vertexesLabel.grid(row=0, column=0, columnspan=2, sticky="WE")
        # X and Y labels
        positionXLabel = Label(figureLabel, text="X")
        positionXLabel.grid(row=1000, column=0)
        positionXLabel['font'] = self.bigFont
        positionYLabel = Label(figureLabel, text="Y")
        positionYLabel.grid(row=1000, column=2)
        positionYLabel['font'] = self.bigFont
        # X and Y entries
        positionXEntry = Entry(figureLabel, justify=CENTER, width=7, validate='all', validatecommand=(self.vcmd, '%P'))
        positionXEntry.grid(row=1000, column=1)
        positionYEntry = Entry(figureLabel, justify=CENTER, width=7, validate='all', validatecommand=(self.vcmd, '%P'))
        positionYEntry.grid(row=1000, column=3)
        # Button to add vertex
        addVertexButton = Button(figureLabel, text="Add vertex", command=lambda: self.addVertexByParameters(positionXEntry.get(), positionYEntry.get()))
        addVertexButton.grid(row=1001, column=0, columnspan=4, sticky="WE")
        addVertexButton['font'] = self.bigFont
        # Bind <Button-1> event to figureLabel
        figureLabel.bind("<Button-1>", lambda event, figureNumber=number: self.onFigureSelect(figureLabel, figureNumber))
        # Bind <Button-1> event to all elements within figureLabel
        for widget in figureLabel.winfo_children():
            widget.bind("<Button-1>", lambda event, figureNumber=number: self.onFigureSelect(figureLabel, figureNumber))

    def onFigureSelect(self, labelFrame, figureNumber):
        if self.selectedFigureLabel:
            self.selectedFigureLabel.config(highlightthickness=0)
            for vertex in self.figureVertexes[self.selectedFigure]:
                self.drawSpace.itemconfig(vertex[2], fill="black", outline="black")
        labelFrame.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.selectedFigureLabel = labelFrame
        self.selectedFigure = figureNumber
        for vertex in self.figureVertexes[self.selectedFigure]:
            self.drawSpace.itemconfig(vertex[2], fill="lightgreen", outline="lightgreen")

    def deleteFigure(self):
        ic("usun")
        if self.selectedFigureLabel:
            self.selectedFigureLabel.destroy()
            self.selectedFigureLabel = None
            self.selectedFigure = 0


    def getVertexByPointIndexInCanvas(self, vertexIndexInCanvas):
        for sub in self.figureVertexes[self.selectedFigure]:
            if sub[2] == vertexIndexInCanvas:
                return sub
        return None

    def movePointByMouse(self, event):
        if self.selectedFigure and self.selectedVertex and any(self.selectedVertex == sub[2] for sub in self.figureVertexes[self.selectedFigure]):
            x, y = event.x, event.y
            self.drawSpace.coords(self.selectedVertex, x - self.offsetX, y - self.offsetY, x - self.offsetX + self.drawSpace.coords(self.selectedVertex)[2] - self.drawSpace.coords(self.selectedVertex)[0], y - self.offsetY + self.drawSpace.coords(self.selectedVertex)[3] - self.drawSpace.coords(self.selectedVertex)[1])
            vertex = self.getVertexByPointIndexInCanvas(self.selectedVertex)
            vertexIndex = self.figureVertexes[self.selectedFigure].index(vertex)
            self.figureVertexes[self.selectedFigure][vertexIndex][0], self.figureVertexes[self.selectedFigure][vertexIndex][1] = x, y
            entryX, entryY = self.figureEntries[self.selectedFigure][vertexIndex][0], self.figureEntries[self.selectedFigure][vertexIndex][1]
            entryX.delete(0, END)
            entryX.insert(0, str(x))
            entryY.delete(0, END)
            entryY.insert(0, str(y))

    def endMovePointByMouse(self, event):
        self.selectedVertex = None

    def drawOrMoveVertex(self, event):
        if self.selectedFigure:
            x, y = event.x, event.y
            figureNumber = self.selectedFigure
            ic("DRAW", x, y, figureNumber)
            shapes = self.drawSpace.find_overlapping(x, y, x, y)
            if shapes:
                # move point
                self.selectedVertex = shapes[-1]
                self.offsetX = x - self.drawSpace.coords(self.selectedVertex)[0]
                self.offsetY = y - self.drawSpace.coords(self.selectedVertex)[1]
            else:
                # draw  point
                vertex = self.drawSpace.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill="black")
                self.figureVertexes[figureNumber].append([x, y, vertex])
                self.addVertexToFigureLabel(x, y)

    def addVertexToFigureLabel(self, x, y):
        ic(self.selectedFigure, self.figureVertexes)
        if self.selectedFigure and self.selectedFigureLabel:
            figureNumber = self.selectedFigure
            rowIndex = len(self.figureVertexes[figureNumber]) - 1
            myVarX = StringVar()
            entryX = Entry(self.selectedFigureLabel, justify=CENTER, width=12, textvariable=myVarX, validate="all", validatecommand=(self.vcmd, '%P'))
            myVarX.trace('w', lambda name, index, mode, var=myVarX, figure=figureNumber, row=rowIndex, col=0: self.vertexEntryChanged(figure, row, col, var.get()))
            entryX.grid(row=rowIndex, column=0, columnspan=2, sticky="ew")
            entryX.insert(0, x)
            myVarY = StringVar()
            entryY = Entry(self.selectedFigureLabel, justify=CENTER, width=12, textvariable=myVarY, validate="all", validatecommand=(self.vcmd, '%P'))
            myVarY.trace('w', lambda name, index, mode, var=myVarY, figure=figureNumber, row=rowIndex, col=1: self.vertexEntryChanged(figure, row, col, var.get()))
            entryY.grid(row=rowIndex, column=2, columnspan=2, sticky="ew")
            entryY.insert(0, y)
            self.figureEntries[self.selectedFigure].append([entryX, entryY])
            # zmiana koloru na zielony dla wszystkich punktow
            for vertex in self.figureVertexes[self.selectedFigure]:
                self.drawSpace.itemconfig(vertex[2], fill="lightgreen", outline="lightgreen")

    def addVertexByParameters(self, x, y):
        ic(x, y)
        if x and y:
            self.drawOrMoveVertex(EventWithXY(x, y))

    def vertexEntryChanged(self, figureNumber, row, column, value):
        if value:
            ic(figureNumber, row, column, value, self.figureVertexes)
            # vertex = self.figureVertexes[figureNumber]
            self.figureVertexes[figureNumber][row][column] = int(value)
            self.movePointByParameters(self.figureVertexes[figureNumber][row][2], self.figureVertexes[figureNumber][row][0], self.figureVertexes[figureNumber][row][1])

    def movePointByParameters(self, itemIndex, newX, newY):
        # ic(itemIndex, newX, newY)
        self.drawSpace.coords(itemIndex, newX - 5, newY - 5, newX + 5, newY + 5)

    @staticmethod
    def validateEntry(P):
        if P == "" or (str.isdigit(P)):
            return True
        else:
            return False


class EventWithXY:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
