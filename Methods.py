#transportation problem
import tkinter as tk
from tkinter import ttk, messagebox, Canvas 
#used to create the user interface
import math
from math import inf 
#used as a comparison value
import copy
from copy import deepcopy  
#used to copy the data matrices so they can be manipulated whilst keeping an original copy
import tableClass 
#written on a seprate program to make it easier to maintain
from tableClass import tableClass, analysisClass 
#used to create the interface for both inputs and results


root = tk.Tk() #creating an instance of Tk so my code can be interpreted
root.title("Transportation Model") 
#it is a global variable because it is used in functions that are called by other functions
#this avoids passing paramters into functions that do not use them


def validateMainWindow(factories, warehouses, totalDemand, totalSupply, window): 
    #validates all data inputs
    #only shows the user one error at a time if there are multiple, so they are not overloaded with information 
    if factories < 0 or warehouses < 0 or totalDemand < 0 or totalSupply < 0:
        messagebox.showerror(title = "ERROR", message = "You cannot have negative values.")
        window.destroy() #stops the input window from opening
    elif factories == 0 or warehouses == 0: #checks inputs are valid for the methods
        messagebox.showerror(title = "ERROR", message = "There must be at least 2 factories and 2 warehouses.")
        window.destroy()
    elif factories == 1 or warehouses == 1: 
        messagebox.showerror(title = "ERROR", message = "There must be at least 2 factories and 2 warehouses. \nIf there is only 1 factory or 1 warehouse, then all items are sent from/ delivered to that factory/ warehouse.")
        window.destroy()
    elif totalDemand < warehouses or totalSupply < factories: #algorithms will not work unless these conditions are met
        messagebox.showerror(title = "ERROR", message = "You must have at least " + str(factories) + " supply and " + str(warehouses) + " demand.")
        window.destroy()
    elif factories > 6 or warehouses > 6: #must limit size of table in order to reduce time taken for program to run
        messagebox.showerror(title = "ERROR", message = "The maximum number of factories is 6, maximum number of warehouses is 6.") 
    else:
        pass

def matrixTable(factories, warehouses, totalSupply, totalDemand):
    #collects data needed to create the entry matrix and then creates the matrix
    entries = [] #this is where the user's data will be stored

    window = tk.Toplevel(root) #creating a new window
    window.title("Transportation Model")
    matrix = tk.Frame(window) #creates a placehold where the input matrix will be
    matrix.grid(row = 0, column = 0) 
    #places the widget onto an the interface in a specific place

    factories = factories.get()
    warehouses = warehouses.get()
    totalSupply = totalSupply.get()
    totalDemand = totalDemand.get() 
    #collects the information inputted by the user on the interface

    try:
        factories = int(factories)
        warehouses = int(warehouses)
        totalSupply = int(totalSupply)
        totalDemand = int(totalDemand) 
        #error checking that the user has inputted an item of data and it is a number
    except:
        messagebox.showerror(title = "ERROR", message = "You must enter integer numbers.") 
        #shows user suitable message if invalid input
        window.destroy() #stops input window opening

    validateMainWindow(factories, warehouses, totalDemand, totalSupply, window)
    #runs other error checking conditions

    rows = factories + 2 
    columns = warehouses + 2 #used to create layout of input matrix
    tc = tableClass(rows, columns, factories, warehouses, totalSupply, totalDemand, matrix, entries) 
    #creates an instance of a class 
    tc.createTable() #calls a method of the tableClass, which creates the input matrix
    menuOptions(window, matrix, rows, columns, entries, totalSupply, totalDemand, factories, warehouses) 
    #calls next function to be executed

def menuOptions(window, matrix, rows, columns, entries, totalSupply, totalDemand, factories, warehouses):
    #creates the menu options to be displayed
    options = tk.Frame(window)
    options.grid(row = 0, column = 1) #creates new placehold where the menu will be shown

    methodMenu = ttk.Menubutton(options, text = "Methods") #creates initial button for the methods
    methodMenu.menu = tk.Menu(methodMenu) #initialises the menu widget
    methodMenu.menu["title"] = "Methods"
    methodMenu["menu"]= methodMenu.menu #sets the property of menu button so it is associated with the method menu
    ##found on:
    ##https://www.tutorialspoint.com/python3/tk_menubutton.htm

    methodMenu.menu.add_command(label = "Least Cost", command = lambda: leastCost(entries, rows, columns, totalSupply, totalDemand , factories, warehouses, window))
    methodMenu.menu.add_command(label = "Vogel's Approx.", command = lambda: vogelsApprox(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window))
    methodMenu.menu.add_command(label = "North West Corner", command = lambda: northWestCorner(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window, matrix))
    methodMenu.grid(row = 0, column = 1, sticky = "N", padx = 5, pady = 5)
    #calling selected 'method' if user clicks on one of the menu options

    helpChoices = tk.Frame(window) 
    helpChoices.grid(row = 0, column = 2)

    helpMenu = ttk.Menubutton(helpChoices, text = "Help")
    helpMenu.menu = tk.Menu(helpMenu)
    helpMenu.menu["title"] = "Help"
    helpMenu["menu"] = helpMenu.menu

    helpMenu.menu.add_command(label = "Matrix Help", command = lambda: helpMatrix())
    helpMenu.menu.add_command(label = "Methods Help", command = lambda: helpMethods())
    helpMenu.grid(row = 0, column = 2)
    #creates another drop down menu widget with extra infromation to understand the interface
    

def validateInputs(rawData, rows, columns, factories, warehouses, window, totalSupply, totalDemand):
    #validates data entered into the entry matrix
    totalZero = 0 #used to check if allocationarray is empty
    totalValue = 0 #used to check if data is all the same
    matrixSupply = 0 
    #used to check if the total supply entered is equal to the one stated in the first window 
    matrixDemand = 0
    #used to check if the total demand inputted is the same as in the first window 
    for i in range (factories):
        for j in range(warehouses):
            if rawData[i][j] == 0:
                totalZero += 1 
                #incrementing the count by 1 if an input is zero
                #used for validation of inputs later
            elif rawData[i][j] == rawData[0][0]:
                totalValue += 1 
                #checking if an input is the same as the first piece of data entered
                #used for validation
            else:
                pass

    if totalSupply == totalDemand:
        Factories = factories + 1
        Warehouses = warehouses + 1
    elif totalSupply < totalDemand: 
        Factories = factories #ensures dummy data is ignored in final solution
        Warehouses = warehouses + 1
    else:
        Factories = factories + 1
        Warehouses = warehouses
        #finding the number of rows/columns to be included when adding total demand/supply

    for x in range(Factories):
        matrixSupply += rawData[x][-1] 
        #adding up all supplies entered in the input table
    for y in range(Warehouses):
        matrixDemand += rawData[-1][y] 
        #adding up all demands entered in the input table

    
    if matrixSupply != totalSupply: 
        #ensuring data in the entry matrix matches the data entered in the first window
        messagebox.showerror(title = "ERROR", message = "Your supplies do not add up to the total you entered.")
        return False
    elif matrixDemand != totalDemand:
        messagebox.showerror(title = "ERROR", message = "Your demands do not add up to the total you entered.")
        return False
    else:
        pass

    if totalZero == (factories*warehouses): 
        #ensuring the user hasnt entered only zeros
        messagebox.showerror(title = "ERROR", message = "You must enter several costs above zero or all routes will be free, so there is no optimum solution.")
        return False
    elif totalValue == (factories*warehouses): 
        #do not need to run algorithm if the cost is the same everywhere
        #it is very unlikely for this to happen
        messagebox.showerror(title = "ERROR", message = "When all values are the same, there is no optimal solution, all routes will have the same outcome.")
        return False
    else:
        return True
    #due to the way tkinter works, i cannot validate this data until the user has chosen a method
    #so this validation cannot be executed at the same time as any previous error checks

