# operating on the TD of the PRIMAL graph of problem instance.
from copy import copy
from heapq import merge
from itertools import chain, combinations
from tokenize import group
from input_output import *
import copy
from fractions import Fraction
import pandas as pd

class Algorithm:
    prob_args = []
    prob_attacks = [] #probabilities of supports are included, assuming no support(a,b) if att(a,b) and viceversa
    childrenList = []
    tables = {}

    #to differentiate between attacks and supports
    #intuitively, when we create the new guesses on edges, we either include or not include the edge, and if we include, we must include in the right place i.e. Ra, or Rs.
    attacks = [] #only contains classical attacks
    supports = []#only contains classical supports
    datts = [] #only contains derived attacks (they get derived in the introduce)
    dsus = []  #analogous

    labelling = {}

    #0   1     2     3      4      5    6    7 8 9 10 11 12
    #[a, atck, sprt, dsprt, datck, Cds, Cda, I,D,U,Cd,Cu, P]

    @classmethod
    def leaf_node(cls):
               #[G, Ra,I, D, U, Cd,Cu, Rs, Da, Ds, P]
               #[0, 1, 2, 3, 4, 5, 6,  7,  8,  9,  P]
        return [[[],[],[],[],[],[],[], [],[],[],1]]  
                                                   
    @classmethod
    def introduce_node(cls, bag_elems, intro_elem, edges, child_tab):
        """
        Description: creates a table for introduction nodes
        Parameters:
            edges (list): list of edges "in the bag" (already returned by htd)
            bag_elems (list): vertices in the bag
            intro_elem (list): introduced vertex; nice TD, so just one. e.g. ['a']
            child_tab (list): a list of lists containing the child rows
        Returns: returns table (list).
        """

        table = []
        prob_introduced = Fraction(cls.prob_args[intro_elem[0]])
        
        for c_row in child_tab: # [[[],[],[],[],[],[],[], [],[],[],1]]  
            graph_prime = copy.deepcopy(c_row[0]) #G'
            row = copy.deepcopy(c_row)# G',L',C',P'

            #G+A
            graph_prime.append(str(intro_elem[0]))
            P = Fraction(c_row[-1]) * Fraction(cls.prob_args[intro_elem[0]]) # only arg contributed at this point

            #for guesses on subgraph,remove derived (datts and dsus) from possible edges
            classic_attacks_supports = []
            for e in edges:
                if cls.is_attack(e) or cls.is_support(e):
                    if e not in classic_attacks_supports:
                        classic_attacks_supports.append(e)

            potential_edges = cls.valid_for_contribution(graph_prime, classic_attacks_supports, intro_elem)# classical attacks and supports incident to introduced, and both ends in subgraph
            edge_guesses = list(cls.powerset(potential_edges))
            edge_guesses = cls.check_edge_guesses(potential_edges, edge_guesses) # remove guesses that didnt guess in attacks/supports with P=1, note that then an edge_guess can still include both attacks and supports, but does not exclude an attack wih P=1.

            if edge_guesses != []:
                for e_guess in edge_guesses: 

                    P_with_args = P
                    for pe in potential_edges:
                        if pe in e_guess:
                            P_with_args = P_with_args * Fraction(cls.prob_attacks[str(pe[0])+"-"+str(pe[1])])
                        else:
                            P_with_args = P_with_args * (1-Fraction(cls.prob_attacks[str(pe[0])+"-"+str(pe[1])]))

                    row_copy = copy.deepcopy(row) 
                    row_copy[0] = graph_prime #has been extended with introduced argument


                    # each attack/support in the guess needs to be inserted either in Ra, or in Rs
                    for e in e_guess:
                        if cls.is_attack(e):
                            row_copy[1].append(list(e)) #Ra
                        elif cls.is_support(e):
                            row_copy[7].append(list(e)) #Rs
                    
                    row_copy[-1] = P_with_args

                   # 1) compute transitive derived new supports
                    derived_supports = cls.transitive_relation(row_copy[7], row_copy[9])
                    for der_sup in derived_supports:
                        row_copy[9].append(der_sup)  # 2) add derived supports to row[9]

                    # 3) compute derived(supported in the case of sbaf) attacks
                    #                                                  Ra        Rs            Ds           Da
                    derived_attacks = cls.compute_supported_attacks(row_copy[1], row_copy[7], row_copy[9],row_copy[8])
                    
                    # uncomment for d-PBAF
                    #implicit_attacks = cls.compute_implicit_attacks(row_copy[1], row_copy[7], row_copy[9],row_copy[8])
                    #if implicit_attacks != None and implicit_attacks != []:
                    #    for att in implicit_attacks:
                    #        derived_attacks.append(att)
                    
                    #print("more_attacks", implicit_attacks)
                    
                    for der_att in derived_attacks:
                        row_copy[8].append(der_att) # 4) add derived attacks to row[8]

                    #                       Ra         Da             I           intro elem
                    if cls.conflict_free_baf(row_copy[1], row_copy[8],row_copy[2], intro_elem[0]) and intro_elem[0] in cls.labelling.keys():
                    #def safe_baf(cls, attacks,  datts,       supports,     dsus,       in_set, introduced_elem):
                    #if cls.safe_baf(row_copy[1], row_copy[8], row_copy[7], row_copy[9], row_copy[2], intro_elem[0]):
                        row_I_plus = copy.deepcopy(row_copy) 
                        row_I_plus[2].append(intro_elem[0])
                        defcheck_prime = row_I_plus[5]
                        row_I_plus[5] = cls.check_defeated(bag_elems, row_I_plus[1], row_I_plus[8], row_I_plus[2], defcheck_prime )
                        #print("row i pluse", row_I_plus)
                        if row_I_plus[5] != -1:

                            table.append(row_I_plus)


                    if intro_elem[0] not in cls.labelling.keys():
                        row_D_plus = copy.deepcopy(row_copy) 
                        row_D_plus[3].append(intro_elem[0])
                        defcheck_prime = row_D_plus[5]
                        row_D_plus[5] = cls.check_defeated(bag_elems, row_D_plus[1], row_D_plus[8], row_D_plus[2], defcheck_prime )
                        #print(row_D_plus)
                        if row_D_plus[5] != -1:
                            table.append(row_D_plus)

                    if intro_elem[0] not in cls.labelling.keys():
                        #if cls.labelling[intro_elem[0]] == 'undec':
                        #U+a
                        row_U_plus = copy.deepcopy(row_copy) 
                        row_U_plus[4].append(intro_elem[0])
                        undeccheck_prime = row_U_plus[6]
                        row_U_plus[6] = cls.check_undecided(bag_elems, row_U_plus[1], row_U_plus[4], undeccheck_prime )
                        #print(row_U_plus)
                        table.append(row_U_plus)
            
            else: #there are no "good" edges to contribute, and P stays as computed for intro_elem (above before if check)
                        row_copy = copy.deepcopy(row)
                        row_copy[0] = graph_prime #has been extended with introduced argument
                        row_copy[-1] = P
                        #I+a
                        #                       Ra            Da             I           intro elem
                        if cls.conflict_free_baf(row_copy[1], row_copy[8],row_copy[2], intro_elem[0]) and intro_elem[0] in cls.labelling.keys():
                        #if cls.safe_baf(row_copy[1], row_copy[8], row_copy[7], row_copy[9], row_copy[2], intro_elem[0]):

                            row_I_plus = copy.deepcopy(row_copy) 
                            row_I_plus[2].append(intro_elem[0])
                            defcheck_prime = row_I_plus[5]
                            row_I_plus[5] = cls.check_defeated(bag_elems, row_I_plus[1], row_I_plus[8], row_I_plus[2], defcheck_prime )
                            #print(row_I_plus)
                            if row_I_plus[5] != -1:

                                table.append(row_I_plus)
                        
                        if intro_elem[0] not in cls.labelling.keys():
                            #D+a
                            row_D_plus = copy.deepcopy(row_copy) 
                            row_D_plus[3].append(intro_elem[0])
                            defcheck_prime = row_D_plus[5]
                            row_D_plus[5] = cls.check_defeated(bag_elems, row_D_plus[1], row_D_plus[8],row_D_plus[2], defcheck_prime )
                            #print(row_D_plus)
                            if row_D_plus[5] != -1:

                                table.append(row_D_plus)

                        if intro_elem[0] not in cls.labelling.keys():
                            #U+a
                            row_U_plus = copy.deepcopy(row_copy) 
                            row_U_plus[4].append(intro_elem[0])
                            undeccheck_prime = row_U_plus[6]
                            row_U_plus[6] = cls.check_undecided(bag_elems, row_U_plus[1], row_U_plus[4], undeccheck_prime )
                            #print(row_U_plus)
                            table.append(row_U_plus)
                            #dont append with not in I not in D not in U #[['a'], [], [], [], [], [], [], '0.100']
            #G_a
            if prob_introduced != 1:
                row_copy = copy.deepcopy(row) 
                #print("then we can create rows without a")
                #G-a,   everything stays the same. Update P w.r.t to arg only
                P = Fraction(c_row[-1]) * (1- Fraction(cls.prob_args[intro_elem[0]])) # P = 1-p(a)

                row_copy[-1] = P
                if intro_elem[0] not in cls.labelling.keys():   
                    table.append(row_copy) #[[G'], [R'], [I'], [D'], [U'], [Cd], [Cu], [CWs] P]  
             
        return table

    @classmethod
    def remove_node(cls, bag_elems, removed_elem, child_tab):

        #table = []
        pandas_table = []

        #1) Filter #Todo
        #2) G,R,I,D,U, Cd, Cu \{a}
        table_minus_rem = []
        filtered_table = cls.sigma_forget(bag_elems, child_tab, removed_elem[0])
        #print("filtered child")
        #for r in filtered_table:
        #    print(r)
        print("removed element", removed_elem[0])
        for row in filtered_table:
            table_minus_rem.append(cls.minus_removed(removed_elem[0], row))
        #print("len graphs", len(considered_graphs))
        print("tableminusrem")
      
        if table_minus_rem != []:

            #pandas approach of merging
            df = pd.DataFrame(table_minus_rem)
            # Create 'key' as a tuple for each row, then use it as an index
            df['key'] = df.apply(lambda x: tuple(x[:10]), axis=1)
            df.set_index('key', inplace=True)
            df.index = df.index.map(str)
            df = df.drop(columns=list(range(10)))  # Drop original columns after using them to create the key
            #df[10] = pd.to_numeric(df[10], errors='coerce')# this was only necessary when dealing with floats, which were stored as strings and had to be converted into numbers in pandas
            grouped = df.groupby('key', sort = False).agg({10:'sum'}).reset_index()

            # print(grouped)

            grouped['as_list'] = [ast.literal_eval(idx) for idx in grouped['key']]
            grouped.drop(columns=['key'], inplace=True)
            cols = ['as_list'] + [col for col in grouped.columns if col != 'as_list']
            grouped = grouped[cols]
            #print("as list")
            #print(grouped)
            grouped = grouped.to_numpy().tolist()
            #print(grouped)
            #print(merged[0])
            for r in grouped:
                new_row = []
                for x in r[0]:
                    new_row.append(x)
                new_row.append(r[1])
                pandas_table.append(new_row)

            #print("pandas table")
            #for r in pandas_table:
            #    print(r)
            #print("end table")

        '''
        #old merging
        #3) #core in remove node = [[G],[R],[I],[D],[U],[Cd],[Cu]]
        cores = []
        for row in table_minus_rem:
            core = copy.deepcopy(row[0:-1])
            if core not in cores:
                cores.append(core)
        print("cores", cores)
        #print("cores", cores)
        for core in cores:
            P = 0
            for row in table_minus_rem:
                if cls.equivalent_rows(core,row[0:-1],"remove"):
                        P = P + float(row[-1])
            core.append(str(cls.format_float(P)))
            #core.append((cls.format_float(P)))
            table.append(core)
        '''
        return pandas_table

    @classmethod
    def join_node(cls, bag_elems, tab_left, tab_right, edges):
        #pd.set_option('display.max_columns', None)  # No limit on the number of displayed columns
        #pd.set_option('display.max_rows', None)  # No limit on the number of displayed rows
        #pd.set_option('display.max_colwidth', None)  # No limit on the width of each column value
        #pd.set_option('display.width', 1000)  # Expand the total width of the output display
        #print(tab_left)
        #print("tab left")
        #for r in tab_left:
        #    print(r)
        #print("tab right")
        #for r in tab_right:
        #    print(r)

        def create_dataframe(tab):
        # Sort each row and immediately create the key
            sorted_tab = [cls.sort_list_of_lists(row) for row in tab]
            df = pd.DataFrame(sorted_tab)
            # Create 'key' as a tuple for each row, then use it as an index
            df['key'] = df.apply(lambda x: tuple(x[:5].tolist()+[x[7]]), axis=1) # our key becomes G Ra I D U _ _  Rs _ _
            df.set_index('key', inplace=True)
            df.index = df.index.map(str)
            df = df.drop(columns=list(range(5)))  # Drop original columns after using them to create the key
            df = df.drop(columns=7)
            return df

        left = create_dataframe(tab_left)
        right = create_dataframe(tab_right)        
        #print(right)
        #print(left)
        #print("merged")

        merged = pd.merge(left, right, on='key', how='inner')
        #print(merged)
        #print("merged",merged)

        def merge_lists(list_x,list_y):
            combined_list = list_x
            # Add elements from list_y only if they are not already in combined_list
            for item in list_y:
                if item not in combined_list:
                    combined_list.append(item)
            return combined_list

        def process_row(row):
            row['5'] = list(set(row['5_x'] + row['5_y']))
            row['6'] = list(set(row['6_x'] + row['6_y']))
            row['8'] = merge_lists(row['8_x'],row['8_y'])
            row['9'] = merge_lists(row['9_x'],row['9_y'])
            row['10'] = Fraction(row['10_x']) * Fraction(row['10_y'])
            return row
        merged = merged.apply(process_row, axis=1)
        merged.drop(columns=['5_x', '5_y', '6_x', '6_y','8_x', '8_y','9_x', '9_y', '10_x', '10_y'], inplace=True)
        merged.reset_index(drop=False, inplace=True)  # This adds a new integer index and drops the existing one

        merged['as_list'] = [ast.literal_eval(idx) for idx in merged['key']]
        merged.drop(columns=['key'], inplace=True)
        cols = ['as_list'] + [col for col in merged.columns if col != 'as_list']
        merged = merged[cols]
       
        merged = merged.to_numpy().tolist()
        #print("merged to list")
        #for r in merged:
        #    print(r)

        #print(merged[0])
        pandas_table = []
        for r in merged:
            new_row = []
            
            for x in r[0][:5]:
                new_row.append(x)
            new_row.append(r[1])
            new_row.append(r[2])
            
            new_row.append(r[0][5])
            new_row.append(r[3])
            new_row.append(r[4])

            # in the following, we compute the discount. The discount represents the probability of the common part when two rows are joined.
            discount = 1
            
            # remove derived (datts and dsus) from possible edges
            classic_attacks_supports = []
            for e in edges:
                if cls.is_attack(e) or cls.is_support(e):
                    classic_attacks_supports.append(e)
            # potential edges that could have been picked in guesses of Ra-Rs
            potential_edges = cls.valid_for_contrib_join(r[0][0], classic_attacks_supports)#edges among bag edges that could have been picked in Ra andor Rs


            for arg in bag_elems:
                parg = Fraction(cls.prob_args[arg])
                if arg in r[0][0]:
                        discount = discount * parg
                else:
                        discount = discount * (1- parg)

            for e in potential_edges:
                if cls.is_attack(e):
                    pattck = Fraction(cls.prob_attacks[str(e[0])+"-"+str(e[1])])
                    if e in r[0][1]: #if edge is in R
                            discount = discount * pattck
                    else:
                            discount = discount * (1-pattck)
                elif cls.is_support(e):
                    pattck = Fraction(cls.prob_attacks[str(e[0])+"-"+str(e[1])])
                    if e in r[0][5]: #if edge is in Rs which in this moment is in 5th position: [(['a', 'b', 'c'], [['b', 'c']], ['a'], ['b', 'c'], [], [['a', 'b']]), [], [], [['a', 'c']], [], '1.000000000000000']
                            discount = discount * pattck
                    else:
                            discount = discount * (1-pattck)
                
            new_row.append(Fraction(r[5])/Fraction(discount))

            pandas_table.append(new_row)

        #for r in pandas_table:
        #    print(r)
        print("----------------")
        return pandas_table


