"""
import bpy
import sys

# Access the custom variables from command line arguments
project_name = sys.argv[sys.argv.index('--') + 1]
projects_folder = sys.argv[sys.argv.index('--') + 2]
currentlod = sys.argv[sys.argv.index('--') + 3]

print(f"NAME: {project_name}")
print(f"FOLDER: {projects_folder}")

# Example Blender operations
bpy.ops.cityjson.import_file('EXEC_DEFAULT', filepath= f"{projects_folder}{project_name}\\generated\\lodextracted={currentlod}_cm.city.json")

# Select all empties
bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
bpy.ops.object.select_by_type(type='EMPTY')  # Select all empties

# Delete all empties
bpy.ops.object.delete()  # Delete the selected empties

# Select all meshes
bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
bpy.ops.object.select_by_type(type='MESH')  # Select all meshes

# Make the first mesh the active selection
if bpy.context.selected_objects:
    first_mesh = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = first_mesh

    # Join all the meshes together into one object
    bpy.ops.object.join()

    # Merge vertices by distance with a distance of 0.1
    bpy.ops.object.editmode_toggle()  # Switch to Edit Mode
    bpy.ops.mesh.select_all(action='SELECT')  # Select all vertices
    bpy.ops.mesh.remove_doubles(threshold=0.1)  # Merge by distance
    bpy.ops.object.editmode_toggle()  # Switch back to Object Mode

    # Enable shade flat on the model
    bpy.ops.object.shade_flat()

    # Rename the remaining object to a variable
    new_name = "MyObject"  # Set your variable name here
    bpy.context.object.name = new_name
else:
    print("No mesh objects found to operate on.")


# Save the Blender file
save_path = f'{projects_folder}{project_name}\\blender\\3d_bag.blend'
bpy.ops.wm.save_as_mainfile(filepath=save_path)
"""