def collectData(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window):
    #collects the data entered in the matrix on the interface 
    data = [] #used to collect data inputted by user
    allocationArray = [] #will be used to create layout of matrix

    for i in range(rows):
        row = [None] * columns 
        #creates array of empty cells- to create intital structure of the data array
        data.append(row)
        if i > 0 and i < rows-1:
            allocationArray.append([0] * (warehouses)) 
            #creates array of zeros for initial structure of the allocation array
        for j in range(columns):
            if entries[i][j] is not None and entries[i][j].get(): 
                #if a cell's value is set to None it's value is added later 
                #the user wasnt allowed to enter data into these cells
                if i > 0 and j > 0:
                    try:
                        data[i][j] = int(entries[i][j].get()) 
                        #tries to collect integer data input by the user from the interface
                        if data[i][j] < 0:
                            #you cannot have negative costs, so if the user enters them an appropriate error message will be shown
                            messagebox.showerror(title = "ERROR", message = "You must only enter numbers above zero.")
                            return data, rows, columns, allocationArray, False 
                            #False will stop the next part of the program running
                        else:
                            pass
                    except:
                        messagebox.showerror(title = "ERROR", message = "You must only enter whole numbers for the costs, supply and demand.") 
                        #validates the user input and displays appropriate error if incorrect
                        return data, rows, columns, allocationArray, False 
                else:
                    data[i][j] = str(entries[i][j].get()) 
                    #if it is in the first row or column the value is stored as a string as it represent the names of the factories and warehouses
            else:
                if entries[i][j] is not None and len(entries[i][j].get()) == 0:
                    messagebox.showerror(title = "ERROR", message = "You must enter an integer value into every empty cell.")
                    return data, rows, columns, allocationArray, False
                else:
                    data[i][j] = 0 
                    #changes values not inputted to zero ie, the values in the table that were not avliable for the user to edit

    if totalDemand < totalSupply: 
        #creating a dummy column so the algorithms can be implemented as the current data is unbalanced
        columns += 1
        balance = totalSupply - totalDemand #to be placed in the dummy column 
        for q in range(rows):
            data[q].append(data[q][-1]) 
            data[q][-2] = 0 
            #moving the demands column across a column, and inserting a column of zeros where the demands column previously was
            #the column of zeros is to be used as a dummy column
        for p in range(factories):
            allocationArray[p].append(allocationArray[p][-1]) 
            #adding another column of zeros to the array of zeros
        data[-1][-2] = balance 
        #adding the value needed to balance supply and demand to the dummy column 
    elif totalSupply < totalDemand: 
        #creating a dummy row for unbalanced matrices
        rows += 1
        balance = totalDemand - totalSupply
        demands = deepcopy(data[-1])  
        data.append(demands) 
        data[-2] = [0] * columns 
        #creating two duplicate rows of the demands and replacing the first row with zeros
        #this will be the dummy row
        data[-2][-1] = balance 
        #changing the final demand column to the value needed to balance supply and demand
        lastRow = deepcopy(allocationArray[-1]) 
        allocationArray.append(lastRow) 
        #adding the row of zeros on to the allocation array to act as a dummy row 
    else:
        pass 
        #if the supply and demand are equal, the matrix is balanced and no changes need to be made

    rawData = deepcopy(data) 
    #the copy will be used to create a matrix without the row and column labels

    del rawData[0] #removes first row of warehouse labels
    for j in rawData: #removes factory labels
        del j[0]

    run = validateInputs(rawData, rows, columns, factories, warehouses, window, totalSupply, totalDemand) 
    #check all inputs are valid so there will not be any errors later on
    return rawData, rows, columns, allocationArray, run
    #returns all updated variables to be used in the method algorithms

def identicalMatrices(factories, warehouses, allocationArray, finalAllocations): 
    #checking if the original solution is identical to the optimal solution
    #this is possible due to the way the stepping stone algorithm works
    del finalAllocations[0] 
    for j in finalAllocations:
        del j[0]
    #the labels were added to the finalAllocations array, so must be removed before comparison
    count = 0 
    #used to keep track of how many cells are identical
    for x in range(factories):
        for y in range(warehouses): 
            #loops through both matrices to compare values
            if allocationArray[x][y] == finalAllocations[x][y]:
                count += 1 
                #if the cells are identical the count is incremented by 1
            else:
                pass
    if count == factories*warehouses: 
        #if all cells are identical
        return True
    else:
        return False #they are not identical

def costCalculate(factories, warehouses, costArray, allocationArray):
    #calculates the overall cost of a solution 
    cost = 0
    for y in range(factories):
        for x in range(warehouses):
            if allocationArray[y][x] > 0: 
                #loops through the allocation array and finds where an allocation has been made
                cost += allocationArray[y][x] * costArray[y][x] 
                #multiplies the cost per unit by the number of allocations made
                #adds the costs of all allocations together to find the overall cost
    return cost

def resultsWindow(cost, method, rows, columns, factories, warehouses, totalSupply, totalDemand, entries, finalAllocations, degenerate):
    #creates a results page for the data passed to the function
    windowPage = tk.Tk() 
    #creates an instance of Tk to create another window
    #this will be separate to the other windows so cannot be closed using the same command
    windowPage.title(method) 
    #shows the user which method the results are for
    blankCanvas = Canvas(windowPage, width = 700, height = 650) 
    #uses the Tkinter Canvas widgit so the graphs can be drawn 
    blankCanvas.grid(row = 0, column = 0) 
    analysis = analysisClass(cost, rows, columns, factories, warehouses, totalSupply, totalDemand, method, finalAllocations, blankCanvas, degenerate)
     #creates an instance of the analysisClass so the methods can be called
    analysis.analysisPage() 
    #creates an output for all written information to go onto the results page
    analysis.networkGraph() 
    #creates the network graph for the particular instance
    analysis.resultsTable() 
    #creates a table of all the allocations made 