#CHECKS & Utils

    #upon removal, filters rows that are not admissible, complete, and that don't match the query extension
    @classmethod
    def sigma_forget(cls, bag_elems, child_tab, removed_elem):
        copy_child_tab = copy.deepcopy(child_tab)
        filtered_child_tab = []

        for row in copy_child_tab:
            
            undecided_but_attacked_by_in = False
            for attack in row[1]:
                if attack[0] in row[2] and attack[1] in row[4]:
                    undecided_but_attacked_by_in = True
            for attack in row[8]:
                if attack[0] in row[2] and attack[1] in row[4]:
                    undecided_but_attacked_by_in = True

            not_true_defeated = removed_elem in row[3] and not removed_elem in row[5] or (removed_elem in row[5] and not removed_elem in row[3]) #G R I D U Cd Cu
            

            # admissible----
            not_admissible = False
            for attack in row[1]:
                if attack[1] == removed_elem and removed_elem in row[2] and attack[0] not in row[3]:    #if removed was attacked by something not in def
                    not_admissible = True
            for attack in row[8]:
                if attack[1] == removed_elem and removed_elem in row[2] and attack[0] not in row[3]:    #if removed was attacked by something not in def
                    not_admissible = True
            #-------------------

            unsafe = False
            all_supports = cls.merge_relations(row[7],row[9])
            for sup in all_supports:
                if sup[1] == removed_elem and removed_elem in row[3] and sup[0] in row[2]:
                    unsafe = True
                if sup[0] == removed_elem and removed_elem in row[2] and sup[1] in row[3]:
                    unsafe = True

            #not_true_undecided = removed_elem in row[4] and not removed_elem in row[6] or (removed_elem in row[6] and not removed_elem in row[4]) #G R I D U Cd Cu

            in_but_attacked_by_undec = False
            for attack in row[1]:
                if attack[0] == removed_elem and removed_elem in row[4] and attack[1] in row[2]:
                    in_but_attacked_by_undec = True
            for attack in row[8]:
                if attack[0] == removed_elem and removed_elem in row[4] and attack[1] in row[2]:
                    in_but_attacked_by_undec = True

            match_query_labelling = True

            not_stable = removed_elem not in row[2] and removed_elem not in row [3]


            not_closed = False
            for support in row[7]:
                if support[1] == removed_elem and removed_elem not in row[2]:
                    not_closed = True
            for support in row[9]:
                if support[1] == removed_elem and removed_elem not in row[2]:
                    not_closed = True 
            
            
            #if value == 'def' and not key in row[3]:
            #            match_query_labelling = False
            #if value == 'undec' and not key in row[4]:
            #            match_query_labelling = False

            #erase rows that didnt add a to the subgraph, but which are required by the labelling
            #required_but_not_in_subgraph = removed_elem in cls.labelling.keys() and removed_elem not in row[0]
            #if required_but_not_in_subgraph:
            #    match_query_labelling = False


            for key,value in cls.labelling.items(): #
                if key in row[0]:
                    if value == 'in' and not key in row[2]:
                        match_query_labelling = False
            for arg in row[0]:
                if arg not in cls.labelling.keys() and arg in row[2]: # if not in extension, but IN
                    match_query_labelling = False
           
            if removed_elem in cls.labelling.keys():
                if cls.labelling[removed_elem] == 'in' and removed_elem not in row[2]:
                    match_query_labelling = False

            # here things get filtered: added or not to the table
            if  not not_closed and not in_but_attacked_by_undec and not undecided_but_attacked_by_in and not not_true_defeated and match_query_labelling and not not_admissible:
                filtered_child_tab.append(row)
            
        return filtered_child_tab


    @classmethod
    def check_defeated(cls, bag_elems, attacks, datts, in_set, def_check_prime):
        def_check = copy.deepcopy(def_check_prime)

        copy1= copy.deepcopy(attacks)
        copy2= copy.deepcopy(datts)

        all_attacks = cls.merge_relations(copy1, copy2)

        for att in all_attacks:
            if att[0] == att[1] and att[0] in in_set:
               return -1
            for elem in bag_elems:
                if (att[0] in in_set and elem == att[1]):
                    print(att[0],"-",att[1])
                    def_check = list(set(def_check).union({elem}))
        return def_check

    @classmethod
    def check_undecided(cls, bag_elems, attacks, undec_set, undec_check_prime):
        undec_check = copy.deepcopy(undec_check_prime)
        for att in attacks:
            for elem in bag_elems:
                if (att[0] in undec_set and elem == att[1]) and elem in undec_set:
                    undec_check = list(set(undec_check).union({elem}))
        return undec_check

    #implicit attacks
    @classmethod
    def compute_implicit_attacks(cls, attacks, supports, derived_supports, derived_attacks):
        new_derivations = []
        all_attacks = cls.merge_relations(attacks, derived_attacks) #Combine supports and derived supports into a single list to consider all relationships
        all_supports = cls.merge_relations(supports, derived_supports)  #Combine supports and derived supports into a single list to consider all relationships

        for att in all_attacks:
            for sup in all_supports:
                if sup[1] == att[1]: #sup = ['a', 'b'], att = ['e', 'b'] then e Da a 
                    der = [att[0],sup[0]]
                    if der not in derived_attacks and der not in new_derivations:
                        new_derivations.append(der)
        return new_derivations

    # 
    @classmethod
    def compute_supported_attacks(cls, attacks, supports, derived_supports, derived_attacks):
        new_derivations = []
        #all_attacks = cls.merge_relations(attacks, derived_attacks) #Combine supports and derived supports into a single list to consider all relationships
        all_supports = cls.merge_relations(supports, derived_supports)  #Combine supports and derived supports into a single list to consider all relationships

        for att in attacks:
            for sup in all_supports:
                if sup[1] == att[0]:        # sup = ['a', 'b'], att = ['b', 'c'] then: a Da c
                    der = [sup[0],att[1]]
                    if der not in derived_attacks and der not in new_derivations:
                        new_derivations.append(der)
        return new_derivations

    # merges arrays of shape [['a','b'],['b','c,']]
    @classmethod
    def merge_relations(cls, relations, der_relations):
        merged = copy.deepcopy(relations)
        for a in der_relations:
            if a not in merged:
                merged.append(a) # Combine supports and derived supports into a single list to consider all relationships
        return merged


    # when given Rs, and Ds, it returns the new transitive derivable supports.
    @classmethod
    def transitive_relation(cls, supports, derived_supports):
        all_supports = cls.merge_relations(supports, derived_supports)  #Combine supports and derived supports into a single list to consider all relationships

        new_derivations = []  # Initialize a list to store new derivations
        derivations = set(tuple(ds) for ds in derived_supports)    # Convert derived supports into a set of tuples for efficient lookup and to avoid duplicates
    
        def find_support(a, b): # Helper function to check if a support relationship (a, b) exists in all_supports
            for support in all_supports:
                if support[0] == a and support[1] == b:
                    return True
            return False

        while True:
            new_found = False  # Flag to check if any new derivations are found in this iteration
            for (a, b) in all_supports:        # Iterate over all pairs of supports
                for (c, d) in all_supports:
                    if b == c: # Check if the second element of the first pair matches the first element of the second pair (transitive rule)
                        if not (a, d) in derivations:  # Check if the derived support (a, d) is not already in the set of derivations
                            if find_support(a, b) and find_support(b, d): # Ensure that both (a, b) and (b, d) supports exist
                                new_derivations.append([a, d])  # Add the new derived support to the list and set
                                derivations.add((a, d))
                                new_found = True  # Set flag to indicate a new derivation was found
            if not new_found:  # If no new derivations were found, exit the loop
                break
        return new_derivations


    # conflict free in baf considers both normal and derived attacks, which in this implementation are kept separate 
    @classmethod
    def conflict_free_baf(cls, attacks, datts, in_set, introduced_elem):
        #print("attacks", attacks, " in_set:", in_set, " intro:",introduced_elem)
        
        all_attacks = cls.merge_relations(attacks, datts)

        for att in all_attacks:
            if att[0] in in_set and introduced_elem==att[1]:
                return False
            if att[1] in in_set and introduced_elem == att[0]:
                return False

        return True



    # S is safe iff there is no argument b such that S attacks b and either S supports b or b in S.
    @classmethod
    def safe_baf(cls, attacks, datts, supports, dsus,  in_set, introduced_elem):
        all_attacks = cls.merge_relations(attacks, datts)
        for att in all_attacks:
            if att[0] in in_set and att[1] == introduced_elem: #if this is the case, then we cannot add b in S
                return False
        return True # return true if conflict free


    # the in_set supports arg if there is a support such that 0 in inset and 1 is arg.
    @classmethod
    def set_supports(cls, supports, dsus, in_set, arg):
        all_supports = cls.merge_relations(supports, dsus)  #Combine supports and derived supports into a single list to consider all relationships

        for s in all_supports:
            if s[1] == arg:
                if s[0] in in_set:
                    return True
        return False
    
    @classmethod
    def equivalent_rows(cls, rowl, rowr, flag):
        equivalent = True
        if set(rowl[0]) != set(rowr[0]): #equivlanet G
            equivalent = False
        #print("sets",rowl[1], "   ", rowr[1] )
        if set(map(tuple,rowl[1])) != set(map(tuple,rowr[1])): #equivalent R map(tuple, rowl[1]) converts each inner list in rowl[1] to a tuple.
            equivalent = False
        if set(rowl[2]) != set(rowr[2]): #equivlanet I
            equivalent = False
        if set(rowl[3]) != set(rowr[3]): #equivlanet D
            equivalent = False
        if set(rowl[4]) != set(rowr[4]): #equivlanet U
            equivalent = False
        #for equivalence in remove nodes
        if flag == "remove":
            if set(rowl[5]) != set(rowr[5]): #equivlanet Cd
                equivalent = False
            if set(rowl[6]) != set(rowr[6]): #equivlanet Cu
                equivalent = False
        return equivalent


    # returns c_row with removed arguments from graph, attacks from R, and so on
    @classmethod
    def minus_removed(cls, removed_elem, c_row):
        rem_row = copy.deepcopy(c_row)
        attacks = []
        supports = []
        datts = []
        dsus = []

        for att in rem_row[1]: 
            attacks.append(att)
        for sup in rem_row[7]: 
            supports.append(sup)
        for datt in rem_row[8]: 
            datts.append(datt)
        for dsu in rem_row[9]: 
            dsus.append(dsu)

        if removed_elem in rem_row[0]: #G
            rem_row[0].remove(removed_elem)
        for edge in attacks:
            if edge[0] == removed_elem or edge[1] == removed_elem:
                rem_row[1].remove(edge) #Ra
        for edge in supports:
            if edge[0] == removed_elem or edge[1] == removed_elem:
                rem_row[7].remove(edge) #Rs
        for edge in datts:
            if edge[0] == removed_elem or edge[1] == removed_elem:
                rem_row[8].remove(edge) #Da
        for edge in dsus:
            if edge[0] == removed_elem or edge[1] == removed_elem:
                rem_row[9].remove(edge) #Dsu
        

        if removed_elem in rem_row[2]:  #I
            rem_row[2].remove(removed_elem)
        if removed_elem in rem_row[3]: #D
            rem_row[3].remove(removed_elem)
        if removed_elem in rem_row[4]: #U
            rem_row[4].remove(removed_elem)  
        if removed_elem in rem_row[5]: #Cd
            rem_row[5].remove(removed_elem) 
        if removed_elem in rem_row[6]: #Cu
            rem_row[6].remove(removed_elem)      
        return rem_row

    #CHECK 3
    #remove guesses that didnt guess in attacks with P=1
    @classmethod
    def check_edge_guesses(cls, potential_edges, guesses):
        good_guesses = [] #those that include attacks with P=1
        if potential_edges != []:
            for guess in guesses:
                bad_guess = False
                for edge in potential_edges:
                    prob_edge = cls.prob_attacks[str(edge[0])+"-"+str(edge[1])]
                    if prob_edge == "1" and edge not in list(guess):
                        bad_guess = True
                if not bad_guess:
                    good_guesses.append(guess)
        else:
            return []
        return good_guesses

    #CHECK 2
    # returns edges incident to introduced, and both ends in graph
    @classmethod
    def valid_for_contribution(cls, graph, edges, introducedElem): #e.g. ['a','b']
        potential_edges = []
        for edge in edges: #edges "in the bag"
            ok = (edge[0] in graph and edge[1] in graph) and (edge[0] == introducedElem[0] or edge[1] ==introducedElem[0])
            if ok:
                potential_edges.append(edge)
        return potential_edges

    #CHECK 4
    # specialised method for join - returns potential edges for this graph
    @classmethod
    def valid_for_contrib_join(cls, graph, edges): #e.g. ['a','b']
        potential_edges = []
        for edge in edges: #edges "in the bag"
            ok = (edge[0] in graph and edge[1] in graph)
            if ok:
                potential_edges.append(edge)
        return potential_edges


    def powerset(iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

    @classmethod
    def setProbs(cls, p1, p2):
        cls.prob_args = p1
        cls.prob_attacks = p2

    @classmethod
    def store_table(cls, key, table):
        cls.tables[key] = table

    @classmethod
    def table_at_key(cls, key):
        return cls.tables[key]

    @classmethod
    def print_tables(cls):
        for key,value in cls.tables.items():
            print("Node ",key,":") 
            for row in value:
                print(row)

    @classmethod
    def set_extension(cls, e):
        cls.labelling = e
        return

    @classmethod
    def set_relations(cls, atts, sups, datts, dsus): #these are used to figure out whether an edge in a node is an attack or a support. We assume it cant be both.
        cls.attacks = atts
        cls.supports = sups
        cls.datts = datts
        cls.dsus = dsus
        return

    
    @classmethod
    def sort_list_of_lists(cls, row):
        sorted_row = []
        for item in row:
            if isinstance(item, list):
                # Define a key function for sorting
                def sort_key(subitem):
                    if isinstance(subitem, list):
                        return tuple(subitem)  # Treat sublists as tuples
                    else:
                        return (subitem,)  # Treat other items as single-element tuples
                # Sort the item using the defined key function
                sorted_item = sorted(item, key=sort_key)
                sorted_row.append(sorted_item)
            else:
                # If the item is not a list, just append it
                sorted_row.append(item)
        return sorted_row

    @classmethod
    def is_attack(cls, edge):
        if edge in cls.attacks:
            return True
        return False

    @classmethod
    def is_support(cls, edge):
        if edge in cls.supports:
            return True
        return False