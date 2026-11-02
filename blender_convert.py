import bpy
import os
from mathutils import Vector

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m, do_unlink=True)

usd_path = "/Users/juyunbal2651/MYFOLDER/simready-assets/tmp_usd/vehicle_forklift_orange_a01/simready_usd/payloads/base.usda"
out_glb = "/Users/juyunbal2651/MYFOLDER/simready-assets/assets/vehicle_forklift_orange_a01.glb"

bpy.ops.wm.usd_import(filepath=usd_path)

orig_meshes = set(o for o in bpy.data.objects if o.type == 'MESH')

bpy.ops.object.select_all(action='DESELECT')
has_instances = False
for obj in list(bpy.data.objects):
    if obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
        obj.select_set(True)
        has_instances = True

if has_instances:
    bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=False)
    new_meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o not in orig_meshes]
    if new_meshes:
        for om in orig_meshes:
            bpy.data.objects.remove(om, do_unlink=True)

for obj in list(bpy.data.objects):
    if obj.type != 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# Check world bounding box in Blender (Z is up in Blender)
mins = [1e9, 1e9, 1e9]
maxs = [-1e9, -1e9, -1e9]
for obj in bpy.data.objects:
    for v in obj.bound_box:
        wv = obj.matrix_world @ Vector(v)
        for i in range(3):
            mins[i] = min(mins[i], wv[i])
            maxs[i] = max(maxs[i], wv[i])

print("World BBox in Blender (X, Y, Z):", [round(maxs[i]-mins[i], 3) for i in range(3)], "min:", [round(x, 3) for x in mins], "max:", [round(x, 3) for x in maxs])
