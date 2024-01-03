import os
import shutil
from termcolor import colored
import json

def load_parameters(home):
    with open(os.path.join(home, "params.json")) as f:
        data = json.load(f)
    return data

def create_temp_directory(temp_dir):
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

def create_core_directory(temp_dir, core):
    core_dir = os.path.join(temp_dir, "core_" + str(core))
    if os.path.exists(core_dir):
        shutil.rmtree(core_dir)
    os.mkdir(core_dir)
    return core_dir

def create_file(data, path):
    file = open(path, "w")
    file.write(data)
    file.close()

def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines]

def create_fact_file_with_data(data, path):
    file  = open(path, "w")
    for row in data:
        file.write(row + "\n")
    file.close()