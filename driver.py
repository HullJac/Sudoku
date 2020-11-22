"""
Program:        Sudoku Solver using Forward Checking, AC-3, and Backtracking Search
Programmer:     Jacob Hull
Date:           11/23/2020

Description:    This program is a command line run program using python3.
                     You feed the program a puzzle containting the puzzle or puzzles on separate lines.
                     The puzzles should be all in one line starting with the top row of the puzzle, 
                    then then second and so on.
                The program then outputs a txt file named output.txt containing
                the finised puzzle or puzzles usingtwo different methods.
                (Forward Checking and AC-3)

"""
import queue
import sys
import copy
import string


#create an alphabet to reference
alphabet = string.ascii_uppercase
alphaList = list(alphabet)


# size to base all the calculations off of
puzzleSize = 9


# prep the variable matrix to be filled
variable_matrix = []
for i in range(puzzleSize):
    variable_matrix.append([])

# fills the matrix
for letter in range(puzzleSize):
    for number in range(puzzleSize):
        variable_matrix[letter].append(alphaList[letter] + str(number + 1))


# prep the constraints to be filled
constraints = []
for i in range(puzzleSize):
    constraints.append([])
    for j in range(puzzleSize):
        constraints[i].append([])


# adds the rows to the constraints
for i in range(puzzleSize):
    for j in range(puzzleSize):
        for k in range(puzzleSize):
            if variable_matrix[i][j] == alphaList[i] + str(k + 1):
                pass
            else:
                constraints[i][j].append(alphaList[i] + str(k + 1))


# adds the columns to the constraints
for i in range(puzzleSize):
    for j in range(puzzleSize):
        for k in range(puzzleSize):
            if variable_matrix[i][j] == alphaList[k] + str(j + 1): 
                pass
            else:
                const = alphaList[k] + str(j + 1)
                constraints[i][j].append(const)


# creates the squares
boxes = []
for i in range(puzzleSize):
    boxes.append([])

boxSize = int(puzzleSize/3)
matrix = copy.deepcopy(variable_matrix)

spot = 0
num = 1
spotReset = 0
# fills the squares
for i in range(puzzleSize):
    for j in range(puzzleSize): #9
        boxes[spot].append(alphaList[j] + str(num))
        if (j + 1) % boxSize == 0:
            spot += 1
    if i + 1 == int(puzzleSize/3):
        spotReset = boxSize
    elif i + 1 == int(puzzleSize - boxSize):
        spotReset = boxSize + boxSize
    spot = spotReset
    num += 1


# adds the square to the constraints minus the columns done already
for i in range(puzzleSize):
    for j in range(puzzleSize):
        pos = alphaList[i] + str(j + 1)
        for box in boxes:
            # finds the box for the position we are at
            if pos in box:
                # go through every spot in the box
                for position in box:
                    # add the position to the constraint if its not there
                    if position not in constraints[i][j] and position != pos:
                        constraints[i][j].append(position)


def BTS_search(csp, revision):
    return BTS(csp, revision)


def BTS(csp, revision):    
    if doneQ(csp):
        return csp
    var=MRV(csp)
    if var=='':
        return None
    domains=csp[var][0]
    for i in domains:
        tempCSP=copy.deepcopy(csp)
        tempCSP[var][0]=[i]
        # Does either the forward chekcing or ac-3 way
        if revision == 'forward_check':
            forwardCheck(tempCSP)
        elif revision == 'ac-3':
            AC_3(tempCSP)
        else:
            print("That is not a supported method: " + revision)
            print("Try again using either 'ac-3' or 'forward_check'")
            sys.exit(1)
        if not collisionTest(tempCSP, var):
            result=BTS(tempCSP, revision)
            if result!=None:
                return result
    return None


def collisionTest(csp,val):
    collisions=0
    domain1=csp[val][0]
    if len(domain1)==1:
         constraints=csp[val][1]
         for k in constraints:
             domain2=csp[k][0]
             if len(domain2)==1:
                 if domain1[0]==domain2[0]:
                    collisions=collisions+1
    if collisions==0:
        return False
    return True


def DomainsComplete(csp):
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            key=variable_matrix[i][j]
            domain=csp[key][0]
            if len(domain)>1:
                return False
    return True


