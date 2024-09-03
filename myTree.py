import bpy
import bmesh
import math
import random
from mathutils import Vector

def create_branch(length, thickness):
    mesh = bpy.data.meshes.new("Branch")
    obj = bpy.data.objects.new("Branch", mesh)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=8,
        radius1=thickness,
        radius2=thickness*0.8,
        depth=length
    )
    bmesh.ops.translate(bm, vec=Vector((0, 0, length/2)), verts=bm.verts)
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_leaf():
    bm = bmesh.new()
    bmesh.ops.create_circle(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=8,
        radius=0.15,
    )
    bmesh.ops.scale(
        bm,
        vec=(1, 0.5, 1),
        verts=bm.verts
    )
    mesh = bpy.data.meshes.new("Leaf")
    bm.to_mesh(mesh)
    bm.free()
    
    leaf = bpy.data.objects.new("Leaf", mesh)
    
    material = bpy.data.materials.new(name="Leaf Material")
    material.use_nodes = True
    material.node_tree.nodes.clear()
    
    node_tree = material.node_tree
    output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    bsdf_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.inputs['Base Color'].default_value = (0.1, 0.5, 0.1, 1)  # Green color
    bsdf_node.inputs['Roughness'].default_value = 0.8
    node_tree.links.new(bsdf_node.outputs[0], output_node.inputs[0])
    
    leaf.data.materials.append(material)
    leaf.scale = (0.2, 0.2, 0.2)
    
    return leaf

def add_leaves(branch, collection):
    num_leaves = random.randint(1, 3)
    for _ in range(num_leaves):
        leaf = create_leaf()
        collection.objects.link(leaf)
        leaf.parent = branch
        
        # Position the leaf
        leaf.location = Vector((random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(0, branch.dimensions.z)))
        
        # Rotate the leaf
        leaf.rotation_euler = (random.uniform(0, math.pi*2), random.uniform(0, math.pi*2), random.uniform(0, math.pi*2))

def create_tree(max_depth, length, thickness, collection):
    trunk = create_branch(length, thickness)
    collection.objects.link(trunk)
    grow_branches(trunk, max_depth, length, thickness, collection)
    return trunk

def grow_branches(parent, depth, length, thickness, collection):
    if depth == 0:
        add_leaves(parent, collection)
        return

    num_branches = random.randint(1, 9)
    for _ in range(num_branches):
        branch_length = length * random.uniform(0.5, 0.8)
        branch_thickness = thickness * random.uniform(0.6, 0.8)
        angle_x = random.uniform(-math.pi/4, math.pi/4)
        angle_z = random.uniform(0, 3*math.pi)
        
        branch = create_branch(branch_length, branch_thickness)
        collection.objects.link(branch)
        branch.parent = parent
        branch.location = Vector((0, 0, length * 0.9))
        branch.rotation_euler = (angle_x, 0, angle_z)
        
        grow_branches(branch, depth-1, branch_length, branch_thickness, collection)

def animate_growth(obj, start_frame, end_frame):
    obj.scale = (0, 0, 0)
    obj.keyframe_insert(data_path="scale", frame=start_frame)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", frame=end_frame)
    
    for child in obj.children:
        child_start = start_frame + random.randint(1, 15)
        child_end = end_frame + random.randint(5, 15)
        animate_growth(child, child_start, child_end)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new collection for the tree
tree_collection = bpy.data.collections.new("Tree")
bpy.context.scene.collection.children.link(tree_collection)

# Create the tree
max_depth = 5
initial_length = 2
initial_thickness = 0.1

tree = create_tree(max_depth, initial_length, initial_thickness, tree_collection)

# Animate the tree growth
start_frame = 1
end_frame = 150
animate_growth(tree, start_frame, end_frame)

# Set up the scene
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = end_frame + max_depth * 15

# Add a camera
bpy.ops.object.camera_add(location=(10, -10, 10), rotation=(math.pi/4, 0, math.pi/4))

# Add a light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

# Force update of the view layer
bpy.context.view_layer.update()

# Set viewport shading to Material Preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

print("Script execution completed")