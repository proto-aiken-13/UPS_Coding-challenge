import json
import math

#Code assumes that the input.json file is in the same folder, and that it is present and has info in it.

file_path = 'input.json'

with open(file_path, 'r') as file:
    # Load JSON data from the file
    data = json.load(file)

schools_list = data.get("schools", [])
students_list = data.get("students", [])

def calculate_priority_score(student, school):
    # Extract coordinates
    student_location = student["homeLocation"]
    school_location = school["location"]
    
    # Calculate Euclidean distance
    def euclidean_distance(loc1, loc2):
        return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    
    distance = euclidean_distance(student_location, school_location)
    
    # Handle the case where distance is zero to avoid division by zero
    if distance == 0:
        inverse_distance = float('inf')  # Infinite similarity for identical locations
    else:
        inverse_distance = 1 / distance
    
    # Calculate the distance contribution to the score
    distance_score = inverse_distance * 0.5
    
    # Check for alumni match
    alumni_match = student.get("alumni") == school.get("name")
    alumni_score = 0.3 if alumni_match else 0
    
    # Check for volunteer match
    volunteer_match = student.get("volunteer") == school.get("name")
    volunteer_score = 0.2 if volunteer_match else 0
    
    # Total score
    total_score = distance_score + alumni_score + volunteer_score
    
    return total_score

# Create a list of tuples using schools_list. The first element is the name of the school and the second element is an empty list.
school_pairs = [[school["name"], []] for school in schools_list]

# Create a dictionary for school capacities
school_capacity_dict = {school["name"]: school.get("maxAllocation", float('inf')) for school in schools_list}

# Create a set of school names for quick lookup
school_names_set = set(school_capacity_dict.keys())

# Calculate priority scores and sort students
for student in students_list:
    # For each student, create a list of tuples (school name, priority score)
    templist = [(school["name"], calculate_priority_score(student, school)) for school in schools_list if school["name"] in school_names_set]
    
    # Sort the list by priority score in descending order and ID in ascending order
    templist_sorted = sorted(templist, key=lambda x: (-x[1], student.get("id", float('inf'))))
    
    # Add the sorted list of schools to the student record
    student["sorted_schools"] = templist_sorted

# Sort all students based on highest priority of their schools and ascending id number
students_sorted = sorted(students_list, key=lambda s: (-s["sorted_schools"][0][1], s.get("id", float('inf'))))

# Assign students to schools
for student in students_sorted:
    # Iterate through the sorted list of schools for the student
    updated_school_list = []
    for school_name, _ in student["sorted_schools"]:
        # Check if the school is not full
        if len(next(students for name, students in school_pairs if name == school_name)) < school_capacity_dict.get(school_name, float('inf')):
            # Add the student to the school
            for i, (name, students) in enumerate(school_pairs):
                if name == school_name:
                    school_pairs[i][1].append(student["id"])
                    break
            # Student assigned, stop checking further schools
            break
        else:
            # If the school is full, remove it from the student's sorted list
            updated_school_list.append((school_name, _))
    
    # Update the student's school list
    student["sorted_schools"] = updated_school_list

# Convert school_pairs list of lists to a dictionary
school_pairs_dict = {school_name: students for school_name, students in school_pairs}

# Write the result to a JSON file
output_file_path = 'output.json'
with open(output_file_path, 'w') as outfile:
    json.dump(school_pairs_dict, outfile, indent=4)