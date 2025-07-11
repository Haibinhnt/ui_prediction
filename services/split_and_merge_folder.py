import os
import shutil
from math import ceil


def split_files_into_parts(folder_path, num_parts):
    # Get all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Calculate the number of files per part
    num_files = len(files)
    files_per_part = ceil(num_files / num_parts)

    # Create destination folders and move files
    for i in range(num_parts):
        part_folder = os.path.join(folder_path, f'part_{i + 1}')
        os.makedirs(part_folder, exist_ok=True)

        start_index = i * files_per_part
        end_index = min((i + 1) * files_per_part, num_files)

        for file in files[start_index:end_index]:
            src_path = os.path.join(folder_path, file)
            dst_path = os.path.join(part_folder, file)
            shutil.move(src_path, dst_path)

def move_all_files_to_one_folder(parent_folder, dest_folder):
    # Create the destination folder if it does not exist
    os.makedirs(dest_folder, exist_ok=True)

    # Iterate through each part folder (assuming part folders are named 'part_1', 'part_2', ..., 'part_20')
    for i in range(1, 26):
        part_folder = os.path.join(parent_folder, f'part_{i}')
        if os.path.exists(part_folder):
            for root, _, files in os.walk(part_folder):
                for file in files:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(dest_folder, file)
                    shutil.move(src_path, dst_path)
                    print(f'Moved {file} from {root} to {dest_folder}')
        else:
            print(f'Folder {part_folder} does not exist.')


def move_all_folders(source_dir, target_dir):
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # List all items in the source directory
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)

        # Check if the item is a directory
        if os.path.isdir(item_path):
            shutil.move(item_path, target_dir)
            print(f"Moved: {item_path} to {target_dir}")