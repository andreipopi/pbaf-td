import sys
import random
import os

# What do we need to generate?
# We need instances in the "classical" asp predicate format
# as a primal graph. Something like:
#arg(a).
#arg(b).
#arg(c).
#p(a,1).
#p(b,1).
#p(c,0.9).
#%we need ids for the attacks in the iterative multiplication, in the D-FLAT/Clingo approach.
#p(1,a,c,0.4).
#p(2,c,a,1).
#p(3,b,c,0.8).
#p(4,c,b,0.4).
#att(a,c).
#att(c,a).
#att(b,c).
#att(c,b).
#query(a).
#extension(a).
#extension(b).
#this instance can be directly use by
# -ClingoSystem
# -DFLATSystem
# -and is the format parsed by the input_output.py in PythonSystem

arguments = []
attacks = []
supports = []

prob_args = []
prob_attacks = []

grid = [] # grid used to select attacks and stuff.
framework = [] # the framework created in lp format.
 
#METHODS
def initialise(n_total_sentences):
    args = ["a" + str(i) for i in range(n_total_sentences)]
    #contraries = {asmpt: random.choice(atoms+assumptions) for asmpt in assumptions}
    print("Arguments: ",args)
    return args

def create_grid(k,n):
    grid_content = arguments.copy()
    random.shuffle(grid_content)
    index = 0
    for _ in range(0, n):
        row = []
        for _ in range(0, k):
            row.append(grid_content[index])
            index = index + 1
        grid.append(row)
    return grid

def print_grid(grid):
    print()
    print("Grid")
    for row in grid:
        print(row,"\n")
    print()
    return

def immediate_neighbours(i, j, grid):
    max_rows = len(grid)
    max_cols = len(grid[0]) if max_rows > 0 else 0
    neighbours = []
    if i - 1 >= 0:    # Check above (i-1, j)
        neighbours.append(grid[i-1][j])
    if i + 1 < max_rows:    # Check below (i+1, j)
        neighbours.append(grid[i+1][j])
    if j - 1 >= 0:    # Check left (i, j-1)
        neighbours.append(grid[i][j-1])
    if j + 1 < max_cols:    # Check right (i, j+1)
        neighbours.append(grid[i][j+1])
    return neighbours

""" not currently used
#i,j is the position of current
#direction is "up" "down" "left" or "right"
def neighbourhood(i, j, direction, size):
    max_rows = len(grid)
    max_cols = len(grid[0]) if max_rows > 0 else 0
    neighbours = []

    if direction == 'up':
        for k in range(1, size + 1):
            if i - k >= 0:  #ensure not moving above the grid
                neighbours.append(grid[i - k][j])
            else:
                break  #went above the top edge of the grid, so stop adding neighbors

    elif direction == 'down':
        for k in range(1, size + 1):
            if i + k < max_rows:  #ensure not moving below the grid
                neighbours.append(grid[i + k][j])
            else:
                break  #went below the bottom edge of the grid, so stop adding neighbors

    elif direction == 'left':
        for k in range(1, size + 1):
            if j - k >= 0:  #ensure not moving to the left of the grid
                neighbours.append(grid[i][j - k])
            else:
                break  #went to the left of the left edge of the grid, so stop adding neighbors

    elif direction == 'right':
        for k in range(1, size + 1):
            if j + k < max_cols:  #ensure not moving to the right of the grid
                neighbours.append(grid[i][j + k])
            else:
                break  #went to the right of the right edge of the grid, so stop adding neighbors
    return neighbours
"""

