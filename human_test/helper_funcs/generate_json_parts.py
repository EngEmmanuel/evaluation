import json
import os
from pathlib import Path
from collections import OrderedDict

#_VIA_FILE_TYPE = { IMAGE:2, VIDEO:4, AUDIO:8 };
#_VIA_FILE_LOC  = { LOCAL:1, URIHTTP:2, URIFILE:3, INLINE:4 };

 # @param {number} fid a globally unique identifier
 # @param {string} fname filename
 # @param {number} type the file type as defined by _VIA_FILE_TYPE
 # @param {string} loc location of file as defined by _VIA_FILE_LOC
 # @param {string} src URI of the file or base64 data


def gen_file_part(save_path, n_images=60, root_name="img", ttype=2, loc=1,fname_root="Image", ext="png"):
    part = OrderedDict()
    
    for i in range(1, n_images+1):
        part[i] = {
            "fid": i,
            "fname": f"{fname_root} {i}",
            "type": ttype,
            "loc": loc,
            "src": f"{root_name}_{i}.{ext}"
        }

    with open(save_path, 'w') as fp:
        json.dump(part, fp) #indent arg may be useful
        

def gen_view_part():
    pass

if __name__ == "__main__":
    base_path = Path(r"C:\Users\spet4299\Documents\DPhil\Research\TEE_Generation\evaluation\human_test\helper_funcs\json_parts")
    fname = "file1"
    print("cwd:", os.getcwd())
    gen_file_part(base_path/f"{fname}.json")