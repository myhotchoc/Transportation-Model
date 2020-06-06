#table class for transportation model
import tkinter as tk
from tkinter import ttk, Canvas #importing the Tkinter libraries to be used to create the interface
#the Canvas library allows any programmer to create shapes and vector images

class tableClass:
    def __init__(self, rows, columns, factories, warehouses, totalSupply, totalDemand, matrix, entries):
        self.rows = rows
        self.columns = columns
        self.factories = factories
        self.warehouses = warehouses
        self.totalSupply = totalSupply
        self.totalDemand = totalDemand
        self.matrix = matrix
        self.entries = entries
        #initialising all variables needed throughout the class

    def createTable(self):
        if self.totalDemand != self.totalSupply:
            total = self.totalDemand, self.totalSupply
        else:
            total = self.totalSupply #creating variable of total supply/ demand that will be outputted to the interface

        for y in range(self.rows):
            cols = []
            for x in range(self.columns): #loops through the number of rows and columns needed to create the input table for the user
                if y == 0 and x == 0:
                    a = ttk.Label(self.matrix)
                    a["text"] = "Factory|Warehouse" #creating a title for the rows and columns
                    cols.append(None)
                elif y == self.rows-1 and x == self.columns-1:
                    a = ttk.Label(self.matrix)
                    a["text"] = "Total:", total #creating a label for the total supply and demand stated by the user
                    cols.append(None)
                elif x == 0 and y == (self.rows-1):
                    a = ttk.Label(self.matrix)
                    a["text"] = "Demand" #creating a title for the Demand column
                    cols.append(None)
                elif y == 0 and x == self.columns-1:
                    a = ttk.Label(self.matrix)
                    a["text"] = "Supply" #creating a title for the Supply row
                    cols.append(None)
                else:
                    a = ttk.Entry(self.matrix)
                    if y == 0 and x > 0:
                        a.insert(0, "W" + str(x)) #prepopulate cell with label ('W1'/ 'W2' etc) but created so the user can change it
                    elif x == 0 and y > 0:
                        a.insert(0, "F" + str(y)) #prepopulate cell with label ('F1'/ 'W2' etc) but created so the user can change it
                    else:
                        pass
                    cols.append(a)
                a["width"] = 14 #set width of each cell in the input matrix
                a.grid(row = y, column = x) #adding the cell to the Tkinter interface
            self.entries.append(cols) #adding the column created on the corresponding iteration to a single identifier
            #entire table will be stored under 'entries' identifier so it can be referenced to 


