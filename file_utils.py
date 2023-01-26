
import os, json

def write_manifest(data: dict, path: str) -> None:
    with open(path, 'w') as manifest:
        json.dump(data, manifest)

        
def read_manifest(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r') as manifest:
            manifest_data = json.load(manifest)
    else:
        manifest_data = {}
        
    return manifest_data


def clean_path(path: str) -> str:
    cleaned_path = path
    dirty_values = '\\#%@&{}<>`?/!":=*| ' + "'"
    for value in dirty_values:
        cleaned_path = cleaned_path.replace(value, "")
    
    return cleaned_path
