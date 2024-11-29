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
    timeouts_by_k = {}  # Dictionary to count timeouts by k

    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.split(',')
                instance_info = parts[0].strip()
                k = instance_info.split('_')[0][1:]
                n = instance_info.split('_')[1][1:]
                
                if k.lower() == 'unknown' or n.lower() == 'unknown':
                    continue

                k = int(k)
                n = int(n)
                instance_count += 1
                
                if 'TIMEOUT' in line:
                    timeout_count += 1
                    if (k, n) not in timeout_by_kn:
                        timeout_by_kn[(k, n)] = 1
                    else:
                        timeout_by_kn[(k, n)] += 1
                    if k not in timeouts_by_k:
                        timeouts_by_k[k] = 1
                    else:
                        timeouts_by_k[k] += 1
                
                elif 'MEMORYOUT' in line:
                    memoryout_count += 1
                    if (k, n) not in memoryout_by_kn:
                        memoryout_by_kn[(k, n)] = 1
                    else:
                        memoryout_by_kn[(k, n)] += 1

                else:
                    # Extract running time from the comment section of the line
                    time_part = line.split('#')[-1].strip()
                    time = float(time_part.split(':')[-1].strip())
                    if (k, n) not in running_times_by_kn:
                        running_times_by_kn[(k, n)] = []
                    running_times_by_kn[(k, n)].append(time)
                    if k not in running_times_by_k:
                        running_times_by_k[k] = []
                    running_times_by_k[k].append(time)

    except FileNotFoundError:
        print("File not found. Please check the file path and name.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return (timeout_count, memoryout_count, instance_count, timeout_by_kn, memoryout_by_kn, 
            running_times_by_kn, running_times_by_k, timeouts_by_k)

def calculate_median_times(running_times):
    median_times = {}
    for key, times in running_times.items():
        if times:
            median_times[key] = statistics.median(times)
        else:
            median_times[key] = None  # No valid running times to calculate median
    return median_times

files = [
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-dpbaf-scom/td-python-dpbaf-scom_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-dpbaf-dcom/td-python-dpbaf-dcom_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-dpbaf-ccom/td-python-dpbaf-ccom_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-spbaf-ccom/td-python-spbaf-ccom_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-spbaf-dcom/td-python-spbaf-dcom_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results/td-python-spbaf-scom/td-python-spbaf-scom_results.txt"
]

for file in files:
    (total_timeouts, total_memoryouts, instance_count, timeout_by_kn, memoryout_by_kn, 
     running_times_by_kn, running_times_by_k, timeouts_by_k) = count_timeouts(file)
    
    # Print file title and total counts
    print(f"File: {os.path.basename(file)}")
    print(f"Total number of TIMEOUTs: {total_timeouts} / {instance_count}")
    print(f"Total number of MEMORYOUTs: {total_memoryouts} / {instance_count}")
    
    # Print timeout counts by (k, n)
    for kn, count in sorted(timeout_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        print(f"k={kn[0]}, n={kn[1]}: {count} TIMEOUTs")
    
    print("\n")  # Add a newline for better separation between files

    # Calculate and print median running times by (k, n)
    median_times_by_kn = calculate_median_times(running_times_by_kn)
    print("Median running times by (k, n):")
    for kn, median_time in sorted(median_times_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        print(f"k={kn[0]}, n={kn[1]}: {median_time:.2f} seconds")
    
    print("\n")

    # Calculate and print median running times by k
    median_times_by_k = calculate_median_times(running_times_by_k)
    print("Median running times by k:")
    for k, median_time in sorted(median_times_by_k.items()):
        print(f"k={k}: {median_time:.2f} seconds")

    # Print total timeouts by k
    print("Total TIMEOUTs by k:")
    for k, count in sorted(timeouts_by_k.items()):
        print(f"k={k}: {count} TIMEOUTs")

    print("\n")