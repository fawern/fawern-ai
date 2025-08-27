import os 

def save_generated_data_to_md(class_name, data):
    """
    Saves generated data into a .md file with a name based on the class name.

    Args:
        class_name (str): The name of the class to base the file name on.
        data (str): The data to be written to the .md file.
    """
    file_name = f"{class_name}" + ".md"

    root_directory = os.getcwd()

    full_path = os.path.join(root_directory, file_name)

    with open(full_path, "w") as md_file:
        md_file.write(data)

    print(f"Data written to {file_name}")