def numLocationsUsed(factories, warehouses, allocationArray):
    #calculates the number of locations where allocations have been made
    locations = 0 
    #reset every time the function is called
    for x in range(factories):
        for y in range(warehouses):
            if allocationArray[x][y] > 0: 
            #iterates through the allocation array and counts the number of places where allocations were made
                locations += 1
    return locations
    #returns the number counted

def originalSolution(root, window, factories, warehouses, costArray, allocationArray, rows, columns, totalSupply, totalDemand, entries, degenerate, method):
    #creates a window showing the initial feasible solution
    solutionWindow = tk.Toplevel(root) 
    #creates the window
    solutionWindow.title("Original Solution")
    initialSolutionTable = tk.Frame(window) 
    initialSolutionTable.grid(row = 0, column = 0)
    #creates a placehold for the initial solution table

    blankCanvas = Canvas(solutionWindow, width = 700, height = 650) 
    #uses the Tkinter library Canvas, so the graphs can be drawn 
    blankCanvas.grid(row = 0, column = 0) 
    
    if isinstance(allocationArray[1][0], str):
        #checks if the allocation array has labels for the rows and columns
        del allocationArray[0] 
        #removes first row of warehouse labels
        for j in allocationArray: #removes factory labels
            del j[0]

    cost = costCalculate(factories, warehouses, costArray, allocationArray)
    #calculates the cost of the initial solution
    initialSolution = analysisClass(cost, rows, columns, factories, warehouses, totalSupply, totalDemand, method, allocationArray, blankCanvas, False)
    #creates an instance of the class so the methods can be called
    initialSolution.analysisPage()
    initialSolution.networkGraph() 
    initialSolution.resultsTable()
    #produces the results page with all the information on it for the original solution

def northWestCorner(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window, matrix):
    rawData, rows, columns, allocationArray, run = collectData(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window) 
    #obtains data from the input page to be used in the algorithm
    if run == False:
        return  
        #to stop function running any more of the algorithm- if the user's data is invalid
        
    northWCAllocations = deepcopy(allocationArray) 
    #taking a copy of the allocation array so it can be manipulated whilst keeping an original copy
    costArray = deepcopy(rawData)

    #rows is x, columns is y
    y = 0 
    x = 0 
    #sets inital cell reference
    supply = rawData[x][-1] 
    #calculates supply for current factory
    allocations = 0 
    #used to count the total allocations made as the algorithm runs, used as a condition for the execution of the algorithm 
    demand = rawData[-1][y] 
    #calculates demand for current warehouse

    while not(allocations == totalSupply) and not(allocations == totalDemand): 
        #code is run until all possible allocations have been made
        if demand == supply:
            northWCAllocations[x][y] = demand 
            #demand and supply are balanced so the maximum allocations can be made to the current cell
            allocations += supply
            y += 1 
            x += 1
            #no more allocations possible for the current row or column, so x and y are both incremented
            supply = rawData[x][-1] 
            demand = rawData[-1][y] #the supply and demand of the next cell are found and stored

        elif demand < supply: 
            northWCAllocations[x][y] = demand 
            #demand is smaller than supply, so the maximum allocations to be made will be the demand value
            allocations += demand
            supply -= demand #the remaining supply is calculated
            y += 1 
            #there is supply remaining so another allocation possible so x stays the same
            demand = rawData[-1][y] #the demand of the next cell is found

        else: 
            northWCAllocations[x][y] = supply 
            #the supply is larger than demand, so the maximum allocations possible will be the supply value
            demand -= supply
             #the remaining demand is calculated
            allocations += supply 
            #the allocations made are added to the running total
            x += 1
            #there is no more suuply on the current row, so the next cell will be on the row below
            supply = rawData[x][-1] #the new supply is stored

    allocationArray = deepcopy(northWCAllocations)

    if totalDemand == totalSupply:
        cost = costCalculate(factories, warehouses, costArray, allocationArray) 
        #calculating cost of initial feasible solution
    elif totalDemand > totalSupply:
        rows -= 1 
        #not taking into account the dummy cells as they were added for the syntax of the algorithm
        cost = costCalculate(factories, warehouses, costArray, allocationArray)
    else:
        columns -= 1
        cost = costCalculate(factories, warehouses, costArray, allocationArray)

    
    allocations = numLocationsUsed(factories, warehouses, allocationArray) 
    #returns the number of places where allocations are made in the initial feasible solution

    finalAllocations, cost, degenerate = steppingStone(rows, columns, window, factories, warehouses, allocationArray, rawData, costArray, allocations, totalSupply, totalDemand) 
    #optimisation algorithm executed on the initial feasible solution

    method = "North West Corner"
     #used as a parameter in the results function
    if finalAllocations == None:
        finalAllocations = allocationArray 
        #original solution used if optimisation algorithm cannot be executed
    if cost == None:
        cost = costCalculate(factories, warehouses, costArray, allocationArray) 
        #cost of original solution needs to be recalculated if the optimisation algorithm was not executed fullly ie, because the solution is degenerate

    original = messagebox.askyesno(title = "Results", message = "Would you like to see the original solution as well as the optimised solution?")
    resultsWindow(cost, method, rows, columns, factories, warehouses, totalSupply, totalDemand, entries, finalAllocations, degenerate) 
    #results page is called once final solution has been calculated to show the user the results
    if original: 
        #the initial feasible solution is shown on a new window if the user wants to see it
        identical = identicalMatrices(factories, warehouses, allocationArray, finalAllocations) 
        #returns whether or not the original and optimal solution are the same
        if degenerate: 
            messagebox.showinfo(title = "Original solution", message = "The solution is degenerate so the original solution is the same as the optimum solution.")
        elif identical: 
            #if the matrices are the same, it only needs to be shown once 
            messagebox.showinfo(title = "Original Solution", message = "The original solution and optimal solution are the same.")
        else:
            originalSolution(root, window, factories, warehouses, costArray, allocationArray, rows, columns, totalSupply, totalDemand, entries, degenerate, method)
    else:
        pass
        
