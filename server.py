import os
import json
import shutil
import subprocess
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from huggingface_hub import hf_hub_download

BASE_DIR = "/Users/juyunbal2651/MYFOLDER/simready-assets"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TMP_DIR = os.path.join(BASE_DIR, "tmp_usd")
BLENDER_BIN = "/Applications/Blender.app/Contents/MacOS/Blender"
WORKER_SCRIPT = os.path.join(BASE_DIR, "blender_worker.py")
REPO_ID = "nvidia/simready-assets"

os.makedirs(ASSETS_DIR, exist_ok=True)


def get_local_assets():
    if not os.path.exists(ASSETS_DIR):
        return []
    return [
        f[:-4]
        for f in os.listdir(ASSETS_DIR)
        if f.endswith(".glb") and not f.startswith(".")
    ]


def get_disk_info():
    total, used, free = shutil.disk_usage("/")
    assets_bytes = sum(
        os.path.getsize(os.path.join(ASSETS_DIR, f))
        for f in os.listdir(ASSETS_DIR)
        if os.path.isfile(os.path.join(ASSETS_DIR, f))
    )
    return {
        "free_gb": round(free / (1024**3), 2),
        "assets_mb": round(assets_bytes / (1024**2), 2),
        "ready_ids": get_local_assets(),
    }


class SimReadyHandler(SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            return self.send_json(get_disk_info())
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/api/convert":
            asset_id = qs.get("id", [""])[0].strip()
            if not asset_id or "/" in asset_id or ".." in asset_id:
                return self.send_json({"ok": False, "error": "Invalid asset id"}, 400)

            out_glb = os.path.join(ASSETS_DIR, f"{asset_id}.glb")
            if os.path.exists(out_glb):
                return self.send_json({
                    "ok": True,
                    "cached": True,
                    "glb": f"./assets/{asset_id}.glb",
                    "disk": get_disk_info(),
                })

            try:
                os.makedirs(TMP_DIR, exist_ok=True)
                files = [
                    f"{asset_id}/simready_usd/payloads/Physics/physics.usda",
                    f"{asset_id}/simready_usd/payloads/base.usda",
                    f"{asset_id}/simready_usd/payloads/materials.usda",
                    f"{asset_id}/simready_usd/payloads/instances.usda",
                    f"{asset_id}/simready_usd/payloads/geometries.usd",
                ]
                for f in files:
                    try:
                        hf_hub_download(
                            repo_id=REPO_ID,
                            filename=f,
                            repo_type="dataset",
                            local_dir=TMP_DIR,
                        )
                    except Exception:
                        pass

                base_usda = os.path.join(
                    TMP_DIR, asset_id, "simready_usd", "payloads", "base.usda"
                )
                geom_usd = os.path.join(
                    TMP_DIR, asset_id, "simready_usd", "payloads", "geometries.usd"
                )
                target_usd = base_usda if os.path.exists(base_usda) else geom_usd

                if not os.path.exists(target_usd):
                    shutil.rmtree(TMP_DIR, ignore_errors=True)
                    return self.send_json(
                        {"ok": False, "error": "USD payload not found in package"}, 404
                    )

                subprocess.run(
                    [
                        BLENDER_BIN,
                        "--background",
                        "--factory-startup",
                        "--python",
                        WORKER_SCRIPT,
                        "--",
                        target_usd,
                        out_glb,
                        asset_id,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                shutil.rmtree(TMP_DIR, ignore_errors=True)

                return self.send_json({
                    "ok": True,
                    "cached": False,
                    "glb": f"./assets/{asset_id}.glb",
                    "disk": get_disk_info(),
                })
            except Exception as e:
                shutil.rmtree(TMP_DIR, ignore_errors=True)
                return self.send_json({"ok": False, "error": str(e)}, 500)

        if parsed.path == "/api/clean_cache":
            keep = {
                "vehicle_forklift_orange_a01.glb",
                "palletJack_heavyDuty_a01.glb",
                "robotics_small_bot_a01.glb",
                "pallet_a01.glb",
                "box_cardboard_a01.glb",
                "sm_sample_model.gltf",
                "sm_sample_model.usd",
            }
            removed = 0
            for f in os.listdir(ASSETS_DIR):
                if f not in keep and f.endswith(".glb"):
                    os.remove(os.path.join(ASSETS_DIR, f))
                    removed += 1
            return self.send_json({"ok": True, "removed": removed, "disk": get_disk_info()})

        return self.send_json({"ok": False, "error": "Not found"}, 404)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    server = ThreadingHTTPServer(("0.0.0.0", 8000), SimReadyHandler)
    print("SimReady Pamphlet & 3D Viewer Server running on http://localhost:8000")
    server.serve_forever()

