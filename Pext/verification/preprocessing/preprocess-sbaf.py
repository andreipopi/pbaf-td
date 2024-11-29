# derive all dattacks
# derive all supports
#adds the following to the instance
#datt(e,a).
#datt(e,z).
#datt(f,c).
#datt(a,c).
#datt(z,c).
#datt(e,b).
#datt(b,c).
#datt(f,d).
#derivedsup(z,b).


import sys
import re
import subprocess
from tokenize import group


file_path = sys.argv[1]
file = open(file_path,'r')
lines = file.read().split("\n")
att_pattern = re.compile(r'att\(([^,]+),([^,]+)\)')
datt_pattern = re.compile(r'datt\(([^,]+),([^,]+)\)')

support_pattern = re.compile(r'support\(([^,]+),([^,]+)\)')
# store the supports available in the instance in an array 
# ['ab','cd']
instance_supports = []
for line in lines:
    if 'support(' in line:
        match = support_pattern.match(line)
        instance_supports.append(match.group(1)+match.group(2))
        #print(match)

instance_attacks = []
for line in lines:
    if 'att(' in line:
        match = att_pattern.match(line)
        if match != None:
            instance_attacks.append(match.group(1)+match.group(2))
        #print(match)

# infer possibly new supports, and dattacks
process = subprocess.Popen(["clingo", "spreprocess.lp", file_path, "0"], stdout = subprocess.PIPE)
output = str(process.communicate()[0], "utf-8") #the output is in process.communicate()[0] and we need it in utf-8 for parsing
#output = str(output.partition("Solving...")[2]) #get what comes after "Solving..."
# Find the start of the "Answer:" section
answer_start = output.find("Answer:")
if answer_start != -1:

    # Find the end of the relevant section (SATISFIABLE or UNSATISFIABLE)
    satisfiable_pos = output.find("SATISFIABLE", answer_start)
    unsatisfiable_pos = output.find("UNSATISFIABLE", answer_start)

    if satisfiable_pos != -1:
        answer_end = satisfiable_pos
    elif unsatisfiable_pos != -1:
        answer_end = unsatisfiable_pos
   
    # Extract the relevant portion
    relevant_output = output[answer_start:answer_end]

    # Remove the "Answer: x" part
    relevant_output = re.sub(r'Answer:\s*\d+', '', relevant_output).strip()

    # Split the output into words
    words = relevant_output.split()
    output = words


derived_datts = []
derived_supports = []

for relation in output:
    if "datt(" in relation:
        derived_datts.append(relation)
    elif "support(" in relation:
        derived_supports.append(relation)


derived_supports_adjusted = []
for sup in derived_supports:
    match = support_pattern.match(sup)
    if match.group(1)+match.group(2) not in instance_supports: #only consider the derived supports that were not already in the original supports
        derived_supports_adjusted.append("dsu("+match.group(1)+","+match.group(2)+")")


derived_attacks_adjusted = []
print("derived atts", derived_datts)
for sup in derived_datts:
    match = datt_pattern.match(sup)
    if match.group(1)+match.group(2) not in instance_attacks: #only consider derived dattacks that were not already in the original attacks
        derived_attacks_adjusted.append("datt("+match.group(1)+","+match.group(2)+")")


print(derived_datts)

print(derived_supports_adjusted)

with open(file_path, 'a') as file:
    file.write("\n")
    for datt in derived_attacks_adjusted:
        file.write(datt + ".\n")

    for dersup in derived_supports_adjusted:
        file.write(dersup + ".\n")


#output = output.split(sep='Answer')


#output = re.sub('\n', '', output)
#output = str(output.replace("'",''))
#output= str(output.replace("[", ''))