def leastCost(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window):
    rawData, rows, columns, allocationArray, run = collectData(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window) 
    #collecting data from user input
    if run == False:
        return 
        #algorithm will not run if the input matrix is invalid

    allocations = 0 
    #used as a condition as to whether or not the algorithm is executed
    data=rawData
    costArray = deepcopy(data) 
    #the data array is edited in this algorithm so a copy must be taken in order to be used later on
    columns -= 1
    rows -= 1 
    #algorithm doesn't take into account the supply and demand row/ column when finding the lowest cost

    if totalDemand < totalSupply: 
        #finds the total allocations that will be made by using the highest value from the supply and demand
        totalAllocationsNeeded = totalSupply
    else:
        totalAllocationsNeeded = totalDemand

    while allocations < totalAllocationsNeeded: 
        #algorithm will run until all allocations possible have been made
        value = inf 
        #used as an initial comparison to find the lowest value in the input matrix
        for x in range(rows-1):
            for y in range(columns-1):
                if data[x][y] < value: 
                    #iterates through matrix and compares every cost to the value variable
                    xIndex = x 
                    #if a cost lower than 'value' is found, the coordinates of the lower value are stored 
                    yIndex = y
                    value = data[x][y] 
                    #the lower value becomes the new comparison value
                elif data[x][y] == value: 
                    if data[x][y] != inf:
                        #if the two comparison values are both infinte, no changes need to be made as one value is not lower than the other
                        currentSupply = data[xIndex][-1]
                        currentDemand = data[-1][yIndex] 
                        #finds the supply and demand of the lowest value
                        newSupply = data[x][-1]
                        newDemand = data[-1][y] 
                        #finds the supply and demand of the same value but in a different cell

                        if newSupply > currentSupply: 
                            #if more items can be moved then the new cell location should be stored instead of the current one
                            xIndex = x
                            yIndex = y
                        elif newDemand > currentDemand: 
                            #if the above conditions aren't met, but the new cell location has a larger demand, then the new cell location should be stored instead of the current one
                                xIndex = x
                                yIndex = y
                        else:
                            pass
                    else:
                        pass
                else:
                    pass 
                    #if these conditions are not met, no changes will need to be made

        supply = data[xIndex][columns-1]
        demand = data[-1][yIndex] 
        #finds the supply and demand of the cell with the lowest cost

        if supply == demand:
            allocationArray[xIndex][yIndex] = demand 
            #using the supply/ demand constraint to calculate the maximum allocations that can be made
            allocations += supply 
            #adding the allocations made to the total allocation count
            for x in range(rows-1):
                data[x][yIndex] = inf
            for y in range(columns-1):
                data[xIndex][y] = inf
                #changing the row and columns of the cell where the allocation was made to infinte as no more allocations can be made 
                #by changing them to infinite, the costs will no longer be compared when finding the lowest cost
            data[xIndex][-1] = 0
            data[-1][yIndex] = 0 
            #changing the supply and demand of the row and column to zero as no more items need to be dispensed/ allocated

        elif demand < supply: 
            allocationArray[xIndex][yIndex] = demand 
            #the demand is lower so that is the maximum number of allocations that can be made
            allocations += demand
            supply -= demand 
            #there will still be supply remaining, so this must be calculated and updated in the data array
            for x in range(rows-1):
                data[x][yIndex] = inf 
                #all demands have been filled so the column of the allocation cell cannot be used as possible allocation locations
            data[-1][yIndex] = 0 
            #changing the demand to show it has all been used
            data[xIndex][-1] = supply 
            #updating the supply requirements so allocations can be made

        else:
            allocationArray[xIndex][yIndex] = supply
             #the supply is lower than demand if the code is in this if statment
            demand -= supply 
            #the supply will all be used up, leaving some demand at the current warehouse
            allocations += supply
            data[xIndex][-1] = 0 
            data[-1][yIndex] = demand 
            #updating the demand in the data array to ensure allocations are made
            for y in range(columns-1):
                data[xIndex][y] = inf 
                #all supply at this factory has been used so the row can no longer be used to make allocations

    rows += 1 
    columns += 1 
    #so the costCalculate function runs through the entire matrix

    if totalDemand == totalSupply:
        cost = costCalculate(factories, warehouses, costArray, allocationArray)
    elif totalDemand > totalSupply:
        rows -= 1 
        #not taking into account the dummy column when calculating cost
        cost = costCalculate(factories, warehouses, costArray, allocationArray)
    else:
        columns -= 1 
        #not taking into account the dummy row
        cost = costCalculate(factories, warehouses, costArray, allocationArray)

    rawData = deepcopy(costArray) 
    #the rawData array was changed so a copy of the original data array must be taken in order to be used later on
    allocations = numLocationsUsed(factories, warehouses, allocationArray) 
    #returns the number of locations where allocations were made

    finalAllocations, cost, degenerate = steppingStone(rows, columns, window, factories, warehouses, allocationArray, rawData, costArray, allocations, totalSupply, totalDemand)
     #optimises the initial feasible solution and returns the optimised result
    method = "Least Cost" 
    #used to show the name of the algorithm when the results are shown to the user
    if finalAllocations == None: 
        #if solution is degenerate, the initial solution will be used
        finalAllocations = allocationArray
    if cost == None: 
        #if the solution is degenerate the cost and finalAllocatiosn will be set to None, so the cost of the initial solution will need to be recalculated
        cost = costCalculate(factories, warehouses, costArray, allocationArray)
    
    original = messagebox.askyesno(title = "Results", message = "Would you like to see the original solution as well as the optimised solution?")
    resultsWindow(cost, method, rows, columns, factories, warehouses, totalSupply, totalDemand, entries, finalAllocations, degenerate)
    #results are shown to the user using tkinter
    if original: 
        #the initial feasible solution is shown on a new window
        identical = identicalMatrices(factories, warehouses, allocationArray, finalAllocations)
        if degenerate:
            messagebox.showinfo(title = "Original solution", message = "The solution is degenerate so the original solution is the same as the optimum solution.")
        elif identical: 
            #the solution only needs to be shown once
            messagebox.showinfo(title = "Original Solution", message = "The original solution and optimal solution are the same.")
        else:
            originalSolution(root, window, factories, warehouses, costArray, allocationArray, rows, columns, totalSupply, totalDemand, entries, degenerate, method)
    else:
        pass 

def calculateDifference(orderedArray): 
    #calculates the difference of the two lowest costs in an array passed as a parameter
    if len(orderedArray) == 1: 
        #if no allocations can be made on the column/ row then only one cost will be avaliable so that is the difference 
        difference = orderedArray[0]
    elif len(orderedArray) > 1:
        difference = orderedArray[1] - orderedArray[0]
    else: 
        #called when no allocations can be made
        difference = 0 
        #the row/ column with the largest difference is where an allocation is made, so this means any allocation that could be made, will be made
    return difference

def findDifferences(factories, warehouses, data):
    #the difference of the two lowest costs is found for each row and column
    for x in range(factories):
        orderedArray = [] 
        #creates new array for each row
        for y in range(warehouses):
            if data[x][y] != inf: 
                #if there is a cost not equal to infinity then it is appended to the row
                orderedArray.append(data[x][y])
            else:
                pass

        orderedArray.sort() 
        #uses the built in function to order the costs from lowest to highest
        data[x][-1] = calculateDifference(orderedArray) 
        #adds the difference of that row returned from the function to the last column
        #this column was appended to the data array and originally set to all zeros

    for y in range(warehouses):
        orderedArray = [] 
        #creates new array for each column
        for x in range(factories):
            if data[x][y] != inf: 
                #if the cost is not infinite, it is added to the array
                orderedArray.append(data[x][y])
            else:
                pass

        orderedArray.sort()
        #array is sorted into ascending order
        data[-1][y] = calculateDifference(orderedArray) 
        #the difference for the current column is added to the last row of the data array
        #this row was appended before the function was run
    return data #the updated data array is returned to the Vogel's function

