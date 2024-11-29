import sys
from tkinter import E

file_path = sys.argv[1]

# Initialize dictionaries to count instances and unsolved instances for each bag size
total_counts = {}
unsolved_counts = {}

# Read the file and process each line
with open(file_path, 'r') as file:
    for line in file:
        # Split the line by comma and strip any whitespace
        parts = line.split(',')
        bag_size_str = parts[1].strip()
        
        # Ignore the line if bag size is "unknown"
        if bag_size_str.lower() == "unknown":
            continue
        
        bag_size = int(bag_size_str)
        result = parts[3].strip()
        
        # Update the total count for the bag size
        if bag_size not in total_counts:
            total_counts[bag_size] = 0
            unsolved_counts[bag_size] = 0
        total_counts[bag_size] += 1
        
        # Check if the result indicates an unsolved instance
        if result in ['MEMORYOUT', 'TIMEOUT']:
            unsolved_counts[bag_size] += 1

# Print the counts of unsolved instances for each bag size
for bag_size in sorted(total_counts):
    print("Bag size", bag_size, ":", unsolved_counts[bag_size], "unsolved instances (", total_counts[bag_size], "instances )")