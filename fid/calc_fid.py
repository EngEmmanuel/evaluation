
import os
import re
import pandas as pd
from pathlib import Path
from subprocess import run

root = Path(r"C:\Users\spet4299\Documents\DPhil\Research\TEE_Generation\evaluation\\fid\\")
set_path = r"C:\Users\spet4299\Documents\DPhil\Research\TEE_Generation\evaluation\fid\sets.csv"
df = pd.read_csv(set_path)

print(df)
dset = ["valtest","train"]
fids = {x:[] for x in dset}


for d in dset:
    for (pA, pB) in zip(df[f"{d}B"], df[f"{d}GB"]):
        args = [
            "python",
            "-m",
            "pytorch_fid",
            pA,
            pB,
        ]

        output= run(args,capture_output=True, shell=False)
        fid = float(re.findall("\d+\.\d+", str(output.stdout))[0])
        fids[d].append(fid)
        print('\n', output)

    df[f"{d}FID"] = fids[d]

df.to_csv(set_path)