def findRowLowestCost(x, warehouses, data):
    #takes in the x coordinate of the current row
    #finds the cell with the lowest cost for the specified row
    orderedArray = []
    for y in range(warehouses):
        if data[x][y] != inf:
            orderedArray.append(data[x][y]) 
            #finds the costs of the current row and appends them to an empty array
        else:
            pass
    if len(orderedArray) == 0: 
        #this means there are no costs that aren't infinite so no more allocations can be made
        return inf 
        #this will ensure no allocations will try to be made for the current row
    else:
        orderedArray.sort()
        return orderedArray[0] 
        #returns the lowest cost from the current row
        #if this row has the highest difference, an allocation will be made at this cell 

def highestRowDifference(data, factories, warehouses, columns):
    #finding the row with the highest difference in the two lowest costs
    currentDifference = 0 
    #trying to find the highest difference so this will be used for comparison
    xIndex = None 
    #will be used to check if a previous xIndex has been stored
    count = None 
    #used as a point of reference in a future function
    #this function is when count = 0, the highestColumnDifference is when count = 1
    for x in range(factories):
        if data[x][-1] > currentDifference: 
            #goes through the data array and compares the differences of all the rows
            currentDifference = data[x][-1] 
            #wants the highest difference, so if the current row difference is higher, it will become the new comparison value
            xIndex = x 
            #the row with the higher difference is stored so it can be used in the main section of Vogel's
            count = 0 
            #to let the program know the highest difference is a row
        elif data[x][-1] == currentDifference:
            if xIndex == None: 
                #if there hasn't been a previous xIndex stored, it will store the current one
                xIndex = x
            else:                    
                lowCostRowOne = findRowLowestCost(x, warehouses, data) 
                #finds the lowest cost on this row
                lowCostRowTwo = findRowLowestCost(xIndex, warehouses, data) 
                #finds the lowest cost of the previously stored row
                if lowCostRowOne < lowCostRowTwo: 
                    #if the cost is lower, the items should be allocated here instead of at the previous row
                    xIndex = x #storing the new row 
                else:
                    pass
        else:
            pass
    if xIndex == None: 
        #this is when all rows have a difference of zero so it will not make a difference which row is chosen 
        xIndex = 0 
    return currentDifference, xIndex, count 
    #this information will be needed by the main section of Vogel's if there is not a lower difference at one of the columns

def findColumnLowestCost(y, factories, data):
    #takes the y coordinate of the current column being worked on
    #finds the cell with the lowest cost
    orderedArray = []
    for x in range(factories):
        if data[x][y] != inf: 
            #finds all costs in the column that are not infinite and appends them to an array
            orderedArray.append(data[x][y])
        else:
            pass

    if len(orderedArray) == 0: 
        #this is when all costs are infinite so no allocations will be made
        return inf
    else:
        orderedArray.sort() 
        #the cell with the lowest cost is found and returned
        return orderedArray[0]

def highestColumnDifference(data, xIndex, currentDifference, factories, warehouses, count):
    #finds the column with the highest difference
    yIndex = None 
    #similar to xIndex, this variable will be used to check if a previous value has been stored
    for y in range(warehouses):  
        #iterates through the columns comparing the differences of each
        if data[-1][y] > currentDifference: 
            #the largest difference will  be used
        #the column differences are compared to the highest row difference from the previous function until a higher difference is found
        #if no difference is found to be higher than the row difference, then the highest row difference is used in the algorithm
            currentDifference = data[-1][y] 
            #the higher difference becomes the comparison value
            yIndex = y 
            count = 1 
            #lets Vogel's algorithm identify that the highest difference is a column
        elif data[-1][y] == currentDifference:
            if yIndex == None: 
                #no previous column index has been stored, so the highest difference is a row
                lowCostRow = findRowLowestCost(xIndex, warehouses, data) 
                #finding the lowest cost for the row 
                lowCostColumn = findColumnLowestCost(y, factories, data)
                #finding the lowest cost for the current column being stored
                if lowCostColumn < lowCostRow: 
                    #need to use the row/column with the lowest cost
                    yIndex = y 
                    #storing the current column to be referenced to later on 
                    count = 1 
                    #updated to let the program know the highest difference is now a column
                else:
                    pass
            else: 
                #if the previous highest difference is a column
                lowCostColumnOne = findColumnLowestCost(y, factories, data) 
                lowCostColumnTwo = findColumnLowestCost(yIndex, factories, data)
                #finding the lowest cost for both columns
                if lowCostColumnOne < lowCostColumnTwo: 
                    #the lowest cost is where the allocation will be made
                    yIndex = y
                    #new column index is stored
                else:
                    pass
        else:
            pass
    return count, xIndex, yIndex 
    #values will be stored in both the xIndex and yIndex depending on where the highest difference is
    #the value of 'count' will determine whether the xIndex or yIndex is used

