"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "23")
    file_2.txt (content: "78")
    file_3.txt (content: "3")

    Output:

    result.txt(content: "23, 78, 3")
"""

import os

def process_all_files_into_one():
    path = "./files"
    files = os.listdir(path)
    files.sort(key=lambda f: int(f.split('.')[0].split('_')[1]))

    values = []
    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
            values.append(f.read())

    with open("result.txt", 'w', encoding='utf-8') as out:
        out.write(", ".join(values))

process_all_files_into_one()