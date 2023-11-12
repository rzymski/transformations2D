from tkinter import *
import tkinter.font as font
from icecream import ic
from math import cos, sin, radians, atan2
import re


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
        # Validation
        self.validation = (self.frame.register(self.validateEntry))
        # self.validationFloat = (self.frame.register(self.validateEntryFloat))
        self.validationRangeFromMinus360To360 = (self.frame.register(self.validateEntryRangeFromMinus360To360))
        # Button to add figure
        self.addFigureButton = Button(self.frame, text="Add figure", command=self.addFigure, padx=12, pady=12)
        self.addFigureButton.grid(row=0, column=0, columnspan=2, sticky="WE")
        self.addFigureButton['font'] = self.bigFont
        # Button to delete figure
        self.deleteFigureButton = Button(self.frame, text="Delete figure", command=self.deleteFigure, padx=12, pady=12)
        self.deleteFigureButton.grid(row=1, column=0, columnspan=2, sticky="WE")
        self.deleteFigureButton['font'] = self.bigFont
        # Tools
        self.toolsLabel = LabelFrame(self.frame, text=f"Tools")
        self.toolsLabel.grid(row=2, column=0, columnspan=2, sticky="WE")
        self.operationType = StringVar(value="1")
        self.cursorTool = Radiobutton(self.toolsLabel, text="Cursor", value="1", variable=self.operationType, command=self.onToolTypeSelect)
        self.cursorTool.grid(row=0, column=0, sticky="W", columnspan=2)
        self.movementTool = Radiobutton(self.toolsLabel, text="Move", value="2", variable=self.operationType, command=self.onToolTypeSelect)
        self.movementTool.grid(row=1, column=0, sticky="W", columnspan=2)
        self.rotationTool = Radiobutton(self.toolsLabel, text="Rotation", value="3", variable=self.operationType, command=self.onToolTypeSelect)
        self.rotationTool.grid(row=2, column=0, sticky="W", columnspan=2)
        self.scalingTool = Radiobutton(self.toolsLabel, text="Scale", value="4", variable=self.operationType, command=self.onToolTypeSelect)
        self.scalingTool.grid(row=3, column=0, sticky="W", columnspan=2)
        # Parameters Label
        self.parameterLabel = LabelFrame(self.frame)
        self.xVectorLabel = Label(self.parameterLabel, text="X vector")
        self.xVectorLabel['font'] = self.bigFont
        self.yVectorLabel = Label(self.parameterLabel, text="Y vector")
        self.yVectorLabel['font'] = self.bigFont
        self.xVectorEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER)
        self.yVectorEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER)
        self.xPointLabel = Label(self.parameterLabel, text="X start point")
        self.xPointLabel['font'] = self.bigFont
        self.yPointLabel = Label(self.parameterLabel, text="Y start point")
        self.yPointLabel['font'] = self.bigFont

        self.entryXVar = StringVar()
        self.xPointEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER, textvariable=self.entryXVar)
        self.entryXVar.trace_add("write", self.drawOriginPointOfTheCoordinateSystem)
        self.entryYVar = StringVar()
        self.yPointEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER, textvariable=self.entryYVar)
        self.entryYVar.trace_add("write", self.drawOriginPointOfTheCoordinateSystem)

        self.degreeLabel = Label(self.parameterLabel, text="Degree value")
        self.degreeLabel['font'] = self.bigFont
        self.degreeEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validationRangeFromMinus360To360, '%P'), justify=CENTER)
        self.xFactorLabel = Label(self.parameterLabel, text="X percentage")
        self.xFactorLabel['font'] = self.bigFont
        self.yFactorLabel = Label(self.parameterLabel, text="Y percentage")
        self.yFactorLabel['font'] = self.bigFont
        self.xFactorEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER)
        self.yFactorEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validation, '%P'), justify=CENTER)
        self.submitOperationButton = Button(self.parameterLabel, text="Execute", command=lambda: self.doOperation("event", -1), padx=8)
        self.submitOperationButton['font'] = font.Font(size=18, weight="bold")
        # White space to draw Bezier Curve
        self.drawSpace = Canvas(self.root, bg="white")
        self.drawSpace.pack(fill="both", expand=True)
        # Binding of mouse click and drag
        self.drawSpace.bind("<ButtonPress-1>", lambda event: self.doOperation(event, 0))
        self.drawSpace.bind("<B1-Motion>", lambda event: self.doOperation(event, 1))
        self.drawSpace.bind("<ButtonRelease-1>", lambda event: self.doOperation(event, 2))
        self.drawSpace.bind("<ButtonPress-3>", self.drawOriginPointOfTheCoordinateSystemByMouse)
        self.figureEntries = {}
        self.figureVertexes = {}
        self.figureLines = {}
        self.lastFigureNumber = 0
        self.selectedFigure = 0
        self.selectedFigureLabel = None
        self.startX, self.startY = None, None
        self.selectedVertex = None
        self.selected = None
        self.originPointOfTheCoordinateSystem = None

        self.rotationDegree = 0

    def onToolTypeSelect(self):
        operationType = int(self.operationType.get())
        self.updateParameterLabel(operationType)
        self.drawOriginPointOfTheCoordinateSystem(variant=operationType)

    def updateParameterLabel(self, value):
        self.parameterLabel.grid_forget()
        self.xVectorLabel.grid_forget()
        self.xVectorEntry.grid_forget()
        self.yVectorLabel.grid_forget()
        self.yVectorEntry.grid_forget()
        self.xPointLabel.grid_forget()
        self.xPointEntry.grid_forget()
        self.yPointLabel.grid_forget()
        self.yPointEntry.grid_forget()
        self.degreeLabel.grid_forget()
        self.degreeEntry.grid_forget()
        self.xFactorLabel.grid_forget()
        self.xFactorEntry.grid_forget()
        self.yFactorLabel.grid_forget()
        self.yFactorEntry.grid_forget()
        self.submitOperationButton.grid_forget()
        if value == 2:
            self.parameterLabel.grid(row=3, column=0, columnspan=2, sticky="WE")
            self.xVectorLabel.grid(row=0, column=0)
            self.xVectorEntry.grid(row=1, column=0)
            self.yVectorLabel.grid(row=2, column=0)
            self.yVectorEntry.grid(row=3, column=0)
            self.submitOperationButton.grid(row=4, column=0)
        elif value == 3:
            self.parameterLabel.grid(row=3, column=0, columnspan=2, sticky="WE")
            self.xPointLabel.grid(row=0, column=0)
            self.xPointEntry.grid(row=1, column=0)
            self.yPointLabel.grid(row=2, column=0)
            self.yPointEntry.grid(row=3, column=0)
            self.degreeLabel.grid(row=4, column=0)
            self.degreeEntry.grid(row=5, column=0)
            self.submitOperationButton.grid(row=6, column=0)
        elif value == 4:
            self.parameterLabel.grid(row=3, column=0, columnspan=2, sticky="WE")
            self.xPointLabel.grid(row=0, column=0)
            self.xPointEntry.grid(row=1, column=0)
            self.yPointLabel.grid(row=2, column=0)
            self.yPointEntry.grid(row=3, column=0)
            self.xFactorLabel.grid(row=4, column=0)
            self.xFactorEntry.grid(row=5, column=0)
            self.yFactorLabel.grid(row=6, column=0)
            self.yFactorEntry.grid(row=7, column=0)
            self.submitOperationButton.grid(row=8, column=0)

    def doOperation(self, event, value):
        if self.selectedFigure:
            operation = int(self.operationType.get())
            # ic(f"WYkonano operacje {operation} event {event}")
            if operation == 1:
                if value == 0:
                    self.startMoveVertexOrDrawNew(event)
                elif value == 1:
                    self.moveVertexByMouse(event)
                else:
                    self.endMoveVertexByMouse(event)
            elif operation == 2:
                if value == -1:
                    self.moveFigureByParameter()
                elif value == 0:
                    self.startMoveFigureByMouse(event)
                elif value == 1:
                    self.moveFigureByMouse(event)
                else:
                    self.endMoveFigureByMouse(event)
            elif operation == 3:
                if value == -1:
                    self.rotateFigureByParameter()
                elif value == 0:
                    self.startRotateFigureByMouse(event)
                elif value == 1:
                    self.rotateFigureByMouse(event)
                else:
                    self.endRotateFigureByMouse(event)
            elif operation == 4:
                self.scaleFigure()

    def moveFigureByParameter(self):
        if self.xVectorEntry.get() != "" or self.yVectorEntry.get() != "":
            xVector = int(self.xVectorEntry.get()) if self.xVectorEntry.get() != "" else 0
            yVector = int(self.yVectorEntry.get()) if self.yVectorEntry.get() != "" else 0
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                vertex[0] += xVector
                vertex[1] += yVector
                entryX, entryY = entry[0], entry[1]
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    def drawOriginPointOfTheCoordinateSystemByMouse(self, event):
        operation = int(self.operationType.get())
        if operation == 3 or operation == 4:
            if self.originPointOfTheCoordinateSystem:
                self.drawSpace.delete(self.originPointOfTheCoordinateSystem)
            x, y = event.x, event.y
            self.xPointEntry.delete(0, END)
            self.xPointEntry.insert(0, str(x))
            self.yPointEntry.delete(0, END)
            self.yPointEntry.insert(0, str(y))

    def drawOriginPointOfTheCoordinateSystem(self, *args, variant=3):
        ic(self.xPointEntry.get(), self.yPointEntry.get())
        if self.originPointOfTheCoordinateSystem:
            self.drawSpace.delete(self.originPointOfTheCoordinateSystem)
        if (variant == 3 or variant == 4) and self.xPointEntry.get() != "" and self.yPointEntry.get() != "":
            x, y = int(self.xPointEntry.get()), int(self.yPointEntry.get())
            self.originPointOfTheCoordinateSystem = self.drawSpace.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")

    def rotateFigureByParameter(self):
        if self.xPointEntry.get() != "" and self.yPointEntry.get() != "" and self.degreeEntry.get() != "":
            xPoint, yPoint, degree = int(self.xPointEntry.get()), int(self.yPointEntry.get()), int(self.degreeEntry.get())
            degree = radians(degree)
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                oldX, oldY = vertex[0], vertex[1]
                vertex[0] = xPoint + (oldX - xPoint) * cos(degree) - (oldY - yPoint) * sin(degree)
                vertex[1] = yPoint + (oldX - xPoint) * sin(degree) + (oldY - yPoint) * cos(degree)
                ic(vertex[0], vertex[1])
                entryX, entryY = entry[0], entry[1]
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    def scaleFigure(self):
        pass

    def addFigure(self):
        number = self.lastFigureNumber = self.lastFigureNumber + 1
        self.figureEntries[number] = []
        self.figureVertexes[number] = []
        self.figureLines[number] = []
        figureLabel = LabelFrame(self.frame, text=f"Figure {number}", labelanchor="nw")
        figureLabel.grid(row=number+3, column=0, columnspan=2, sticky="WE")
        self.onFigureSelect(figureLabel, number)
        # Frame for vertexes
        vertexesLabel = LabelFrame(figureLabel, text="Vertexes positions", labelanchor="nw")
        vertexesLabel.grid(row=0, column=0, columnspan=4, sticky="WE")
        #Label to add Vertex
        labelAddVertex = Label(figureLabel, text="Add vertex")
        labelAddVertex.grid(row=999, column=0, columnspan=4)
        # X and Y labels
        positionXLabel = Label(figureLabel, text="X", padx=2)
        positionXLabel.grid(row=1000, column=0)
        # positionXLabel['font'] = self.bigFont
        positionYLabel = Label(figureLabel, text="Y", padx=3)
        positionYLabel.grid(row=1000, column=2)
        # positionYLabel['font'] = self.bigFont
        # X and Y entries
        positionXEntry = Entry(figureLabel, justify=CENTER, width=7, validate='all', validatecommand=(self.validation, '%P'))
        positionXEntry.grid(row=1000, column=1)
        positionYEntry = Entry(figureLabel, justify=CENTER, width=7, validate='all', validatecommand=(self.validation, '%P'))
        positionYEntry.grid(row=1000, column=3)
        # Button to add vertex
        addVertexButton = Button(figureLabel, text="Add vertex", command=lambda: self.addVertexByParameters(positionXEntry.get(), positionYEntry.get()))
        addVertexButton.grid(row=1001, column=0, columnspan=4, sticky="WE")
        # addVertexButton['font'] = self.bigFont
        # Bind <Button-1> event to figureLabel
        figureLabel.bind("<Button-1>", lambda event, figureNumber=number: self.onFigureSelect(figureLabel, figureNumber))
        # Bind <Button-1> event to all elements within figureLabel
        for widget in figureLabel.winfo_children():
            widget.bind("<Button-1>", lambda event, figureNumber=number: self.onFigureSelect(figureLabel, figureNumber))

    def onFigureSelect(self, labelFrame, figureNumber):
        if self.selectedFigureLabel:
            self.selectedFigureLabel.config(highlightbackground="SystemButtonFace", highlightcolor="SystemButtonFace")
            self.changeColorOfSelectedFigure()
        labelFrame.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.selectedFigureLabel = labelFrame
        self.selectedFigure = figureNumber
        self.changeColorOfSelectedFigure("lightgreen")

    def changeColorOfSelectedFigure(self, color="black"):
        if self.selectedFigure:
            # ic("Wierzcholki:", self.figureVertexes[self.selectedFigure])
            for vertex in self.figureVertexes[self.selectedFigure]:
                self.drawSpace.itemconfig(vertex[2], fill=color, outline=color)
            # ic("Linie:", self.figureLines[self.selectedFigure])
            for line in self.figureLines[self.selectedFigure]:
                self.drawSpace.itemconfig(line, fill=color)

    def deleteFigure(self):
        if self.selectedFigureLabel:
            self.drawSpace.delete(f"Figure{self.selectedFigure}Line")
            self.drawSpace.delete(f"Vertex{self.selectedFigure}")
            self.figureVertexes.pop(self.selectedFigure)
            self.figureLines.pop(self.selectedFigure)
            self.selectedFigureLabel.destroy()
            self.selectedFigureLabel = None
            self.selectedFigure = 0

    # Moving vertex by mouse
    def startMoveVertexOrDrawNew(self, event):
        if self.selectedFigure:
            x, y = event.x, event.y
            shapes = self.drawSpace.find_overlapping(x, y, x, y)
            selectedVertex = None
            if shapes:
                for shape in shapes:
                    tags = self.drawSpace.gettags(shape)
                    if f"Vertex{self.selectedFigure}" in tags:
                        selectedVertex = shape
                        break
            if selectedVertex:
                # move point
                self.selectedVertex = selectedVertex
            else:
                # draw point
                vertex = self.drawSpace.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill="black", tags=f"Vertex{self.selectedFigure}")
                self.figureVertexes[self.selectedFigure].append([x, y, vertex])
                self.addVertexToFigureLabel(x, y)

    def getVertexByPointIndexInCanvas(self, vertexIndexInCanvas):
        for sub in self.figureVertexes[self.selectedFigure]:
            if sub[2] == vertexIndexInCanvas:
                return sub
        return None

    def moveVertexByMouse(self, event):
        if self.selectedFigure and self.selectedVertex and any(self.selectedVertex == sub[2] for sub in self.figureVertexes[self.selectedFigure]):
            x, y = event.x, event.y
            vertex = self.getVertexByPointIndexInCanvas(self.selectedVertex)
            vertexIndex = self.figureVertexes[self.selectedFigure].index(vertex)
            self.figureVertexes[self.selectedFigure][vertexIndex][0], self.figureVertexes[self.selectedFigure][vertexIndex][1] = x, y
            entryX, entryY = self.figureEntries[self.selectedFigure][vertexIndex][0], self.figureEntries[self.selectedFigure][vertexIndex][1]
            entryX.delete(0, END)
            entryX.insert(0, str(x))
            entryY.delete(0, END)
            entryY.insert(0, str(y))

    def endMoveVertexByMouse(self, event):
        self.selectedVertex = None

    # Moving figure by mouse
    def startMoveFigureByMouse(self, event):
        if self.selectedFigure:
            x, y = event.x, event.y
            ic("START", x, y)
            shapes = self.drawSpace.find_overlapping(x, y, x, y)
            selected = None
            if shapes:
                for shape in shapes:
                    tags = self.drawSpace.gettags(shape)
                    for tag in tags:
                        if f"{self.selectedFigure}" in tag:
                            selected = shape
                            break
            if selected:
                self.startX = x
                self.startY = y
                self.selected = selected

    def moveFigureByMouse(self, event):
        if self.selectedFigure and self.selected:
            x, y = event.x, event.y
            dx, dy = x - self.startX, y - self.startY
            self.startX, self.startY = self.startX + dx, self.startY + dy
            for entry, vertex in zip(self.figureEntries[self.selectedFigure], self.figureVertexes[self.selectedFigure]):
                entryX, entryY = entry[0], entry[1]
                currentX, currentY = int(entryX.get()), int(entryY.get())
                newX, newY = currentX + dx, currentY + dy
                vertex[0], vertex[1] = float(newX), float(newY)
                entryX.delete(0, END)
                entryX.insert(0, str(newX))
                entryY.delete(0, END)
                entryY.insert(0, str(newY))

    def endMoveFigureByMouse(self, event):
        self.selected, self.startX, self.startY = None, None, None

    # Rotating figure by mouse
    def startRotateFigureByMouse(self, event):
        x, y = event.x, event.y
        self.startX = x
        self.startY = y

    def rotateFigureByMouse(self, event):
        if self.selectedFigure and self.xPointEntry.get() != "" and self.yPointEntry.get() != "":
            x, y = event.x, event.y
            # xPoint and yPoint are center of coordinate system
            xPoint, yPoint = float(self.xPointEntry.get()), float(self.yPointEntry.get())
            angleMousePoint = atan2(yPoint - y, xPoint - x)
            angleStartPoint = atan2(yPoint - self.startY, xPoint - self.startX)
            # degree is the difference between angles of previous start to actual mouse point
            degree = angleMousePoint - angleStartPoint
            # Replacing old start position with new start position
            self.startX, self.startY = x, y
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                entryX, entryY = entry[0], entry[1]
                oldX, oldY = vertex[0], vertex[1]
                vertex[0] = xPoint + (oldX - xPoint) * cos(degree) - (oldY - yPoint) * sin(degree)
                vertex[1] = yPoint + (oldX - xPoint) * sin(degree) + (oldY - yPoint) * cos(degree)
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    def endRotateFigureByMouse(self, event):
        self.startX, self.startY = None, None

    def addVertexToFigureLabel(self, x, y):
        if self.selectedFigure and self.selectedFigureLabel:
            figureNumber = self.selectedFigure
            rowIndex = len(self.figureVertexes[figureNumber]) - 1
            myVarX = StringVar()
            entryX = Entry(self.selectedFigureLabel, justify=CENTER, width=8, textvariable=myVarX, validate="all", validatecommand=(self.validation, '%P'))
            myVarX.trace('w', lambda name, index, mode, var=myVarX, figure=figureNumber, row=rowIndex, col=0: self.vertexEntryChanged(figure, row, col, var.get()))
            entryX.grid(row=rowIndex, column=0, columnspan=2, sticky="ew")
            entryX.insert(0, x)
            myVarY = StringVar()
            entryY = Entry(self.selectedFigureLabel, justify=CENTER, width=8, textvariable=myVarY, validate="all", validatecommand=(self.validation, '%P'))
            myVarY.trace('w', lambda name, index, mode, var=myVarY, figure=figureNumber, row=rowIndex, col=1: self.vertexEntryChanged(figure, row, col, var.get()))
            entryY.grid(row=rowIndex, column=2, columnspan=2, sticky="ew")
            entryY.insert(0, y)
            self.figureEntries[self.selectedFigure].append([entryX, entryY])

    def makeLinesOfVertexes(self):
        if self.selectedFigure:
            self.drawSpace.delete(f"Figure{self.selectedFigure}Line")
            self.figureLines[self.selectedFigure].clear()
            for i in range(1, len(self.figureVertexes[self.selectedFigure])):
                x1, y1, _ = self.figureVertexes[self.selectedFigure][i-1]
                x2, y2, _ = self.figureVertexes[self.selectedFigure][i]
                newLine = self.drawSpace.create_line(x1, y1, x2, y2, width=3, tags=f"Figure{self.selectedFigure}Line")
                self.figureLines[self.selectedFigure].append(newLine)
            if len(self.figureVertexes[self.selectedFigure]) >= 3:
                x1, y1, _ = self.figureVertexes[self.selectedFigure][0]
                newLine = self.drawSpace.create_line(x2, y2, x1, y1, width=3, tags=f"Figure{self.selectedFigure}Line")
                self.figureLines[self.selectedFigure].append(newLine)
            self.changeColorOfSelectedFigure("lightgreen")

    def addVertexByParameters(self, x, y):
        if x and y:
            self.startMoveVertexOrDrawNew(EventWithXY(x, y))

    def vertexEntryChanged(self, figureNumber, row, column, value):
        if value:
            if abs(int(value) - self.figureVertexes[figureNumber][row][column]) > 1:
                ic("Zmienionono entry recznie", value, self.figureVertexes[figureNumber][row][column])
                self.figureVertexes[figureNumber][row][column] = float(value)
            self.movePointByParameters(self.figureVertexes[figureNumber][row][2], self.figureVertexes[figureNumber][row][0], self.figureVertexes[figureNumber][row][1])
            self.makeLinesOfVertexes()

    def movePointByParameters(self, itemIndex, newX, newY):
        # ic(itemIndex, newX, newY)
        self.drawSpace.coords(itemIndex, newX - 5, newY - 5, newX + 5, newY + 5)

    @staticmethod
    def validateEntry(P):
        if P == "":
            return True
        try:
            int(P)
            return True
        except ValueError:
            return False

    # @staticmethod
    # def validateEntryFloat(P):
    #     pattern = r'^-?\d*(\.\d{0,3})?$'
    #     if re.match(pattern, P) is not None:
    #         return True
    #     else:
    #         return False

    @staticmethod
    def validateEntryRangeFromMinus360To360(P):
        if P == "":
            return True
        try:
            intP = int(P)
        except ValueError:
            return False
        if -360 <= intP <= 360:
            return True
        return False


class EventWithXY:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