def vogelsApprox(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window):
    rawData, rows, columns, allocationArray, run = collectData(entries, rows, columns, totalSupply, totalDemand, factories, warehouses, window) 
    #the data inputted by the user is collected from the interface and stored in the values returned by the function
    if run == False: 
        #stops the algorithm running if there is an error with the inputted data
        return

    data=rawData 
    #name is changed for consistency, as the identifier 'data' is used in other functions
    costArray = deepcopy(data) 
    #the data array will be changed so a copy is made to be used later
    data = [x + [0] for x in data] 
    #adding an extra column onto the matrix where the differences will be stored
    data.append([0]*columns) 
    #adding an extra row onto the matrix where the differences will be stored

    allocations = 0 
    #used as a condition as to whether or not the algorithm executes another time

    while not(allocations == totalSupply) and not(allocations == totalDemand):
        data = findDifferences(factories, warehouses, data) 
        #returns the function with all differences calculated
        currentDifference, xIndex, count = highestRowDifference(data, factories, warehouses, columns) 
        #finds the row with the highest difference 
        count, xIndex, yIndex = highestColumnDifference(data, xIndex, currentDifference, factories, warehouses, count) 
        #if a column has a higher difference than the one found in the rows function, the index of the column will be used
       
        lowestCost = inf 
        #used as a comparison when finding the lowest cost of a row
        if count == 0: 
            #if highest difference is a row then this code will be executed 
            for p in range(warehouses):
                if data[xIndex][p] < lowestCost: 
                    #finds the y coordinate of the cell with the lowest cost
                    lowestCost = data[xIndex][p] 
                    #the xIndex is the value when the highest difference was found
                    yIndex = p 
                    #iterates through the row to find the lowest cost 
                else:
                    pass
        else: 
            #if the highest difference is a column then the following code will be executed
            for r in range(factories): 
                #iterates through the column to find the lowest cost
                if data[r][yIndex] < lowestCost: 
                    #the yIndex was previosuly found when finding the highest difference 
                    lowestCost = data[r][yIndex]
                    xIndex = r 
                    #the xIndex of the cell with the lowest cost is stored
                else:
                    pass
        #the coordinates of the cell with the lowest cost, on the row/ column with the highest difference has now been stored
        supply = data[xIndex][-2] 
        demand = data[-2][yIndex] #finding the supply and demand of the selected cell

        if supply == demand:
            allocationArray[xIndex][yIndex] = supply 
            #as the supply and demand are balanced, it can all be allocated to the current cell
            allocations += supply 
            #the allocation just made is added to the running total
            supply = 0 
            demand = 0 
            #all supply and demand will be used up
            for r in range(rows):
                data[r][yIndex] = inf
            for s in range(columns):
                data[xIndex][s] = inf 
                #the cost of the cells in the row and column of the current cell are set to infinite
                #so they are not used when finding the next cell coordinates
            data[xIndex][-2] = 0
            data[-2][yIndex] = 0 
            #updating the supply and demand constraints in the data array

        elif demand < supply:
            allocationArray[xIndex][yIndex] = demand 
            #the demands can be fulfilled so are allocated to the selected cell
            allocations += demand
            supply -= demand 
            #the remaining supply is calculated
            for r in range(rows):
                data[r][yIndex] = inf 
                #the costs of the column are changed to infinite as ther is no demand left
            data[xIndex][-2] = supply 
            data[-2][yIndex] = 0 
            #supply and demand are updated so they can be used in the next iteration 

        else:
            allocationArray[xIndex][yIndex] = supply 
            #the supply can be used up
            demand -= supply 
            #calculating the remaining demand for the selected column
            allocations += supply
            for s in range(columns):
                data[xIndex][s] = inf 
                #there is no supply left on the selected row so all costs must be changed to infinite
            data[-2][yIndex] = demand
            data[xIndex][-2] = 0 
            #the supply and demand constraints for the selected row/ column are updated in the data array


    if totalDemand == totalSupply:
        cost = costCalculate(factories, warehouses, costArray, allocationArray) 
        #the cost of the initial feasbile solution is calculated 
    elif totalDemand > totalSupply:
        rows -= 1 
        #updating the number of rows so the dummy row isnt taken into account
        cost = costCalculate(factories, warehouses, costArray, allocationArray)
    else:
        columns -= 1 
        #updating the variable so the dummy column isnt taken into account
        cost = costCalculate(factories, warehouses, costArray, allocationArray)

    #the current allocations variable has the total number of allocations
    #the number of locations where allocations have been made is needed
    allocations = numLocationsUsed(factories, warehouses, allocationArray)
    #this returns the number of lcoations
    finalAllocations, cost, degenerate = steppingStone(rows, columns, window, factories, warehouses, allocationArray, rawData, costArray, allocations, totalSupply, totalDemand)
    #the initial solution is then passed through this function to optimise it, and the resulting data is returned

    if finalAllocations == None: 
        #if solution is degenerate, the original solution is used
        finalAllocations = allocationArray
    if cost == None: 
        #if solution is degenerate then the cost will need to be recalculated
        cost = costCalculate(factories, warehouses, costArray, allocationArray)

    method = "Vogel's Approximation Method" 
    #used in following function to be printed on the results page
    original = messagebox.askyesno(title = "Results", message = "Would you like to see the original solution as well as the optimised solution?")
    resultsWindow(cost, method, rows, columns, factories, warehouses, totalSupply, totalDemand, entries, finalAllocations, degenerate)
    #results are shown to the user using tkinter
    if original: 
        #the initial feasible solution is shown on a new window
        identical = identicalMatrices(factories, warehouses, allocationArray, finalAllocations)
        if degenerate:
            #if optimal solution is degenerate, the original solution is used as the final solution
            messagebox.showinfo(title = "Original solution", message = "The solution is degenerate so the original solution is the same as the optimum solution.")
        elif identical: #the original and optimal solution might be identical, so it only needs to be shown once
            messagebox.showinfo(title = "Original Solution", message = "The original solution and optimal solution are the same.")
        else:
            originalSolution(root, window, factories, warehouses, costArray, allocationArray, rows, columns, totalSupply, totalDemand, entries, degenerate, method)
    else:
        pass 

def degeneracyCheck(factories, warehouses, allocations):
    #checks whether a solution is degenerate
    if allocations < factories+warehouses-1: 
        #degeneracy formula found in my research 
        return True
    else:
        return False 
        #Boolean variable used to determine the outcome of the chosen algorithm
    
def pathFound(vertices):
    #checks if a path has been found form the current vertices
    if vertices[-1][0] == vertices[0][0]: 
        path = True 
        #a Boolean variable used to determine whether or not a function is run
    elif vertices[-1][1] == vertices[0][1]: 
        #if it is on the same row/ column the path is complete
        path = True
    else:
        path = False 
        #if not then the function is run again
    return path 

def rowSearch(x, y, allocationArray, vertices, columns, rows, skipVertex, factories, dummySource, recurse, count, changeY, timer, warehouses): 
    #contains parameters that depend upon the results of the column search
    vertexFound = False
    if recurse == True:
        count += 1 
        #used in the column search to keep track of how many times the functions have been called without finding a vertex
        if count > factories: 
            #if its been recursed more times than the number of factories, the previous two vertices should be removed
            count = 0 
            #set back to zero as the vertices will be changed
            vertexFound = True
            timer += 1 
            if timer >= 2: 
                #the timer shouldnt go above 3 or the vertex is invalid, ie, a path cannot be found from the current vertex
                changeY = True 
                #changes the Boolean conditions, so a different section of the code is run 
                timer = 0 
                #set back to zero as the vertices will be changed
            else:
                vertices.pop()
                vertices.pop() 
                #removes the last two vertices
                y = vertices[-1][1] 
                #sets the y coordinate to the last valid vertex, so a new search can be executed
        else:
            if changeY == True: 
                #the current vertex did not create a valid path so the coordinates are changed
                #the search for the next vertex is started again as the conditions are different this time
                y = 0
                changeY = False
            else:
                y = vertices[-1][1] 
                #the search starts from the column of the previous vertex - this condition is used in the next iteration
            x = vertices[-1][0] 
            #the x coordinate of the last vertex is used to find the next vertex in that row
        recurse = False 
        #the function does not need to be recursed through
    else:
        y = 0 
        #the search starts from the far left cell
    while vertexFound == False: 
        #the code is executed until a vertex is found
        index = [x,y]
        if y == warehouses: 
            #it has reached the end of the column so the search needs to be reset with different conditions
            recurse = True
            vertexFound = True
        elif index in (skipVertex[i] for i in range(len(skipVertex))): 
            #if the current cell is in the array skipVertex, then the y coordinate is incrememnted by 1
            y += 1 
        else:
            if allocationArray[x][y] > 0: 
                #an allocation was made at this coordinate, so it can be used as a vertex
                vertices.append([x,y]) 
                #the new vertex is appended to the array of vertices
                skipVertex.append([x,y]) 
                #it no longer needs to be included in the search for a new vertex
                vertexFound = True 
                #stops the loop from runnning again

    return vertices, y, recurse, count, changeY, timer

