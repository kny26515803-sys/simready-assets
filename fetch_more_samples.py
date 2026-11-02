import os
from huggingface_hub import hf_hub_download

repo_id = "nvidia/simready-assets"
local_dir = "/Users/juyunbal2651/MYFOLDER/simready-assets/tmp_usd"

assets = ["pallet_a01", "box_cardboard_a01"]

for asset in assets:
    files = [
        f"{asset}/simready_usd/payloads/Physics/physics.usda",
        f"{asset}/simready_usd/payloads/base.usda",
        f"{asset}/simready_usd/payloads/materials.usda",
        f"{asset}/simready_usd/payloads/instances.usda",
        f"{asset}/simready_usd/payloads/geometries.usd",
    ]
    for f in files:
        try:
            p = hf_hub_download(repo_id=repo_id, filename=f, repo_type="dataset", local_dir=local_dir)
            print("Downloaded:", p)
        except Exception as e:
            print("Skip:", f, e)
