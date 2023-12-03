import sys
import re
import os
from pathlib import Path
import shutil
image_extensions = ["jpeg", "png", "jpg", "svg"]
video_extensions = ["avi", "mp4", "mov", "mkv"]
doc_extensions = ["doc", "docx", "txt", "pdf", "xlsx", "pptx"]
audio_extensions = ["mp3", "ogg", "wav", "amr"]
archive_extensions = ["zip", "gz", "tar"]
known_extensions = []
known_extensions = image_extensions + video_extensions + doc_extensions + audio_extensions + archive_extensions
unknown_extensions_found = set()
known_extensions_found = set()
designated_folders = {"Images": image_extensions, "Video": video_extensions, "Documents": doc_extensions, "Audio": audio_extensions, "Archives": archive_extensions,}
polish_characters = {"Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z", "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z"}

def normalize(string_to_normalize):
    """This method takes string as an input and returns altered string.
    Replaces characters "ę" "ą" "ż" etc for "e" "a "z"
    Charactes other then letters and digits are replaced with "_" """
    global file_extension
    global file_name
    global item
    result = ""
    if item.is_file(): #checks if item is a file
        file_name, file_extension = os.path.splitext(string_to_normalize) # separates file name and file extension
    else:
        file_name = item.name # if item is a folder there is no need to separate an extension 
        file_extension = "" #empty string just so it works with the rest of the code 
    for character in file_name: # only file name is modified
        if character in polish_characters: #changes polish characters to latin
            character = polish_characters[character]
        if not re.search("\w", character): #charactes other then letters, digits and "_" gets replaced with "_"
            character = "_"
        result += character
    result += file_extension
    return result

def check_argument():
    """Takes no arguments.
    Checks if script was run with correct argument
    """
    if len(sys.argv) < 2: #checks if script was run with any argument
        print("You need to run script with argument (path to folder to clean)")
        exit()
    elif not Path(sys.argv[1]).is_dir(): #checks if argument is a valid directory
        print("Argument is not a correct directiory")
        exit()

def sort_out_files(path):
    """Funcion takes a path to folder to be cleaned as an argument
    -funcion unpackes archives
    -normalize file names and moves them to designanted folders
    -doesnt change a name of a file with unknown extension"""
    global item
    global archive_folders_to_ignore
    for item in path.iterdir():
        new_item_name = normalize(item.name) #generating new name, also generating separated file name and extension
        if item.is_dir(): #checks if item is a folder
            if item.name in designated_folders.keys() or item.name == "Unknown": #ignoring certain folders
                continue
            else:
                sort_out_files(item)  # going into subfolder      
        elif item.is_file(): #checks if item is a file
            if file_extension.lstrip(".").lower() not in known_extensions: # determine if its file with unknown extension
                global unknown_extensions_found
                unknown_extensions_found.add(file_extension.lstrip(".")) #adds unknown extension to a set to create a raport later on
                if not Path(f'{sys.argv[1]}\\Unknown\\').exists(): #checks if Folder Unknown to exist and create it if necesary
                    os.makedirs(Path(f'{sys.argv[1]}\\Unknown')) #create folder to move a file
                shutil.move(item, Path(f'{sys.argv[1]}\\Unknown\\{item.name}')) # move file to new location without changing a name
                continue
            else: #code for files with known extension
                known_extensions_found.add(file_extension.lstrip(".").lower()) #adds known extension to a set to create a raport later on       
                if file_extension.lstrip(".").lower() in archive_extensions: #check if file is an archive
                    if not Path(f'{sys.argv[1]}\\Archives\\').exists(): #checks if Folder Unknown to exist and create it if necesary
                        os.makedirs(Path(f'{sys.argv[1]}\\Archives')) #create folder to move a file
                    shutil.unpack_archive(item, Path(f'{sys.argv[1]}\\Archives\\{file_name}')) #unpack archive in subfolder with designated name
                    os.remove(item) #delete unpacked file
                    continue
                else: #not an archive
                    for data_type, extension_list in designated_folders.items(): #to determine type of a file
                        if file_extension.lstrip(".").lower() in extension_list:
                            if not Path(f'{sys.argv[1]}\{data_type}\\').exists(): #checks if Folder to move exist and create it if necesary
                                os.makedirs(Path(f'{sys.argv[1]}\{data_type}')) #create folder to move a file
                            shutil.move(item, Path(f'{sys.argv[1]}\{data_type}\{new_item_name}')) # move file to new location with new name


def delete_empty_folders(path):
    """Takes directory as an argument
    Method delete empty folders in a given directory
    Ignores designated folders"""
    for item in path.iterdir():
        if item.is_dir(): #checks if item is a folder
            if item.name in designated_folders.keys() or item.name == "Unknown": #ignoring certain folders
                continue
            else:                
                if len(os.listdir(item)) == 0: #checks if folder is empty
                    print(f"{item.name} is an empty folder. Deleting {item.name}")
                    os.rmdir(item)
                else:
                    delete_empty_folders(item)  # going into subfolder
                    os.rmdir(item) #delete a folder when all subfolders are gone

def create_report():
    """Funcions prints report of found extension and gives files list"""
    if bool(unknown_extensions_found): #unknown extension report
        print('|{:^80}|'.format("*****Unknown Extensions Found*****"))
        for unknown_extension in unknown_extensions_found:
            print('|{:^80}|'.format(unknown_extension))
    if bool(known_extensions_found):
        print('|{:^80}|'.format("*****Known Extensions Found*****")) #known extensions report
        for known_extension in known_extensions_found:
            print('|{:^80}|'.format(known_extension))
    if Path(f'{sys.argv[1]}\\Unknown\\').exists():
        print('|{:^80}|'.format(f"*****Files in folder Unknown*****")) #files in folder Unknown
        for file in Path(f'{sys.argv[1]}\\Unknown\\').iterdir():
            print('|{:^80}|'.format(file.name))
    for folder in designated_folders: #files in all other folders
        if Path(f'{sys.argv[1]}\{folder}\\').exists():
            print('|{:^80}|'.format(f"*****Files in folder {folder}*****"))
            for file in Path(f'{sys.argv[1]}\{folder}\\').iterdir():
                print('|{:^80}|'.format(file.name))


check_argument()
sort_out_files(Path(sys.argv[1]))
delete_empty_folders(Path(sys.argv[1]))
create_report()
exit()