import os
from huggingface_hub import hf_hub_download

repo_id = "nvidia/simready-assets"
asset = "vehicle_forklift_orange_a01"
local_dir = "/Users/juyunbal2651/MYFOLDER/simready-assets/tmp_usd"

files = [
    f"{asset}/simready_usd/payloads/instances.usda",
    f"{asset}/simready_usd/sm_{asset}_01.usd",
]

for f in files:
    p = hf_hub_download(repo_id=repo_id, filename=f, repo_type="dataset", local_dir=local_dir)
    print("Downloaded:", p)
