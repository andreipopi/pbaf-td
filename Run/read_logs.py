import os

def extract_and_compile_results(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Traverse each subfolder in the input folder
    for solver in sorted(os.listdir(input_folder)):  # Sort the solver directories
        solver_path = os.path.join(input_folder, solver)

        results = []

        # Continue only if it is a directory
        if os.path.isdir(solver_path):
            output_subfolder = os.path.join(output_folder, solver)
            # Create subfolder in output directory
            if not os.path.exists(output_subfolder):
                os.makedirs(output_subfolder)
                
            # File to write the compiled results
            output_file_path = os.path.join(output_subfolder, f"{solver}_results.txt")
            with open(output_file_path, 'w') as output_file:
                # Sort files alphabetically before processing
                for file_name in sorted(os.listdir(solver_path)):
                    if file_name.endswith('.log'):
                        file_path = os.path.join(solver_path, file_name)
                        
                        try:
                            # Read from the log file
                            with open(file_path, 'r') as file:
                                lines = file.readlines()
                                result_lines = [line.strip() for line in lines if 'RESULT' in line]
                                max_bag_lines = [line.strip() for line in lines if 'Largest bag size' in line]
                                timeout_lines = [line.strip() for line in lines if 'Maximum CPU time exceeded' in line] 
                                memoryout_lines = [line.strip() for line in lines if 'Maximum VSize exceeded' in line] 
                                models_lines = [line.strip() for line in lines if 'Models' in line] 
                                user_time_milliseconds = [line.strip() for line in lines if 'total CPU user time (s)' in line] 

                                instance_name = os.path.splitext(file_name)[0]


                                '''
                                if result_lines and timeout_lines == []:
                                    last_result_line = result_lines[-1]
                                    output_file.write(f"{instance_name}, {solver}, {last_result_line}\n")
                                else:
                                    # Write TIMEOUT if no RESULT line is found
                                    output_file.write(f"{instance_name}, {solver}, TIMEOUT\n")
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")


                            '''     # Extract k, n, and index values
                                parts = instance_name.split('_')
                                k_value = int(parts[0][1:])  # Assumes format is k<number>
                                n_value = int(parts[1][1:])  # Assumes format is n<number>
                                index_value = int(parts[3].split('.')[0])  # Corrected to split by '.' and take the first part

                                max_bag_size = "unknown"

                                print(max_bag_lines)
                                if max_bag_lines != []:
                                    max_bag_size = max_bag_lines[0].split(":")[-1]
                                if result_lines:
                                    last_result_line = result_lines[-1]
                            
                                    results.append((k_value, n_value, index_value, f"{instance_name}, {max_bag_size}, {solver}, {last_result_line}, {user_time_milliseconds[0]}\n"))
                                
                                elif models_lines and timeout_lines == [] and memoryout_lines == []:
                                    last_result_line = models_lines[-1]
                                    results.append((k_value, n_value, index_value, f"{instance_name},{max_bag_size}, {solver}, {last_result_line}, {user_time_milliseconds[0]}\n"))

                                elif timeout_lines != []:
                                    results.append((k_value, n_value, index_value, f"{instance_name},{max_bag_size},  {solver}, TIMEOUT\n"))
                                elif memoryout_lines != []:
                                    results.append((k_value, n_value, index_value, f"{instance_name},{max_bag_size},  {solver}, MEMORYOUT\n"))

                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")

        # Sort results by k, n, and index
        results.sort(key=lambda x: (x[0], x[1], x[2]))

        # Write sorted results to file
        with open(output_file_path, 'w') as output_file:
            for _, _, _, line in results:
                output_file.write(line)

# Set the path to your input folder and define the output folder
input_folder = '/Users/andrei/Documents/GitLab/pbaf-treedec/Run/results_rerun2'
output_folder = 'compiled_results_rerun2'

# Call the function
extract_and_compile_results(input_folder, output_folder)