def create_framework(n, k):
    
    directions = {1: 'x', 2:'left', 3:'right', 4:'bidirectional'}
    prob_args = {}
    prob_attacks = {} #inside here we also store the probabilities of supports (they are uniqueliy identified by (a,b), as we dont allow support(a,b) and att(a,b))

    probabilities_asp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #weights = [4]* 9 + [1]
    weights = [10]*9 + [0.1]


    p_being_picked_in_extension = 0.04
    query = ''
    extension = {}
    id_atck = 0


    #being_attacked = random.random() < p_being_attacked #if true then it is attacked, if false it is an attacker


    visited_edges_in_grid = []

    for i in range(0, n):
        for j in range(0, k):
            #arg_probability = random.sample(probabilities,1)[0]

            # Arguments
            arg_probability = random.choices(probabilities_asp, weights, k=1)[0]
            prob_args[grid[i][j]] = arg_probability
            #prob_args_asp[grid[i][j]] = probabilities_asp[str(arg_probability)]

            select_in_extension = random.random() < p_being_picked_in_extension
            if select_in_extension:
                extension[grid[i][j]] = 'in'

            # Attacks
            immediate_neighs = immediate_neighbours(i,j, grid)
            possible_edges = [[grid[i][j], neigh] for neigh in immediate_neighs]
            new_edges = [edge for edge in possible_edges if edge not in visited_edges_in_grid] # new edges which we can consider for new attacks

            for edge in new_edges:
                #updated visited_edges_in_grid
                visited_edges_in_grid.append([edge[0],edge[1]])
                visited_edges_in_grid.append([edge[1],edge[0]])

                #coin = random.choice([True,False]) #if true, an attack, if false, a support

                # Define the weights for True and False
                weights_coin = [0.9, 0.1]

                # Choose based on the defined weights
                coin = random.choices([True, False], weights=weights_coin, k=1)[0]

                if coin:
                    pick = random.sample(range(1,5),1)[0]

                    if directions[pick] != 'x':
                        #selection_set = neighbourhood(i,j,directions[pick],4)
                        
                        if directions[pick] == 'left':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[1]
                            prob_attack = [attacker, edge[0], atck_probability]
                            attack = [attacker, edge[0]]
                            prob_attacks[id_atck] = prob_attack
                            attacks.append(attack)
                            id_atck += 1

                        elif directions[pick] == 'right':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[0]
                            prob_attack = [attacker, edge[1], atck_probability]
                            attack = [attacker, edge[1]]
                            prob_attacks[id_atck] = prob_attack
                            attacks.append(attack)
                            id_atck += 1

                        elif directions[pick] == 'bidirectional':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[0]
                            prob_attack = [attacker, edge[1], atck_probability]
                            attack = [attacker, edge[1]]
                            prob_attacks[id_atck] = prob_attack
                            attacks.append(attack)
                            id_atck += 1

                            atck_probability2 = random.choices(probabilities_asp, weights, k=1)[0] #
                            prob_attack2 = [edge[1], edge[0], atck_probability2]
                            attack2 = [edge[1], edge[0]]
                            prob_attacks[id_atck] = prob_attack2
                            attacks.append(attack2)
                            id_atck += 1
                else:

                    pick = random.sample(range(1,5),1)[0]

                    if directions[pick] != 'x':
                        #selection_set = neighbourhood(i,j,directions[pick],4)
                        
                        if directions[pick] == 'left':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[1]
                            prob_attack = [attacker, edge[0], atck_probability]
                            attack = [attacker, edge[0]]
                            prob_attacks[id_atck] = prob_attack
                            supports.append(attack)
                            id_atck += 1

                        elif directions[pick] == 'right':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[0]
                            prob_attack = [attacker, edge[1], atck_probability]
                            attack = [attacker, edge[1]]
                            prob_attacks[id_atck] = prob_attack
                            supports.append(attack)
                            id_atck += 1

                        elif directions[pick] == 'bidirectional':
                            atck_probability = random.choices(probabilities_asp, weights, k=1)[0] #
                            attacker = edge[0]
                            prob_attack = [attacker, edge[1], atck_probability]
                            attack = [attacker, edge[1]]
                            prob_attacks[id_atck] = prob_attack
                            supports.append(attack)
                            id_atck += 1

                            atck_probability2 = random.choices(probabilities_asp, weights, k=1)[0] #
                            prob_attack2 = [edge[1], edge[0], atck_probability2]
                            attack2 = [edge[1], edge[0]]
                            prob_attacks[id_atck] = prob_attack2
                            supports.append(attack2)
                            id_atck += 1




    print("attacks", attacks)
    print("supports", supports)
                    
    print("prob_args", prob_args)
    print()
    print("prob_attacks", prob_attacks)

    flattened_grid = [item for sublist in grid for item in sublist]
    query = random.sample(flattened_grid,1)[0] 
                    
    return prob_args, prob_attacks, attacks, supports, query, extension


def create_instance_file(arguments, pargs, attacks, supports, patts, query, extension, out_filename):
    """
    Print the given framework in ASP format.
    """
    print("out filnemae", out_filename)

    if not os.path.exists(os.path.dirname("instance_set/")):
        os.makedirs(os.path.dirname("instance_set/"))

    
    with open("instance_set/"+out_filename, 'w') as out:
        for arg in arguments:
            out.write("arg(" + arg + ").\n")
        for arg, parg in pargs.items():
            out.write("p(" + str(arg) +","+ str(parg)+ ").\n")
        for att in attacks:
            out.write("att("+str(att[0])+","+att[1]+").\n")
        for sup in supports:
            out.write("support("+str(sup[0])+","+sup[1]+").\n")
        for at, patt in patts.items():
            out.write("p(" + str(at) + "," + patt[0] + ","+ patt[1]+","+ str(patt[2])+").\n")
        for elem in extension:
            out.write("in("+elem+").\n")
        #out.write("query(" + str(query) + ").")
    out.close()


# main()
k = int(sys.argv[1])
n = int(sys.argv[2])
id_instance = int(sys.argv[3])

n_sentences = k * n #arguments in the grid

print()
print("total n arguments: ", n_sentences )

arguments = initialise(n_sentences)

create_grid(k,n)
print_grid(grid)


p1, p2, att, sup, q, ext = create_framework(n,k)
print("prob args", p1)
print("prob attacks", p2)
print("attacs", att)
print("extension", ext)
print("query", q)

create_instance_file(sorted(arguments), p1, att, sup, p2, q, sorted(ext), "k"+str(k)+"_"+"n"+str(n)+"_q"+str(q)+"_"+str(id_instance)+".lp")