class analysisClass:
    def __init__(self, cost, rows, columns, factories, warehouses, totalSupply, totalDemand, entries, method, allocationArray, blankCanvas, degenerate):
        self.cost = cost
        self.rows = rows
        self.columns = columns
        self.factories = factories
        self.warehouses = warehouses
        self.totalSupply = totalSupply
        self.totalDemand = totalDemand
        self.method = method
        self.allocationArray = allocationArray
        self.blankCanvas = blankCanvas
        self.degenerate = degenerate
        self.entries = entries
        #initialises variabales needed wihtin this class

    def calculateTotal(self):
        for x in range(self.factories):
            totalAllocations = 0
            for y in range(self.warehouses):
                if self.allocationArray[x][y] > 0:
                    totalAllocations += self.allocationArray[x][y]
                else:
                    pass
            self.allocationArray[x].append(totalAllocations) #calculates the total allocations made on each row and added to the end of each row of the alllcationArray

        row = [0] * self.columns 
        self.allocationArray.append(row) #adds an row of zeros to the end of allocationArray so it can be edited later on
        total = 0

        y = 0 
        while y < self.warehouses:
            totalAllocations = 0
            for x in range(self.factories):
                if self.allocationArray[x][y] > 0: #going through each column and adding the allocations for that column
                    totalAllocations += self.allocationArray[x][y] #adding each column total so the total allocations made can be calculated
                    total += self.allocationArray[x][y]
                else:
                    pass
            self.allocationArray[-1][y] = totalAllocations #apending the allocations made in the corresponding column to the end of the column
            y += 1

        return total, self.allocationArray #returning the array and total so the appended versoins can be used

    def analysisPage(self):
        self.blankCanvas.create_text(150,10, text = "Using the "+ self.method +":")
        self.blankCanvas.create_text(150,30, text = "A network graph of the different routes taken.", fill = 'grey')
        self.blankCanvas.create_text(150,50, text = "The supplies to be transported are shown.", fill = 'grey')
        self.blankCanvas.create_text(150,80, text = "The total cost for this method is: £" + str(self.cost))
        self.blankCanvas.create_text(500,30, text = "These are the amounts to be transported from the \n specified factories to the specified warehouses", fill = "grey") #outputting this information to the user so they can understand the results

        if self.degenerate: #if degenerate the solution will not be optimised so must let the user know
            self.blankCanvas.create_text(150,65, text = "This is a degenerate solution.", fill = 'red')


    def networkGraph(self):
        nodes = [100, 200, 300, 400, 500, 600] #will be used as constants for the positioning of the graph nodes
        self.allocationArray = balancedChecked(self.totalSupply, self.totalDemand, self. allocationArray) #checks whether or not the supply and demand are equal and if not adapts the allocation array so it is in the correct syntax

        for x in range(self.factories):
            self.blankCanvas.create_oval(70, nodes[x], 100, nodes[x]+30, fill = "#aad6ff") #the coordinates for each node changes because of the for loop, creating a line of nodes
            self.blankCanvas.create_text((85, nodes[x]+15), text="F"+str(x+1)) #creates nodes for all the factories

        for y in range(self.warehouses):
            self.blankCanvas.create_oval(200, nodes[y], 230, nodes[y]+30, fill = "#ffb3ab")
            self.blankCanvas.create_text((215, nodes[y]+15), text="W"+str(y+1)) #creates nodes for all the warehouses

        lineCreated = False #used as a fallback method if the solution has no allocations
        for f in range(len(self.allocationArray)):
            w = 0
            while w < self.warehouses:
                if self.allocationArray[f][w] > 0: #checking each cell to see if an allocation has been made
                    self.blankCanvas.create_line(100,nodes[f]+15,200,nodes[w]+15) #creates a line for an allocation between the corresponding factory (f) and warehouse (w)
                    lineCreated = True 
                else:
                    pass
                w += 1
        if lineCreated == False: #explains why there are no results
            self.blankCanvas.create_text(500,60, text = "The solution is degenerate and unbalanced so there is no solution", fill = "red")
    
    def resultsTable(self):
        xCoOrd = [300,350,400,450,500,550,600,650,700]
        yCoOrd = [100,130,160,190,220,250,280,310,340] #used to refer to as coordinates for the table of allocations

        total, self.allocationArray = self.calculateTotal(self.factories, self.warehouses, self.allocationArray, self.columns) #calculates the total allocations for each row and column and appends it to the allocationArray variable
        self.allocationArray = appendAllocationArray(self.allocationArray, self.columns, self.rows) #adds the row and column labels back in, from the original input matrix
        del self.allocationArray[-1][-1] #removes very last cell as it is replaced in the previous line

        for x in range(self.rows):
            for y in range(self.columns):
                self.blankCanvas.create_rectangle(xCoOrd[y], yCoOrd[x], xCoOrd[y+1], yCoOrd[x+1]) #creates a table made up of rectangles 
                #it is the easiest way to create the table since the Canvas library is in use on this window

        x = 0 
        while x < self.rows:
            for y in range(self.columns):
                if x == self.rows-1 and y == self.columns-1:
                    self.blankCanvas.create_text((xCoOrd[x]+25, yCoOrd[y]+15), text= str(total)) #adds total supply and demand label to the table
                else:
                    self.blankCanvas.create_text((xCoOrd[y]+25, yCoOrd[x]+15), text=str(self.allocationArray[x][y])) #adds the allocations made at all factories/warehouses to the table, if no allocations are made it is shown as 0
            x += 1
"""check if i can change the while loop to a for loop@@@"""
"""check if i can move the functuons into the class"""

"""there is an extra column for some reason but it is needed in some places and not others - must heck side effects of changing in appendAllocationArray"""


def appendAllocationArray(allocationArray, columns, rows):
    label = ["F|W"]
    for q in range(1,columns):
        if q == columns-1:
            label.append("TOTAL")
        else:
            label.append("W" + str(q)) #adding labels for each column to an array
    allocationArray.insert(0, label) #inserting the label array into the allocationArray so the user can understand what each column represents

    for p in range(1, rows):
        if p == rows-1:
            label = "TOTAL"
        else:
            label = 'F'+str(p) 
        allocationArray[p].insert(0, label) #inserting labels for each row to the allocationArray so the user can identify what each cell means
    
    return allocationArray #returning the updated array

def balancedChecked(totalSupply, totalDemand, allocationArray): #to ensure dummy rows/ columns arent counted when creating the network graphs
    if totalDemand > totalSupply:
        del allocationArray[-1] #removing dummy row
    elif totalSupply > totalDemand:
        for j in allocationArray: #removing dummy column
            del j[-1]
    else:
        pass
    return allocationArray #returning updated allocationArray