def generate_domain(board): 
    domain = []
    for i in range(puzzleSize):
        domain.append([])
    temp=list(board)
    temp2=[]
    for i in temp:
        temp2.append(int(i))
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            domain[i].append([temp2[9*i+j]])
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            if domain[i][j][0]==0:
                domain[i][j]=[1,2,3,4,5,6,7,8,9]
    return domain
        

def forwardCheck(csp):
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            key=variable_matrix[i][j]
            domainDi=csp[key][0]
            if len(domainDi)!=1:
                constraints=csp[key][1]
                for keyJ in constraints:
                    domainDj=csp[keyJ][0]
                    if len(domainDj)==1 and len(domainDi)>1:
                        try:
                            csp[key][0].remove(domainDj[0])
                        except:
                            pass


def doneQ(csp):
    total=0
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            tmp=variable_matrix[i][j][0]
            if len(csp[variable_matrix[i][j]][0])==1:
                total=total+1
    if total == int(puzzleSize*puzzleSize) and not totalColTest(csp): #total == 81
        return True
    return False


def totalColTest(csp):
    collisions=0
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            val=variable_matrix[i][j]
            if collisionTest(csp,val):
                return True
    return False


def AC_3(csp):
    q = queue.Queue()
    # add all the possible arcs to the queue
    for row in range(puzzleSize):
        for spot in range(puzzleSize):
            for const in range(len(constraints[0][0])):
                q.put([variable_matrix[row][spot], constraints[row][spot][const]])
        
    while not q.empty():
        # arc contains [Xi, Xj]
        arc = q.get()
        # check if the arc changes the csp
        if revise(csp, arc):
            # check the length of the domain of the arc if zero return false
            if len(csp[arc[0]][0]) == 0:
                return False
            # add the other constriants that point to the one revised to the queue
            for Xk in csp[arc[0]][1]:
                if Xk == arc[1]:
                    pass
                else:
                    q.put([Xk, arc[0]])
    return True
            

def revise(csp, arc):
    revised = False
    # goes through each item in the domain of the Xi (arc[0])
    for domain in csp[arc[0]][0]:
        if not isConsistent(csp, domain, arc):
            csp[arc[0]][0].remove(domain)
            revised = True
    return revised


def isConsistent(csp, domain, arc):
    for y in csp[arc[1]][0]:
        if arc[1] in csp[arc[0]][1] and y != domain:
            return True
    return False


def MRV(csp):
    mrv=1000
    minkey=''
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            key=variable_matrix[i][j]
            domain=csp[key][0]
            d1=len(domain)
            if d1<mrv and d1!=1:
                mrv=d1
                minkey=key
    return minkey


def display(csp):
    for i in range(puzzleSize):
        line=[]
        for j in range(puzzleSize):
            key=variable_matrix[i][j]
            domainDi=csp[key][0]
            line.append(domainDi)
        print(str(line))


# function that helps to get the final output as a string
def getFinalPuzzle(csp):
    puz = ''
    for i in range(puzzleSize):
        for j in range(puzzleSize):
            key = variable_matrix[i][j]
            domain = csp[key][0]
            puz = puz + str(domain[0])
    return puz


def main():
    sys.argv=[sys.argv[0], sys.argv[1]]
    f = open("output.txt", "w")
    for Type in range(2): 
        csp={}
        domain=generate_domain(sys.argv[1])
        for i in range(puzzleSize):
            for j in range(puzzleSize):
                csp.update({variable_matrix[i][j]:[domain[i][j],constraints[i][j]]})
                # line below is used to print out the csp
                #print(variable_matrix[i][j]+"  "+str(csp[variable_matrix[i][j]][0])+" "+str(csp[variable_matrix[i][j]][1]))
        # do ac-3 then forward check
        if Type == 0:
            solution=BTS_search(csp, 'ac-3')
        else:
            solution=BTS_search(csp, 'forward_check')

        # writes the solution to the file
        if solution == None:
            f.write(sys.argv[1] + " FAIL")
            sys.exit(0)
        else:
            finalPuz = getFinalPuzzle(solution)
            if Type == 0:
                f.write(finalPuz + " AC3\n")
            else:
                f.write(finalPuz + " FC")
    f.close()


if __name__=="__main__":
    main()
