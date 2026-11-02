import json
from huggingface_hub import HfApi

api = HfApi()
print("Fetching full root directory list from nvidia/simready-assets...")
items = list(api.list_repo_tree("nvidia/simready-assets", repo_type="dataset", recursive=False))
out = [{"type": getattr(x, "type", "directory" if hasattr(x, "last_commit") is False else "file"), "path": x.path} for x in items]
with open("hf_full_tree.json", "w") as f:
    json.dump([{"path": x.path, "is_dir": x.__class__.__name__ == "RepoFolder"} for x in items], f, indent=2)
print(f"Saved {len(items)} items to hf_full_tree.json")

