import os
import statistics

def count_timeouts(filename):
    timeout_count = 0
    instance_count = 0
    memoryout_count = 0
    memoryout_by_kn = {}

    timeout_by_kn = {}  # Dictionary to count timeouts by k and n

    running_times_by_kn = {}
    running_times_by_k = {}

    try:
        with open(filename, 'r') as file:
            for line in file:
                instance_count += 1
                parts = line.split(',')
                instance_info = parts[0].strip()
                # Parse k and n values from instance_info
                k = int(instance_info.split('_')[0][1:])
                n = int(instance_info.split('_')[1][1:])
                
                if 'TIMEOUT' in line:
                    timeout_count += 1
                    if (k, n) not in timeout_by_kn:
                        timeout_by_kn[(k, n)] = 1
                    else:
                        timeout_by_kn[(k, n)] += 1
                
                elif 'MEMORYOUT' in line:
                    memoryout_count += 1
                    if (k, n) not in memoryout_by_kn:
                        memoryout_by_kn[(k, n)] = 1
                    else:
                        memoryout_by_kn[(k, n)] += 1

                elif not 'MEMORYOUT' in line:
                    #MEDIAN per (k,n)
                    # Extract running time from the comment section of the line
                    time_part = line.split('#')[-1].strip()
                    time = float(time_part.split(':')[-1].strip())
                    if (k, n) not in running_times_by_kn:
                        running_times_by_kn[(k, n)] = []
                    running_times_by_kn[(k, n)].append(time)
                '''
                else:
                    time_part = line.split('#')[-1].strip()
                    time = float(time_part.split(':')[-1].strip())
                    if k not in running_times_by_k:
                        running_times_by_k[k] = []
                    running_times_by_k[k].append(time)



                    elif not 'MEMORYOUT' in line:
                        # Extract running time from the comment section of the line
                        time_part = line.split('#')[-1].strip()
                        time = float(time_part.split(':')[-1].strip())
                        if k not in running_times_by_k:
                            running_times_by_k[k] = []
                        running_times_by_k[k].append(time)
                '''
                
                
                

    except FileNotFoundError:
        print("File not found. Please check the file path and name.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return timeout_count, memoryout_count, instance_count, timeout_by_kn, memoryout_by_kn, running_times_by_kn
    #return timeout_count, memoryout_count, instance_count, timeout_by_kn, memoryout_by_kn, running_times_by_k



def calculate_median_times(running_times_by_kn):
    median_times_by_kn = {}
    for kn, times in running_times_by_kn.items():
        if times:
            median_times_by_kn[kn] = statistics.median(times)
        else:
            "never reach this code cause not added"
            median_times_by_kn[kn] = None  # No valid running times to calculate median

    return median_times_by_kn


def calculate_median_times_by_k(running_times_by_k):
    median_times_by_k = {}
    for k, times in running_times_by_k.items():
        if times:
            median_times_by_k[k] = statistics.median(times)
        else:
            median_times_by_k[k] = None  # No valid running times to calculate median

    return median_times_by_k

'''
files = [
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-acc-rational-efficient-join/td-python-acc-rational-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-ver-rational-efficient-join/td-python-ver-rational-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-acc-real-efficient-join/td-python-acc-real-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-ver-real-efficient-join/td-python-ver-real-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/monolithic-clingo-acc/monolithic-clingo-acc_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/monolithic-clingo-ver/monolithic-clingo-ver_results.txt"
]


'''

'''
files = [
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_additional_small/td-python-acc-rational-efficient-join/td-python-acc-rational-efficient-join_results.txt",
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_additional_small/td-python-acc-real-efficient-join/td-python-acc-real-efficient-join_results.txt",
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_additional_small/monolithic-clingo-count-acc/monolithic-clingo-count-acc_results.txt"
]
'''

'''
files = [
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/monolithic-clingo-count-acc-stable/monolithic-clingo-count-acc-stable_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/td-python-acc-real-efficient-join-stable/td-python-acc-real-efficient-join-stable_results.txt"
]
'''

'''
files = [
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-ver-rational-efficient-join/td-python-ver-rational-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/td-python-ver-real-efficient-join/td-python-ver-real-efficient-join_results.txt",
    "/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results/monolithic-clingo-ver/monolithic-clingo-ver_results.txt"
]
'''
'''
files = [
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/monolithic-clingo-count-acc-complete/monolithic-clingo-count-acc-complete_results.txt",
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/monolithic-clingo-count-acc-stable/monolithic-clingo-count-acc-stable_results.txt",
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/td-python-acc-real-efficient-join-complete/td-python-acc-real-efficient-join-complete_results.txt",
"/Users/andrei/Documents/GitLab/praaf-tree-decomposition/Experiments/Run/compiled_results_dense_stable/td-python-acc-real-efficient-join-stable/td-python-acc-real-efficient-join-stable_results.txt"

]
'''

files = ["/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-dpbaf-sadm/td-python-dpbaf-sadm_results.txt",
"/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-dpbaf-dadm/td-python-dpbaf-dadm_results.txt",
"/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-dpbaf-cadm/td-python-dpbaf-cadm_results.txt",
"/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-spbaf-cadm/td-python-spbaf-cadm_results.txt",
"/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-spbaf-dadm/td-python-spbaf-dadm_results.txt",
"/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun/td-python-spbaf-sadm/td-python-spbaf-sadm_results.txt"]

for file in files:
    total_timeouts,total_memoryouts, instance_count, timeout_by_kn, memoryout_by_kn, running_times_by_kn= count_timeouts(file)
    
    # Print file title and total timeouts
    print(f"File: {os.path.basename(file)}")
    print(f"Total number of TIMEOUTs:", total_timeouts ,"/", instance_count)
    print(f"Total number of MEMORYOUTs:", total_memoryouts ,"/", instance_count)

    
    # Print timeout counts by k and n
    for kn, count in sorted(timeout_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        print(f"k={kn[0]}, n={kn[1]}: {count} TIMEOUTs")

    print("\n")  # Add a newline for better separation between files



    median_times_by_kn = calculate_median_times(running_times_by_kn)
    
    #----per kn---------------------
    
    print("Median running times:")
    for kn, median_time in sorted(median_times_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        #if median_time is not None:
        print(f"k={kn[0]}, n={kn[1]}: {median_time:.2f} seconds")
        #else:
        #    print(f"k={kn[0]}, n={kn[1]}: No valid running times")
    
    #-------------------------


    #-----per k--------------------
    '''
    print("Median running times per k:")
    for k, median_time in sorted(median_times_by_kn.items()):
        print(f"k={k}: {median_time:.2f} seconds")
    '''
    #-------------------------

    print("\n")