def columnSearch(x, y, allocationArray, vertices, columns, rows, skipVertex, warehouses, factories, dummySource, recurse, count, changeY, timer, costArray, totalSupply, totalDemand):
    #finds the next vertex of the path in the same column as the current vertex
    vertexFound = False
    #the algorithm starts at the top of every column
    if recurse == True:
        #if this function was just called
        count += 1 
        #count is used to keep track of how many times this function has been called without finding a vertex
        if count > warehouses: 
            #after the function has been run this many times, the current path is incorrect so the previous two vertices must be removed and a different path must be tried
            count = 0 
            #set back to zero as the vertices have been changed
            vertexFound = True
            timer += 1 
            #count is used to keep track of how many times the row search has been executed without finding a vertex
            vertices.pop()
            vertices.pop()
            x = vertices[-1][0] 
            #sets the x coordinate to the last valid vertex, so the next vertex can be found from this
        else:
            x = 0 
            #starts the search again from the top of the column, missing out last vertex because it didnt create a valid path 
            y = vertices[-1][1]
        recurse = False
    else:
        x = 0

    while vertexFound == False: 
        #the code is executed repeatedly until a vertex is found 
        index = [x,y] 
        #used as a comparison
        if x == factories: 
            #the end of the column has been reached so the function needs to be executed again with the new conditions
            recurse = True 
            vertexFound = True 
            #updating these Boolean variables will ensure the function is recursed
        elif index in (skipVertex[i] for i in range(len(skipVertex))):
            x += 1 
            #if you are currently at a cell that can be skipped the x index is incremented by 1
        else:
            if allocationArray[x][y] >0: 
                #if there is an allocation a vertex has been found
                vertices.append([x,y]) 
                #the vertex is added to the array of vertices
                skipVertex.append([x,y]) 
                #the vertex will now be ignored when completing the path
                vertexFound = True

    allocations = numLocationsUsed(factories, warehouses, allocationArray) 
    #returns the number of locations where allocations have been made
    degenerate = degeneracyCheck(factories, warehouses, allocations) 
    #must check if new solution is degenerate
    
    if degenerate == True:
        return None, True
    else:
        path = pathFound(vertices) 
        #checks if the path is complete
        vertices = verticesCheck(vertices, factories) 
        #checks vertices are valid
        length = len(vertices) 
        #used as part of a condition 

        if path == True and len(vertices) > 2:
            return vertices, False 
            #the path has been found and optimisation can now take place
        else:
            vertices, y, recurse, count, changeY, timer = rowSearch(x, y, allocationArray, vertices, columns, rows, skipVertex, factories, dummySource, recurse, count, changeY, timer, warehouses) 
            #calls the function that finds the next vertex
            #the functions alternatively execute - column, row, column etc 
            path = pathFound(vertices) 
            #checks if the path is complete
            if length >= factories and path == True :
                return vertices, False 
                #the path has been found and optimisation can take place
            else:
                return columnSearch(x, y, allocationArray, vertices, columns, rows, skipVertex, warehouses, factories, dummySource, recurse, count, changeY, timer, costArray, totalSupply, totalDemand) 
                #if a path hasn't been found, then a new vertex needs to be found in the same column

def costChange(vertices, rawData):
    #updates the costs of the current path
    #the costs will alternate with positive and negative values
    costs = [] 
    #declaring a variable that will contain the costs of each vertex of a path
    for i in range(len(vertices)):
        costs.append(rawData[vertices[i][0]][vertices[i][1]]) 
        #appending the cost of each vertex to the variable 'costs'

    for j in range(1, len(vertices), 2):
        costs[j] *= -1 
        #making every other vertex a negative cost starting with the second vertex

    netCost = sum(costs) 
    #adding all the costs in the path together
    return netCost, costs 
    #returning information calculated 

def verticesCheck(vertices, factories):
    #checks that the vertices for the path are valid
    fixed = False 
    #used as a condition for the while loop
    while fixed == False:
        if len(vertices) <= 2:  
            #if there are less than 3 vertices a path cannot be created, so the vertices are returned to be manipulated further
            return vertices
        else:
            for p in range(1, len(vertices)):
                if p >= len(vertices)-1: 
                    #sometimes greater than due to recursion, if so the vertices are returned and assumed to be valid
                    return vertices
                elif vertices[p-1][0] == vertices[p][0] and vertices[p][0] == vertices[p+1][0]: 
                    #if three vertices lie on the same column, the middle one is removed and the new vertices are checked again, through recursion
                    vertices.pop(p) 
                    #in-built function that removes the index 'p' from the array 'vertices'
                    verticesCheck(vertices, factories) 
                    #passes the updated vertices as a parameter
                    fixed = True 
                    #this stops the while loop running, once the vertices have been validated
                elif vertices[p-1][1] == vertices[p][1] and vertices[p][1] == vertices[p+1][1]: 
                    #if three vertices lie in the same row, the middle one is removed and the new vertices are checked again using recursion
                    vertices.pop(p)
                    verticesCheck(vertices, factories)
                    fixed = True
                else:
                    pass

