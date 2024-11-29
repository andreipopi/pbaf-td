import os
import statistics

def count_timeouts(filename):
    timeout_count = 0
    instance_count = 0
    memoryout_count = 0
    memoryout_by_kn = {}
    timeout_by_kn = {}
    running_times_by_kn = {}
    running_times_by_k = {}
    timeouts_by_k = {}

    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.split(',')
                instance_info = parts[0].strip()
                k = instance_info.split('_')[0][1:]
                n = instance_info.split('_')[1][1:]

                if k == 'unknown' or n == 'unknown':
                    continue

                k = int(k)
                n = int(n)
                instance_count += 1

                if 'TIMEOUT' in line:
                    timeout_count += 1
                    timeout_by_kn[(k, n)] = timeout_by_kn.get((k, n), 0) + 1
                    timeouts_by_k[k] = timeouts_by_k.get(k, 0) + 1

                elif 'MEMORYOUT' in line:
                    memoryout_count += 1
                    memoryout_by_kn[(k, n)] = memoryout_by_kn.get((k, n), 0) + 1

                else:
                    time_part = line.split('#')[-1].strip()
                    time = float(time_part.split(':')[-1].strip())
                    running_times_by_kn.setdefault((k, n), []).append(time)
                    running_times_by_k.setdefault(k, []).append(time)

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
            median_times[key] = None
    return median_times

files = [
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-dpbaf-sadm/td-python-dpbaf-sadm_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-dpbaf-dadm/td-python-dpbaf-dadm_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-dpbaf-cadm/td-python-dpbaf-cadm_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-spbaf-cadm/td-python-spbaf-cadm_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-spbaf-dadm/td-python-spbaf-dadm_results.txt",
    "/Users/andrei/Documents/GitLab/pbaf-treedec/Run/compiled_results_rerun2/td-python-spbaf-sadm/td-python-spbaf-sadm_results.txt"
]

for file in files:
    (total_timeouts, total_memoryouts, instance_count, timeout_by_kn, memoryout_by_kn, 
     running_times_by_kn, running_times_by_k, timeouts_by_k) = count_timeouts(file)
    
    print(f"File: {os.path.basename(file)}")
    
    '''
    print(f"Total number of TIMEOUTs: {total_timeouts} / {instance_count}")
    print(f"Total number of MEMORYOUTs: {total_memoryouts} / {instance_count}")
    '''
    for kn, count in sorted(timeout_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        print(f"k={kn[0]}, n={kn[1]}: {count} TIMEOUTs")
    
    print("\n")
    

    median_times_by_kn = calculate_median_times(running_times_by_kn)
    print("Median running times by (k, n):")
    for kn, median_time in sorted(median_times_by_kn.items(), key=lambda x: (x[0][0], x[0][1])):
        if median_time is not None:
            print(f"k={kn[0]}, n={kn[1]}: {median_time:.2f} seconds")
        else:
            print(f"k={kn[0]}, n={kn[1]}: No valid running times")
    
    print("\n")
    
    median_times_by_k = calculate_median_times(running_times_by_k)


    '''
    print("Median running times by k:")
    for k, median_time in sorted(median_times_by_k.items()):
        if median_time is not None:
            print(f"k={k}: {median_time:.2f} seconds")
        else:
            print(f"k={k}: No valid running times")

    print("Total TIMEOUTs by k:")
    for k, count in sorted(timeouts_by_k.items()):
        print(f"k={k}: {count} TIMEOUTs")
    '''
    
    print("\n")