from huggingface_hub import HfApi

api = HfApi()
for asset in ["vehicle_forklift_orange_a01", "palletJack_heavyDuty_a01", "robotics_small_bot_a01", "box_cardboard_a01", "pallet_a01"]:
    thumbs = [x.path for x in api.list_repo_tree("nvidia/simready-assets", path_in_repo=f"{asset}/simready_usd/.thumbs", repo_type="dataset", recursive=True) if x.path.endswith(".png")]
    print(asset, "->", thumbs)

