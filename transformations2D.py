from tkinter import *
import tkinter.font as font
from icecream import ic
from math import cos, sin, radians, atan2
import re
import pickle
from tkinter.filedialog import asksaveasfilename, askopenfilename


class HomogeneousCoordinates:
    @staticmethod
    def changeCoordinatesToMatrix(x, y):
        return [[x],
                [y],
                [1]]

    @staticmethod
    def translation(P, Tx, Ty):
        Ttxty = [[1, 0, Tx],
                 [0, 1, Ty],
                 [0, 0, 1]]
        resultMatrix = [[0],
                        [0],
                        [0]]
        for i in range(3):
            for j in range(3):
                resultMatrix[i][0] += Ttxty[i][j] * P[j][0]
        return resultMatrix

    @staticmethod
    def rotation(P, alfa):
        R = [[cos(alfa), -sin(alfa), 0],
             [sin(alfa), cos(alfa), 0],
             [0, 0, 1]]
        resultMatrix = [[0],
                        [0],
                        [0]]
        for i in range(3):
            for j in range(3):
                resultMatrix[i][0] += R[i][j] * P[j][0]
        return resultMatrix

    @staticmethod
    def scaling(P, Sx, Sy):
        Ssxsy = [[Sx, 0, 0],
                 [0, Sy, 0],
                 [0, 0, 1]]
        resultMatrix = [[0],
                        [0],
                        [0]]
        for i in range(3):
            for j in range(3):
                resultMatrix[i][0] += Ssxsy[i][j] * P[j][0]
        return resultMatrix


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
        self.frameForFigures = LabelFrame(self.root, padx=0, pady=0, labelanchor="w")
        self.frameForFigures.pack(side="left", fill="both")
        # Validation
        self.validation = (self.frame.register(self.validateEntry))
        self.validationFloat = (self.frame.register(self.validateEntryFloat))
        self.validationRangeFromMinus360To360 = (self.frame.register(self.validateEntryRangeFromMinus360To360))
        # Button to save
        self.saveButton = Button(self.frame, text="Save", command=self.saveState, padx=12, pady=12)
        self.saveButton.grid(row=0, column=0, columnspan=2, sticky="WE")
        self.saveButton['font'] = self.bigFont
        # Button to load
        self.loadButton = Button(self.frame, text="Load", command=self.loadState, padx=12, pady=12)
        self.loadButton.grid(row=1, column=0, columnspan=2, sticky="WE")
        self.loadButton['font'] = self.bigFont
        # Button to add figure
        self.addFigureButton = Button(self.frame, text="Add figure", command=self.addFigure, padx=12, pady=12)
        self.addFigureButton.grid(row=2, column=0, columnspan=2, sticky="WE")
        self.addFigureButton['font'] = self.bigFont
        # Button to delete figure
        self.deleteFigureButton = Button(self.frame, text="Delete figure", command=self.deleteFigure, padx=12, pady=12)
        self.deleteFigureButton.grid(row=3, column=0, columnspan=2, sticky="WE")
        self.deleteFigureButton['font'] = self.bigFont
        # Tools
        self.toolsLabel = LabelFrame(self.frame, text=f"Tools")
        self.toolsLabel.grid(row=4, column=0, columnspan=2, sticky="WE")
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
        self.xRatioLabel = Label(self.parameterLabel, text="X ratio")
        self.xRatioLabel['font'] = self.bigFont
        self.yRatioLabel = Label(self.parameterLabel, text="Y ratio")
        self.yRatioLabel['font'] = self.bigFont
        self.xRatioEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validationFloat, '%P'), justify=CENTER)
        self.yRatioEntry = Entry(self.parameterLabel, validate='all', validatecommand=(self.validationFloat, '%P'), justify=CENTER)
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
        # self.drawSpace.bind("<ButtonPress-2>", self.changeSelectedFigure)
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
        self.errorLabel = None

    def saveState(self):
        filename = asksaveasfilename(initialfile='Untitled.pkl', defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
        if filename is not None:
            state = {
                'figureVertexes': self.figureVertexes,
            }
            try:
                with open(filename, 'wb') as file:
                    pickle.dump(state, file)
            except FileNotFoundError:
                return self.errorPopup("File not found.")
            except Exception as e:
                return self.errorPopup(f"Error loading file: {str(e)}")
            ic(f"Saved to {filename}")

    def loadState(self):
        filename = askopenfilename()
        if filename is not None:
            try:
                with open(filename, 'rb') as file:
                    state = pickle.load(file)
                loadedFigureVertexes = state['figureVertexes']
            except FileNotFoundError:
                return self.errorPopup("File not found.")
            except Exception as e:
                return self.errorPopup(f"Error loading file: {str(e)}")
            self.restoreLayoutFromVertexes(loadedFigureVertexes)

    def restoreLayoutFromVertexes(self, newFigureVertexes):
        self.clearData()
        for figure in newFigureVertexes.values():
            self.selectedFigure, self.selectedFigureLabel = self.addFigure()
            for vertex in figure:
                self.addVertexByParameters(vertex[0], vertex[1])

    def clearData(self):
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
        self.errorLabel = None
        self.drawSpace.delete("all")
        self.frameForFigures.destroy()
        self.frameForFigures = LabelFrame(self.root, padx=0, pady=0, labelanchor="w")
        self.frameForFigures.pack(side="left", fill="both")
        self.drawSpace.pack_forget()
        self.drawSpace.pack(fill="both", expand=True)

    def errorPopup(self, information=None):
        self.errorLabel = Label(Toplevel(), text=information, padx=20, pady=20)
        self.errorLabel.pack(side="top", fill="both", expand=True)

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
        self.xRatioLabel.grid_forget()
        self.xRatioEntry.grid_forget()
        self.yRatioLabel.grid_forget()
        self.yRatioEntry.grid_forget()
        self.submitOperationButton.grid_forget()
        if value == 2:
            self.parameterLabel.grid(row=5, column=0, columnspan=2, sticky="WE")
            self.xVectorLabel.grid(row=0, column=0)
            self.xVectorEntry.grid(row=1, column=0)
            self.yVectorLabel.grid(row=2, column=0)
            self.yVectorEntry.grid(row=3, column=0)
            self.submitOperationButton.grid(row=4, column=0)
        elif value == 3:
            self.parameterLabel.grid(row=5, column=0, columnspan=2, sticky="WE")
            self.xPointLabel.grid(row=0, column=0)
            self.xPointEntry.grid(row=1, column=0)
            self.yPointLabel.grid(row=2, column=0)
            self.yPointEntry.grid(row=3, column=0)
            self.degreeLabel.grid(row=4, column=0)
            self.degreeEntry.grid(row=5, column=0)
            self.submitOperationButton.grid(row=6, column=0)
        elif value == 4:
            self.parameterLabel.grid(row=5, column=0, columnspan=2, sticky="WE")
            self.xPointLabel.grid(row=0, column=0)
            self.xPointEntry.grid(row=1, column=0)
            self.yPointLabel.grid(row=2, column=0)
            self.yPointEntry.grid(row=3, column=0)
            self.xRatioLabel.grid(row=4, column=0)
            self.xRatioEntry.grid(row=5, column=0)
            self.yRatioLabel.grid(row=6, column=0)
            self.yRatioEntry.grid(row=7, column=0)
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
                if value == -1:
                    self.scaleFigureByParameter()
                elif value == 0:
                    self.startScaleFigureByMouse(event)
                elif value == 1:
                    self.scaleFigureByMouse(event)
                else:
                    self.endScaleFigureByMouse(event)

    def moveFigureByParameter(self):
        if self.xVectorEntry.get() != "" or self.yVectorEntry.get() != "":
            xVector = int(self.xVectorEntry.get()) if self.xVectorEntry.get() != "" else 0
            yVector = int(self.yVectorEntry.get()) if self.yVectorEntry.get() != "" else 0
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                P = HomogeneousCoordinates.changeCoordinatesToMatrix(vertex[0], vertex[1])
                Pprim = HomogeneousCoordinates.translation(P, xVector, yVector)
                vertex[0], vertex[1] = Pprim[0][0], Pprim[1][0]
                entryX, entryY = entry[0], entry[1]
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    # version without use of  Homogeneous Coordinates
    # def moveFigureByParameter(self):
    #     if self.xVectorEntry.get() != "" or self.yVectorEntry.get() != "":
    #         xVector = int(self.xVectorEntry.get()) if self.xVectorEntry.get() != "" else 0
    #         yVector = int(self.yVectorEntry.get()) if self.yVectorEntry.get() != "" else 0
    #         for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
    #             vertex[0] += xVector
    #             vertex[1] += yVector
    #             entryX, entryY = entry[0], entry[1]
    #             entryX.delete(0, END)
    #             entryX.insert(0, str(round(vertex[0])))
    #             entryY.delete(0, END)
    #             entryY.insert(0, str(round(vertex[1])))

    def rotateFigureByParameter(self):
        if self.degreeEntry.get() != "":
            xPoint = int(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
            yPoint = int(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
            degree = int(self.degreeEntry.get())
            degree = radians(degree)
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                P = HomogeneousCoordinates.changeCoordinatesToMatrix(vertex[0], vertex[1])
                # przesuniecie do wspolrzednych (0, 0)
                P = HomogeneousCoordinates.translation(P, -xPoint, -yPoint)
                # obrocenie
                Pprim = HomogeneousCoordinates.rotation(P, degree)
                # przesuniecie z powrotem
                Pprim = HomogeneousCoordinates.translation(Pprim, xPoint, yPoint)
                vertex[0], vertex[1] = Pprim[0][0], Pprim[1][0]
                entryX, entryY = entry[0], entry[1]
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    # version without use of  Homogeneous Coordinates
    # def rotateFigureByParameter(self):
    #     if self.degreeEntry.get() != "":
    #         xPoint = int(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
    #         yPoint = int(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
    #         degree = int(self.degreeEntry.get())
    #         degree = radians(degree)
    #         for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
    #             oldX, oldY = vertex[0], vertex[1]
    #             vertex[0] = xPoint + (oldX - xPoint) * cos(degree) - (oldY - yPoint) * sin(degree)
    #             vertex[1] = yPoint + (oldX - xPoint) * sin(degree) + (oldY - yPoint) * cos(degree)
    #             entryX, entryY = entry[0], entry[1]
    #             entryX.delete(0, END)
    #             entryX.insert(0, str(round(vertex[0])))
    #             entryY.delete(0, END)
    #             entryY.insert(0, str(round(vertex[1])))

    def scaleFigureByParameter(self):
        if self.xRatioEntry.get() != "" or self.yRatioEntry.get() != "":
            xPoint = int(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
            yPoint = int(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
            xRatio = float(self.xRatioEntry.get()) if self.xRatioEntry.get() != "" else 1
            yRatio = float(self.yRatioEntry.get()) if self.yRatioEntry.get() != "" else 1
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                P = HomogeneousCoordinates.changeCoordinatesToMatrix(vertex[0], vertex[1])
                # przesuniecie do wspolrzednych (0, 0)
                P = HomogeneousCoordinates.translation(P, -xPoint, -yPoint)
                # przeskalowanie
                Pprim = HomogeneousCoordinates.scaling(P, xRatio, yRatio)
                # przesuniecie z powrotem
                Pprim = HomogeneousCoordinates.translation(Pprim, xPoint, yPoint)
                vertex[0], vertex[1] = Pprim[0][0], Pprim[1][0]
                entryX, entryY = entry[0], entry[1]
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))

    # version without use of  Homogeneous Coordinates
    # def scaleFigureByParameter(self):
    #     if self.xRatioEntry.get() != "" or self.yRatioEntry.get() != "":
    #         xPoint = int(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
    #         yPoint = int(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
    #         xRatio = float(self.xRatioEntry.get()) if self.xRatioEntry.get() != "" else 1
    #         yRatio = float(self.yRatioEntry.get()) if self.yRatioEntry.get() != "" else 1
    #         for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
    #             vertex[0] = xPoint + (vertex[0] - xPoint) * xRatio
    #             vertex[1] = yPoint + (vertex[1] - yPoint) * yRatio
    #             entryX, entryY = entry[0], entry[1]
    #             entryX.delete(0, END)
    #             entryX.insert(0, str(round(vertex[0])))
    #             entryY.delete(0, END)
    #             entryY.insert(0, str(round(vertex[1])))

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
        # ic(self.xPointEntry.get(), self.yPointEntry.get())
        if self.originPointOfTheCoordinateSystem:
            self.drawSpace.delete(self.originPointOfTheCoordinateSystem)
        if (variant == 3 or variant == 4) and self.xPointEntry.get() != "" and self.yPointEntry.get() != "":
            x, y = int(self.xPointEntry.get()), int(self.yPointEntry.get())
            self.originPointOfTheCoordinateSystem = self.drawSpace.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")

    def addFigure(self):
        number = self.lastFigureNumber = self.lastFigureNumber + 1
        self.figureEntries[number] = []
        self.figureVertexes[number] = []
        self.figureLines[number] = []
        figureLabel = LabelFrame(self.frameForFigures, text=f"Figure {number}", labelanchor="nw")
        figureLabel.grid(row=number, column=0, sticky="WE")
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
        return number, figureLabel

    def onFigureSelect(self, labelFrame, figureNumber):
        if self.selectedFigureLabel:
            self.selectedFigureLabel.config(highlightbackground="SystemButtonFace", highlightcolor="SystemButtonFace")
            self.changeColorOfSelectedFigure()
        labelFrame.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.selectedFigureLabel = labelFrame
        self.selectedFigure = figureNumber
        self.changeColorOfSelectedFigure("lightgreen")

    # def findFigureWhichItBelong(self, value):
    #     for figureNumber in self.figureVertexes:
    #         for vertex in self.figureVertexes[figureNumber]:
    #             if vertex == value:
    #                 return figureNumber
    #         for line in self.figureLines[figureNumber]:
    #             if line == value:
    #                 return figureNumber
    #     return None
    #
    # def changeSelectedFigure(self, event):
    #     x, y = event.x, event.y
    #     shapes = self.drawSpace.find_overlapping(x, y, x, y)
    #     if shapes:
    #         ic(shapes)
    #         self.selectedFigure = self.findFigureWhichItBelong(shapes[-1])
    #         ic(self.selectedFigure)

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

    # Mowing or drawing single vertex
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
        if self.selectedFigure:
            x, y = event.x, event.y
            # xPoint and yPoint are center of coordinate system
            xPoint = float(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
            yPoint = float(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
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

    # Scaling figure by mouse
    def startScaleFigureByMouse(self, event):
        x, y = event.x, event.y
        self.startX = x
        self.startY = y

    def scaleFigureByMouse(self, event):
        if self.selectedFigure:
            x, y = event.x, event.y
            # xPoint and yPoint are center of coordinate system
            xPoint = float(self.xPointEntry.get()) if self.xPointEntry.get() != "" else 0
            yPoint = float(self.yPointEntry.get()) if self.yPointEntry.get() != "" else 0
            if xPoint == x or yPoint == y:
                ic("Center = 0", xPoint, x, yPoint, y)
                return
            for vertex, entry in zip(self.figureVertexes[self.selectedFigure], self.figureEntries[self.selectedFigure]):
                entryX, entryY = entry[0], entry[1]
                vertex[0] = xPoint + (vertex[0] - xPoint) * ((xPoint - x) / (xPoint - self.startX))
                vertex[1] = yPoint + (vertex[1] - yPoint) * ((yPoint - y) / (yPoint - self.startY))
                entryX.delete(0, END)
                entryX.insert(0, str(round(vertex[0])))
                entryY.delete(0, END)
                entryY.insert(0, str(round(vertex[1])))
            # Replacing old start position with new start position
            self.startX, self.startY = x, y

    def endScaleFigureByMouse(self, event):
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

    @staticmethod
    def validateEntryFloat(P):
        pattern = r'^-?\d*(\.\d*)?$'
        if re.match(pattern, P) is not None:
            return True
        else:
            return False

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
