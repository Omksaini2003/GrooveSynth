import sys, os
from flask import Flask, request, render_template, send_file

app = Flask(__name__)


def extract_lines_with_ids(input_file, output_file, id_array):
    with open(input_file, "r") as f_input, open(output_file, "w") as f_output:
        for line in f_input:
            words = line.split()
            if len(words) >= 2:  # Check if the line has at least two words
                line_id = words[1]  # Assuming the ID is the second word in each line
                if line_id in id_array and words[0] == "ATOM":
                    f_output.write(line)


def distance(coord1, coord2):
    return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5


def nearest_neighbor(nodes, coordinates):
    if not nodes:
        print("Error: Nodes list is empty")
        return None, None
    unvisited = set(nodes)
    start_node = nodes[0]
    current_node = start_node
    path = [current_node]
    total_distance = 0
    while unvisited:
        nearest_node = None
        min_distance = sys.maxsize
        for neighbor in unvisited:
            if neighbor != current_node:
                dist = distance(coordinates[current_node], coordinates[neighbor])
                if dist < min_distance:
                    min_distance = dist
                    nearest_node = neighbor
        path.append(nearest_node)
        unvisited.remove(nearest_node)
        total_distance += min_distance
        current_node = nearest_node
    total_distance += distance(coordinates[current_node], coordinates[start_node])
    return total_distance, path


def extract_words(input_file):
    extracted_words = {}
    extracted_aa = {}
    with open(input_file, "r") as f_input:
        for line in f_input:
            print("Line:", line)
            words = line.split()
            print("Words:", words)
            if len(words) >= 8:  # Ensure the line has at least 8 words
                extracted_aa[int(words[1])] = words[3]
                extracted_words[int(words[1])] = (
                    float(words[6]),
                    float(words[7]),
                    float(words[8]),
                )  # Extract words 2nd, 6th, 7th, and 8th
                # extracted_words.append(words_to_extract)
    return extracted_words, extracted_aa


def interpolate_coordinates(point_A, point_B, distance):
    # Calculate the distance between points A and B
    distance_AB = (
        (point_A[0] - point_B[0]) ** 2 + (point_A[1] - point_B[1]) ** 2
    ) ** 0.5
    # Calculate the fraction of distance between A and B
    fraction = distance / distance_AB
    # Interpolate coordinates based on the fraction
    interpolated_x = round(point_A[0] + fraction * (point_B[0] - point_A[0]), 3)
    interpolated_y = round(point_A[1] + fraction * (point_B[1] - point_A[1]), 3)
    interpolated_z = round(point_A[2] + fraction * (point_B[2] - point_A[2]), 3)
    return (interpolated_x, interpolated_y, interpolated_z)


def add_ala(path, coordinates, threshold):
    final_path = []
    index = 0
    for i in range(len(path) - 1):
        final_path.append(i)
        if distance(coordinates[path[i]], coordinates[path[i + 1]]) > threshold:
            coordinates[index - 1] = interpolate_coordinates(
                coordinates[path[i]], coordinates[path[i + 1]], threshold
            )
            final_path.append(index - 1)
            index -= 1
            while distance(coordinates[index], coordinates[path[i + 1]]) > threshold:
                coordinates[index - 1] = interpolate_coordinates(
                    coordinates[index], coordinates[path[i + 1]], threshold
                )
                final_path.append(index - 1)
                index -= 1

    return final_path, coordinates


def ala(i, x, y, z):
    txt = f"ATOM      {i}  C   ALA A   1      {x}  {y}   {z}  1.00 35.50           C\n"
    return txt


def rearrange_lines(input_file, arranged_ids, output_file, coordinates):
    # Read the contents of the text file and store them in memory
    with open(input_file, "r") as f:
        lines = f.readlines()
    # Create a dictionary mapping each ID to its corresponding line
    id_to_line = {}
    for line in lines:
        parts = line.strip().split()
        # print(parts)
        id_ = parts[1]  # Assuming the ID is the second element in each line
        id_to_line[str(id_)] = line  # Convert the ID to string before using it as key
    # Iterate through the array of arranged IDs and append the corresponding lines to a new list
    rearranged_lines = []
    for id_ in arranged_ids:
        if id_ + 1 <= 0:
            rearranged_lines.append(
                ala(id_, coordinates[id_][0], coordinates[id_][1], coordinates[id_][2])
            )
        if str(id_ + 1) in id_to_line:
            rearranged_lines.append(id_to_line[str(id_ + 1)])
    # Write the lines from the new list to a new text file
    with open(output_file, "w") as f:
        f.writelines(rearranged_lines)


def replace_ids_with_line_numbers(input_file, output_file):
    # Open the input file for reading
    with open(input_file, "r") as f_input:
        # Open the output file for writing
        with open(output_file, "w") as f_output:
            # Initialize line number
            line_number = 1
            # Iterate over each line in the input file
            for line in f_input:
                # Split the line by whitespace and replace the first element (ID) with line number
                parts = line.strip().split()
                parts[1] = str(line_number)
                # Write the modified line to the output file
                f_output.write(" ".join(parts) + "\n")
                # Increment the line number
                line_number += 1


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "input_file" in request.files:
            input_file = request.files["input_file"]
            input_file_path = "input.pdb"
            input_file.save(input_file_path)
        else:
            input_file_path = "4dfr.pdb"
        id_array = request.form["id_array"].split(",")
        threshold = float(request.form["threshold"])
        output_file_1 = "extracted_lines.pdb"
        extract_lines_with_ids(input_file_path, output_file_1, id_array)
        extracted_words, extracted_aa = extract_words(output_file_1)
        nodes = list(extracted_words.keys())
        coordinates = extracted_words
        min_cost, path = nearest_neighbor(nodes, coordinates)
        final_path, coordinates = add_ala(path, coordinates, threshold)
        output_file_2 = "lines.pdb"
        rearrange_lines(output_file_1, final_path, output_file_2, coordinates)
        output_file_3 = "final1.pdb"
        replace_ids_with_line_numbers(output_file_2, output_file_3)
        return send_file(output_file_3, as_attachment=True)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
