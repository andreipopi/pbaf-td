# python probableSolver.py instance.lp
from ast import arguments
from input_output import *
from spbaf_dadm import *
from itertools import chain, combinations

import sys

def process_input_output(instance):

    arguments_digits = InputOutput.args_char_to_digit(instance)
    attacks_digits = InputOutput.attacks_char_to_digit(instance)
    nArgs = len(arguments_digits)
    nAtts = len(attacks_digits)
    htdInstance = InputOutput.to_htd_format(nArgs, nAtts)

    #print(htdInstance)
    htdOutput = InputOutput.call_htd(htdInstance)
    print(htdOutput)
    print("Largest bag size: ", InputOutput.get_largest_bag_size())
    print("constructed TD")
    InputOutput.extract_sections(htdOutput) #GET POST ORDER TRAVERSAL OF HTD
    InputOutput.stringTraversalToDict()
    #InputOutput.printDictionary(InputOutput.traversal_dict)
    InputOutput.digitsToLiterals(InputOutput.traversal_dict)
    # We want an ordered traversal, where each node to traverse is a line of the shape:
    # [type, ID, [bag], [elements rem/intro], [[edge1], [edge2]], [childrenIDS]]
        #InputOutput.printDictionary(InputOutput.getTraversalDict())
    #print("-------------------------------------------------------")
    Algorithm.setProbs(InputOutput.getProbabilities()[0], InputOutput.getProbabilities()[1])
    #print(Algorithm.prob_args)
    #print(Algorithm.prob_attacks)
    Algorithm.set_extension(InputOutput.extract_extension())
    Algorithm.set_relations(InputOutput.get_relations()[0],InputOutput.get_relations()[1],InputOutput.get_relations()[2],InputOutput.get_relations()[3])
    #preprocess


if len(sys.argv) == 1:
    print("-----------------------ProbableSolver-----------------------")
    print("Try passing an .lp instance!")

elif len(sys.argv) == 2:
    print("Specify s or d.")

elif len(sys.argv) == 3:
    #INPUT OUTPUT-------------------------
    #GET INSTANCE TO htd FORMAT

    script = ""
    if sys.argv[2] == 's':
        script = "../preprocessing/preprocess-sbaf.py"
    elif sys.argv[2] == 'd':
        script = "../preprocessing/preprocess-dbaf.py"
    
    instance = sys.argv[1]

    # Pre-processing of instance
    result = subprocess.run([sys.executable, script, instance], cwd="../verification/preprocessing/", check=True, text=True, capture_output=True)
    #---end pre processing of instance-----

    # parsing/extracting/setting up the content
    process_input_output(instance)
    #print(Algorithm.prob_args)
    #print("classical attacks: ",Algorithm.attacks)
    #print("classical supports: ", Algorithm.supports)
    #print("derived attacks: ", Algorithm.datts)
    #print("derived supports: ", Algorithm.dsus)
    #print(Algorithm.prob_args)
    #print(Algorithm.prob_attacks)
    #--------------------------------------

    #for each node in traversal:
    n_nodes = len(InputOutput.getTraversalDict().items())
    count = 0
    for key, value in InputOutput.getTraversalDict().items():
        count += 1
        if value[1] == "leaf" and value[3]== []: #and not last node, but it seems the last (the root) is a remove. need some cleanup
            print()
            print("NODE:", key, "leaf")
            table = Algorithm.leaf_node()
            Algorithm.store_table(key, table)
            for row in table:
                print(row)
        elif value[1] == "intro":
           
            
            print()
            print("NODE:", key, " intro", value[0])
            print("introduced", value[2])
            # bag, introduced, edges, child
            table = Algorithm.introduce_node(value[0], value[2], value[4], Algorithm.table_at_key(value[6][0]))
            Algorithm.store_table(key, table ) #value[6][0] is the key of child
            for row in table:
               print(row)
            if table == []: #no row survived and the result probability is 0
                print("RESULT:", 0)
                break
            
           
            

        elif value[1] == "rem":# and not count == n_nodes: #in traversal the last remove node is the root
            print()
            
            print("NODE:", key, " rem - ", value[0] )
            #if not count == n_nodes:
            #    table =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]), "remove_node")
            #else:
            #    table, result =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]), "root")
            #    print("final result", result)
            #if value[0] == []: # when bag is empty, we must use penalties, otherwise everything gets summed together.
            #if not count == n_nodes:
            table =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]))
            #else:
            #    table, result =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]),"root")
            #else:
            #    table =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]))
            #for row in table:
            #    print(row)
            #table =  Algorithm.remove_node(value[0], value[2], Algorithm.table_at_key(value[6][0]))
            #table =   Algorithm.table_at_key(value[6][0]) #if use this you can see all solutions
            Algorithm.store_table(key,table)
            #print("output table")
            for row in table[0:20]:
               print(row)
            
            if table == []: #no row survived and the result probability is 0
                print("RESULT:", 0)
                break
            elif count == n_nodes:
                print("RESULT", float(table[0][-1]))

            
        elif value[1] == "join":
            print()
            print("NODE:", key, " join")
            #print("children: ", value[-1])

           # print("left", Algorithm.table_at_key(value[-1][0]))
           # print("right", Algorithm.table_at_key(value[-1][1]))
            table =Algorithm.join_node(value[0], Algorithm.table_at_key(value[5][0]),Algorithm.table_at_key(value[5][1]), value[3])
            #table = Algorithm.table_at_key(value[5][0])
            Algorithm.store_table(key, table)
            for row in table:
                print(row)
            if table == []: #no row survived and the result probability is 0
                print("RESULT:", 0)
                break
        #else:
        #    print("NODE:", key, " root")
            #print("must be root or leaf")

    
    #print("")
    #print("")
    #print("STORED TABLES--------------------------")
    #Algorithm.print_tables()

    #here we remove the derived stuff we added to the instance.
    InputOutput.clean_instance(instance)


#print(Algorithm.prob_args)
#print(Algorithm.prob_attacks)