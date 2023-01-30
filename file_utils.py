'''
    Paul Smith
    
    A collection of functions for saving and loading data to json, downloading a
    file from a url, and cleaning a string for a file path

'''

import os
import json
import requests

def write_manifest(data: dict, path: str) -> None:
    with open(path, 'w') as manifest:
        json.dump(data, manifest, indent=4)

        
def read_manifest(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r') as manifest:
            manifest_data = json.load(manifest)
    else:
        manifest_data = {}
        
    return manifest_data

def download_file(url: str, filename: str=None, callback=None):
    if filename is None:
        filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        file_size = int(r.headers.get('Content-Length'))
        content_remaining = int(file_size)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                content_remaining -= len(chunk)
                f.write(chunk)
                if callable(callback):
                    callback(content_remaining, file_size)

def clean_path(path: str) -> str:
    cleaned_path = path
    dirty_values = '\\#%@&{}<>`?/!":=*| ' + "'"
    for value in dirty_values:
        cleaned_path = cleaned_path.replace(value, "")
    
    return cleaned_path
