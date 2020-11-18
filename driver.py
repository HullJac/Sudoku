"""
Program:        Sudoku Solver using Forward Checking, AC-3, and Backtracking Search
Programmer:     Jacob Hull
Date:           11/XX/2020

Description:    This program is a command line run program using python3.
                You feed the program a txt file containting the puzzle or puzzles on separate lines.
                The puzzles should be all in one line starting with the top row of the puzzle, 
                then then second and so on.
                The program then outputs a txt file containing the finised puzzle or puzzles using
                two different methods. (Forward Checking and AC-3)
"""
import queue
import sys
import copy

variable_matrix=[["A1","A2","A3","A4"],["B1","B2","B3","B4"],["C1","C2","C3","C4"]
                 ,["D1","D2","D3","D4"]]

constraints=[
    [["A2","A3","A4","B1","C1","D1","B2"],["A1","A3","A4","B2","C2","D2","B1"],["A1","A2","A4","B3","C3","D3","B4"],["A1","A2","A3","B4","C4","D4","B3"]]
    ,[["B2","B3","B4","A1","C1","D1","A2"],["B1","B3","B4","A2","C2","D2","A1"],["B1","B2","B4","A3","C3","D3","A4"],["B1","B2","B3","A4","C4","D4","A3"]]
    ,[["C2","C3","C4","B1","A1","D1","D2"],["C1","C3","C4","B2","A2","D2","D1"],["C1","C2","C4","B3","A3","D3","D4"],["C1","C2","C3","B4","A4","D4","D3"]]
    ,[["D2","D3","D4","B1","C1","A1","C2"],["D1","D3","D4","B2","C2","A2","C1"],["D1","D2","D4","B3","C3","A3","C4"],["D1","D2","D3","B4","C4","A4","C3"]]
             ]


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
            ###display(tempCSP)
            ###print('')
            forwardCheck(tempCSP)
            ###display(tempCSP)
            ###print("---------------------------")
        elif revision == 'ac-3':
            display(tempCSP)
            print('')
            AC_3(tempCSP)
            print('after')
            display(tempCSP)
            print("---------------------------")
        else:
            print("That is not a supported method: " + revision)
            print("Try again using either 'ac-3' or 'forward_check'")
            sys.exit(1)
        if not collisionTest(tempCSP, var):
            result=BTS(tempCSP, revision)
            ###print(result)
            ###print('')
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
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            key=variable_matrix[i][j]
            domain=csp[key][0]
            if len(domain)>1:
                return False
    return True


def generate_domain(board):
    domain=[[],[],[],[]]
    temp=list(board)
    temp2=[]
    for i in temp:
        temp2.append(int(i))
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            domain[i].append([temp2[4*i+j]])
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            if domain[i][j][0]==0:
                domain[i][j]=[1,2,3,4]
    return domain
        

def forwardCheck(csp):
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
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
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            tmp=variable_matrix[i][j][0]
            if len(csp[variable_matrix[i][j]][0])==1:
                total=total+1
    if total==16 and not totalColTest(csp):
        return True
    return False


def totalColTest(csp):
    collisions=0
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            val=variable_matrix[i][j]
            if collisionTest(csp,val):
                return True
    return False


def AC_3(csp):
    q = queue.Queue()
    # these numbers change for size of puzzle
    # add all the possible arcs to the queue
    for row in range(len(variable_matrix)):
        for spot in range(len(variable_matrix)):
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
    # goes throuhg each item in the domain of the Xi (arc[0])
    for domain in csp[arc[0]][0]:
        if not isConsistent(csp, domain, arc):
            csp[arc[0]][0].remove(domain)
            revised = True
    return revised


def isConsistent(csp, domain, arc):
    # is this the domain or constraints
    for y in csp[arc[1]][0]:
        if arc[1] in csp[arc[0]][1] and y != domain:
            return True
    return False


def MRV(csp):
    mrv=1000
    minkey=''
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            key=variable_matrix[i][j]
            domain=csp[key][0]
            d1=len(domain)
            if d1<mrv and d1!=1:
                mrv=d1
                minkey=key
    return minkey


#def solutionQ(csp):



def display(csp):
    for i in range(len(variable_matrix)):
        line=[]
        for j in range(len(variable_matrix)):
            key=variable_matrix[i][j]
            domainDi=csp[key][0]
            line.append(domainDi)
        print(str(line))


def main():
    sys.argv=[sys.argv[0], '0430001001000340']
            #'0403002000013000']
    csp={}
    domain=generate_domain(sys.argv[1])
    for i in range(len(variable_matrix)):
        for j in range(len(variable_matrix)):
            csp.update({variable_matrix[i][j]:[domain[i][j],constraints[i][j]]})
            #print(variable_matrix[i][j]+"  "+str(csp[variable_matrix[i][j]][0])+" "+str(csp[variable_matrix[i][j]][1]))
    solution=BTS_search(csp, 'ac-3')
    display(solution)
    

if __name__=="__main__":
    main()
