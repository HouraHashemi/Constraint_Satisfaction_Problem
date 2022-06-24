import copy
import os
import time

class Puzzle():
    
    def __init__(self):
        # each element is tuple(row,col)
        self.step = 0
        self.test_file_name = ""

        self.history = dict()
        self.blank_domain = dict()
        self.assignment = dict()
        self.fixed = list()


    def load_puzzle(self,file_name):
        self.test_file_name = file_name.split("/")[-1]
        self.file = open(file_name,"r")
        self.dimension = tuple([int(d) for d in self.file.readline().split()])
        # [[][][]...[]]
        self.puzzle = [self.file.readline().split() for line in range(int(self.dimension[0]))]


    def find_blank(self):
        # put blank to blank_domain dictionary
        full = list()
        for line in range(self.dimension[0]):
            for el in range(self.dimension[1]):
                if self.puzzle[line][el] == '-':
                    self.blank_domain[(line,el)] = ['0','1']
                else:
                    full.append((line,el))
        # find fixed cell
        if self.fixed == []:
            self.fixed: Final = full
        # print(self.blank_domain)


    def MRV_heuristic(self):
        # mll: min_len_list
        mll = []
        # find minimum domain len
        min_len = min([len(l) for l in self.blank_domain.values()])
        # find keys that its value is matching to min_len
        for k in self.blank_domain.keys():
            if (len(self.blank_domain[k]) == min_len) and (k not in self.assignment.values()):
                mll.append(k)
        # return list of blanks with min len boundry domain    
        return mll
    
    
    def constranints(self, blank_coordinate, domain_member):
        # ruls:
        #   . domain is [0,1]
        #   . only 0,1,11,00 substring accepted
        #   . each column and row unic
        #   . count(1) == count(0) in each column and row
        temp_puzzle = copy.deepcopy(self.puzzle)
        temp_puzzle[blank_coordinate[0]][blank_coordinate[1]] = domain_member
        # row and column that blank_coordinate on it
        row = temp_puzzle[blank_coordinate[0]]
        col = [temp_puzzle[r][blank_coordinate[1]] for r in range(self.dimension[0])]
        # row rules ---------------------------------------------------
        if ("111" in "".join(row)) or ("000" in "".join(row)):
                return False
        if row.count('1')>(len(row)/2) or row.count('0')>(len(row)/2):
                return False
        # rsl: row string list , create rows as string in a list
        rsl = list()
        for r in temp_puzzle:
            if '-' not in r:
                rsl.append("".join(r))
        if len(rsl) != len(set(rsl)):
            return False
        # column rules ------------------------------------------------
        if ("111" in "".join(col)) or ("000" in "".join(col)): 
            return False
        if col.count('1')>(len(col)/2) or col.count('0')>(len(col)/2):
            return False
        # iterate in columns
        csl = list()
        for c in range(self.dimension[1]):
            cx = [temp_puzzle[r][c] for r in range(self.dimension[0])]
            if '-' not in cx:
                csl.append("".join(cx))
        if len(csl) != len(set(csl)):
            return False
        # -------------------------------------------------------------       
        return True
    

    def forward_checking(self, candidate):
        
        for blank in self.blank_domain:
            # clear updated_domain_fch(forward_checking)
            updated_domain_fch = []
            for member in self.blank_domain[blank]:
                if self.constranints(blank, member):
                    updated_domain_fch.append(member)            
            self.blank_domain[blank] = updated_domain_fch
        # print(self.blank_domain)
        if [] in self.blank_domain.values():
            return False
        else:
            return True


    def complete_puzzle(self):
        # backup cell, if backtraking needed
        back_to_this_cell = None
        num_of_backtracking = 0

        while(len(self.blank_domain) != 0):
            self.step = self.step + 1
            if back_to_this_cell == None:
                blank_candidate = self.MRV_heuristic()[0]
                domain_candidate = self.blank_domain[blank_candidate]
            else:
                blank_candidate = back_to_this_cell[0]
                domain_candidate = back_to_this_cell[1] 
                back_to_this_cell = None
        
            # more then 2 option or first step 
            if (len(domain_candidate) > 1):
                self.history[blank_candidate] = copy.deepcopy(self.puzzle)
            
            d = domain_candidate[0]
            if self.constranints(blank_candidate,str(d)):
                # submit head of the domain queue to puzzle
                self.assignment[blank_candidate] = d
                self.puzzle[blank_candidate[0]][blank_candidate[1]] = str(d)
                self.blank_domain.pop(blank_candidate)        
                #-------------------------------------
                check = self.forward_checking(blank_candidate)
                #-------------------------------------
                print("🔲 BLANK_CANDIDATE : {}\n🖐️  DOMANI_CANDIDATE: {}\n📌 DOMAIN_SELECTED : {}"\
                    .format(blank_candidate,domain_candidate,d))
                print("----------------------------------------")
                print("❔ FORWARD_CHECKING: {}".format(check))
                print("========================================")
                if check == True:
                    self.display_puzzle()
                else:
                    self.display_puzzle()  
                    print("========================================")
                    print("[⚠️ ]----------------BACKTRAKING NEEDED")
                    print("========================================")
                    num_of_backtracking = num_of_backtracking + 1
                    # time.sleep(1)
                    if self.history == {}:
                        os.system('cls' if os.name == 'nt' else 'clear') 
                        print("========================================")
                        print("-------🔻 THERE IS NO SOLUTION🔻-------")
                        print("========================================")
                        break
                    back_to_this_cell = self.backtracking()
            
            # time.sleep(.5)
            os.system('cls' if os.name == 'nt' else 'clear')
        print("========================================")            
        print("[🐾 ] STEP: {} | TEST FILE: {}\n[♻️  ] NUM OF BACKTRACKING: {} "\
            .format(self.step, self.test_file_name, num_of_backtracking))
        print("========================================")            


    def backtracking(self):

        # ():[[][][]] last_blank with more than one option and its puzzle
        last_puzzle = list(self.history.items())[-1][1]
        last_blank  = list(self.history.items())[-1][0]
       
        self.assignment = dict(list(self.assignment.items())[:list(self.assignment.keys()).index(last_blank)])

        self.puzzle = last_puzzle
        self.find_blank()
        #-------------------------------------
        self.forward_checking((-1,-1))
        #-------------------------------------
        self.blank_domain[last_blank] = self.blank_domain[last_blank][1:]
        
        if len(self.blank_domain[last_blank])<2:
            self.history.pop(last_blank)

        return (last_blank, self.blank_domain[last_blank]) 
        

    def simulate_solution(self, file_name):
        os.system('cls' if os.name == 'nt' else 'clear') 
        self.load_puzzle(file_name)
        for b in self.assignment.keys():
            self.puzzle[b[0]][b[1]]= self.assignment[b]
            self.display_puzzle()
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear') 
        self.display_puzzle()
 

    def display_puzzle(self):
        # for l in self.puzzle:
        #     print(l)
        emoji = ["🔻","♻️","1️⃣","0️⃣","⚠️","❎","🖐️","📌","🔲","🐾"]
        for r in range(self.dimension[0]):
            for c in range(self.dimension[1]):
                if tuple([r,c]) in self.fixed:
                    if self.puzzle[r][c] == '1':
                        print("1️⃣",end="  ")
                    elif self.puzzle[r][c] == '0':
                        print("0️⃣",end="  ")
                else:
                    if self.puzzle[r][c] == '-':
                        print("❎", end=" ")
                    else:
                        print("|"+self.puzzle[r][c]+"|", end="")
            print()
        print("========================================")

       
#---------------------------------------------------------
# END OF CLASS
#---------------------------------------------------------

if __name__ == '__main__':
    

    test_file_name = "puzzles//puzzle5.txt"
    p = Puzzle()
    p.load_puzzle(test_file_name)
    p.find_blank()
    p.complete_puzzle()
    p.display_puzzle()
 