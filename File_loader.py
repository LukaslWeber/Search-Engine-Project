import errno
import json
import os
import sys
from PriorityQueue import PriorityQueue
from typing import List, Dict
from joblib import dump, load


def load_visited_pages():
    file_name = "visited_pages.json"
    error_message = "Try giving the Web_Crawler object a frontier to create an empty frontier or construct it newly."
    return set(load_file(os.path.join("data_files", file_name), error_message))


def load_frontier():
    file_name = "frontier_pages.joblib"
    error_message = "Try giving the Web_Crawler object a frontier that you define manually instead of loading the file."
    frontier_list = load(os.path.join("data_files", file_name))
    frontier_pq = PriorityQueue()
    for (priority, url) in frontier_list:
        frontier_pq.put((priority, url))
    return frontier_pq



def load_index():
    forward_index = load(os.path.join("data_files", 'forward_index.joblib'))
    return forward_index


def save_index(file_name, forward_index: Dict[int, tuple]):
    dump(forward_index, file_name)


def save_visited_pages(file_name, visited_pages: set):
    with open(file_name, 'w') as file:
        json.dump(list(visited_pages), file)


def save_frontier_pages(file_name, frontier_pages: PriorityQueue):
    dump(frontier_pages.to_list(), file_name)


def load_file(file_name: str, error_message: str):
    try:
        file = load_json(file_name)
    except FileNotFoundError as file_not_found_err:
        print(file_not_found_err)
        sys.exit(f"{file_name} does not exist. {error_message}")
    except json.JSONDecodeError as dec_err:
        print(dec_err)
        sys.exit("An error occurred in decoding the JSON file.")

    return file


def load_json(file_name: str):
    # Check if it is a .json file
    if not file_name.endswith('.json'):
        raise ValueError("Invalid file format. Only JSON files are supported.")

    # Raise exception when the file_name does not exist
    if not os.path.isfile(file_name):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), file_name)
    # If it exists, then open it.
    try:
        with open(file_name, 'r') as file:
            visited_pages = json.load(file)
        return visited_pages
    # When the file is corrupt, it throws an exception
    except json.JSONDecodeError as e:
        print(f"Error loading {file_name}: \n{e}")
        raise json.JSONDecodeError(f"An error occurred in decoding {file_name}", file_name, 0)