def steppingStone(rows, columns, window, factories, warehouses, allocationArray, rawData, costArray, allocations, totalSupply, totalDemand):
    #function is automatically run after a method is chosen to optimise the initial solution
    dummySource = True
    recurse = False
    changeY = False 
    #all used as Boolean conditions
    timer = 0
    count = 0 
    #both used as count variables to keep track of different loops

    degenerate = degeneracyCheck(factories, warehouses, allocations) 
    #returns whether or not the solution is degenerate
    if degenerate == True:
        return None, None, True 
        #returns these values so that the initial feasible solution will be used as the final solution
    else:
        optimalSolution = False 
        #the solution is not degenerate so can be optimised further
        while optimalSolution == False:
            emptyCells = [] 
            #keeps track of cells that have not had any allocations 
            currentLowestCost = 0 
            #used as a condition later on
            for p in range(factories):
                for q in range(warehouses): 
                    #loops through the allocationArray
                    if allocationArray[p][q] == 0:
                        emptyCells.append([]) 
                        #appends an empty index to the empty cells array if no allocations have been made at the current coordinates
                        emptyCells[-1] = [p,q] 
                        #updates the emptyCells array appended with the coordinates of the current cell
                    else:
                        pass

            skipVertex = [0] 
            #declares an array that will be filled with coordinates
            for p in range(0,len(emptyCells)): 
                #a path will be created for each empty cell 
                vertices = [] 
                #an array declared that will have the coordinates of the current path being created
                x = emptyCells[p][0]
                y = emptyCells[p][1]
                vertices.append([x, y]) 
                #the starting vertex is the current empty cell
                skipVertex = deepcopy(emptyCells) 
                #all empty cells are ignored because the path can only contain one empty cell, which is the first vertex
                vertices, degenerate = columnSearch(x, y, allocationArray, vertices, columns, rows, skipVertex, warehouses, factories, dummySource, recurse, count, changeY, timer, costArray, totalSupply, totalDemand) 
                #calls the function that returns the path found for the current empty cell
                if degenerate == True:
                    return None, None, True 
                    #ensures the initial solution is used because degenerate solutions cannot be optimised
                else:
                    pass
                completeVertices = verticesCheck(vertices, factories) 
                #returns the path of vertices that have been validated

                netCosts, costs = costChange(completeVertices, rawData) 
                #finds out whether or not the path can be optimised further
                if netCosts < currentLowestCost: 
                    #if the netCost is negative, the path can be optimised
                    currentLowestCost = netCosts 
                    optimalVertices = deepcopy(vertices) 
                    #a copy is used to show the difference of the original and optimised vertices
                    newCosts = deepcopy(costs)
                    #finds the path with the most negative netCost and keeps a copy of that path and it's costs
                    #this condition is checked at the end of every iteration, ie, every time a new path has been created

            finalAllocations = deepcopy(allocationArray) 
            #the 'finalAllocations' array will be changed and optimimsed so a copy of the solution is kept

            if currentLowestCost < 0:
                 #if the path can be optimised
                lowestAllocation = inf 
                #will be used as a comparison value
                for k in range(1, len(optimalVertices), 2): 
                    #ignores the empty cell since no allocations will be made there
                    #finds the smallest allocation for the vertices with a negative cost 
                    currentAllocation = finalAllocations[optimalVertices[k][0]][optimalVertices[k][1]] 
                    #finds the allocation made at the current vertex
                    if currentAllocation <= lowestAllocation: 
                        #finds the smallest allocation for the negative vertices
                        lowestAllocation = currentAllocation
                        xIndex = optimalVertices[k][0] 
                        yIndex = optimalVertices[k][1] 
                        #saves the coordinates of the vertex with the lowest allocation
                        minimumAllocation = finalAllocations[xIndex][yIndex] 
                        #updates the value of the lowest allocation 

                for j in range(len(optimalVertices)):
                    x = optimalVertices[j][0]
                    y = optimalVertices[j][1] 
                    #declares the coordinates of the current vertex as 'x' and 'y'
                    if newCosts[j] > 0: 
                        #if the cost of the current vertex is positive we add the minimum allocation
                        finalAllocations[x][y] += minimumAllocation
                    else:
                        finalAllocations[x][y] -= minimumAllocation 
                        #if the cost is negative, we subtract the minimum allocation 
                allocationArray = finalAllocations 
                #the allocationArray identifier is used when the code executes on the next iteration 
                #the optimisation algorithm is then used on the updated array

            else:
                optimalSolution = True

            cost = costCalculate(factories, warehouses, costArray, finalAllocations) 
            #the cost of the optimised array is calculated

        return finalAllocations, cost, False 
        #the optimised data is returned to be dispayed on the results page 

def helpMainPage():
    #help information for the main page
    tk.messagebox.showinfo("Help", "The number of Factories and Warehouses are the total number of places you are planning to move items from/ to. \n\nThe  demand and supply are the total quantities you have in all the factories and all the warehouses.\n\nThe execution button will show you a window where you can enter the rest of your data and select a method.") 
    #one piece of information the user can read if the help button for this window is selected

def helpMatrix():
    #help information for the input matrix
    tk.messagebox.showinfo("Help", "The cells labelled with 'W' and 'F' represent your factories and warehouses. The cells at the end of each row/ column are for the total supply/ demand for that factory/warehouse. The other cells represent the transportation cost for the factory to warehouse at that index.") 
    #more information the user can access if needed

def helpMethods():
    #help information for the avaliable methods
    tk.messagebox.showinfo("Help", "There are three different methods to produce a solution. To find the most efficient for your data compare the results of each.\n\nA results window will open to show the optimal solution to the method you click on.")

def mainMenu():
    #declares all variables and information needed to create the interface 
    warehouses = tk.StringVar()
    factories = tk.StringVar()
    totalSupply = tk.StringVar()
    totalDemand = tk.StringVar() 
    #initialising variables to be used on first window

    img = tk.PhotoImage(file = "lorry.png") 
    #original size is larger than necessary 
    smallImg = img.subsample(7,7) 
    #makes image 1/3 of the size by taking every third pixel from x and y 
    tk.Label(root, image = smallImg).grid(row = 0, column = 1)
     #places image onto the window

    ttk.Label(text = "No. warehouses").grid(row = 1, column =0)
    warehouse_box = ttk.Entry(root, textvariable = warehouses, width = 4) 
    #creates a label with a box for the user to enter the stated information
    warehouse_box.grid(row = 1, column =1)

    ttk.Label(text = "No. factories").grid(row = 1, column =2)
    factory_box = ttk.Entry(root, textvariable = factories, width = 4)
    #matches each entry box input to a different variable to be used later on
    factory_box.grid(row = 1, column =3)

    ttk.Label(text = "Total Supply").grid(row = 2, column =0)
    factory_box = ttk.Entry(root, textvariable = totalSupply, width = 4)
    factory_box.grid(row = 2, column =1)

    ttk.Label(text = "Total Demand").grid(row = 2, column =2)
    factory_box = ttk.Entry(root, textvariable = totalDemand, width = 4)
    factory_box.grid(row = 2, column =3)

    ttk.Button(root, text = "execution", command = lambda: matrixTable(factories, warehouses, totalSupply, totalDemand)).grid(row = 3, column =1) 
    #creates a button the user can click on to go to the next window
    ttk.Button(root, text = "help", command = lambda: helpMainPage()).grid(row = 3, column = 2) 
    #outputs extra information to the user if needed
    root.mainloop() 
    #enables us to run the program
    #creates an infinte loop waiting for the user to give it a task and will carry on until the program (interface) is closed

mainMenu() #calls the first function, starting the program



