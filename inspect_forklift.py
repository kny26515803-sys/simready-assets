from huggingface_hub import HfApi

api = HfApi()
for item in api.list_repo_tree("nvidia/simready-assets", path_in_repo="vehicle_forklift_orange_a01", repo_type="dataset", recursive=True):
    size = getattr(item, "size", 0)
    print(f"{item.path}  ({size/1024:.1f} KB)")

