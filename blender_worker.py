import bpy
import sys
import os

argv = sys.argv
if "--" not in argv:
    sys.exit(1)
args = argv[argv.index("--") + 1:]
usd_path = args[0]
out_glb = args[1]
asset_id = args[2] if len(args) > 2 else ""

# Clear default objects & meshes
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m, do_unlink=True)

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

# Determine primary accent color from asset_id
aid = asset_id.lower()
if 'blue' in aid:
    paint_color = (0.10, 0.42, 0.82, 1.0)
elif 'red' in aid:
    paint_color = (0.85, 0.14, 0.12, 1.0)
elif 'yellow' in aid:
    paint_color = (0.95, 0.72, 0.05, 1.0)
elif 'green' in aid:
    paint_color = (0.28, 0.68, 0.12, 1.0)
else:
    paint_color = (0.95, 0.38, 0.02, 1.0)  # Default industrial orange

for mat in bpy.data.materials:
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    out = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    n = mat.name.lower()
    if 'glass' in n or 'trans' in n:
        bsdf.inputs['Base Color'].default_value = (0.55, 0.80, 0.95, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.1
        bsdf.inputs['Roughness'].default_value = 0.08
        bsdf.inputs['Alpha'].default_value = 0.35
    elif 'painted' in n or 'orange' in n or 'body' in n or 'chassis' in n or 'cover' in n:
        bsdf.inputs['Base Color'].default_value = paint_color
        bsdf.inputs['Metallic'].default_value = 0.35
        bsdf.inputs['Roughness'].default_value = 0.32
    elif 'blue' in n:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.40, 0.72, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.25
        bsdf.inputs['Roughness'].default_value = 0.38
    elif 'red' in n:
        bsdf.inputs['Base Color'].default_value = (0.86, 0.14, 0.14, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.25
        bsdf.inputs['Roughness'].default_value = 0.38
    elif 'yellow' in n:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.72, 0.05, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.25
        bsdf.inputs['Roughness'].default_value = 0.38
    elif 'rubber' in n or 'wheel' in n or 'tire' in n:
        bsdf.inputs['Base Color'].default_value = (0.09, 0.10, 0.11, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.05
        bsdf.inputs['Roughness'].default_value = 0.85
    elif 'metal' in n or 'steel' in n or 'iron' in n or 'aluminum' in n or 'chrome' in n:
        bsdf.inputs['Base Color'].default_value = (0.26, 0.29, 0.33, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.32
    elif 'wood' in n or 'paper' in n or 'cardboard' in n or 'pallet' in n:
        bsdf.inputs['Base Color'].default_value = (0.76, 0.58, 0.36, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.82
    else:
        bsdf.inputs['Base Color'].default_value = (0.22, 0.25, 0.29, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.25
        bsdf.inputs['Roughness'].default_value = 0.45

# Link all mesh objects to main scene collection and decimate heavy meshes
for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
    if obj.name not in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.link(obj)
        except Exception:
            pass
    if len(obj.data.vertices) > 10000:
        obj.data = obj.data.copy()
        mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
        mod.ratio = 0.18
        with bpy.context.temp_override(object=obj):
            bpy.ops.object.modifier_apply(modifier=mod.name)

bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_yup=True,
    export_apply=True
)
print(f"SUCCESS_GLB:{out_glb}:{os.path.getsize(out_glb)}")
