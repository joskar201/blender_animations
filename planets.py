from math import pi, radians
from random import random
import bpy


def setup_render_settings(output_path, test_render=False):
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    bpy.context.scene.render.filepath = output_path

    if test_render:
        # Lower resolution for faster test renders
        bpy.context.scene.render.resolution_x = 960  # Half of 1920
        bpy.context.scene.render.resolution_y = 540   # Half of 1080
        bpy.context.scene.render.resolution_percentage = 50  # Or set to 100 for full scale at reduced resolution
    else:
        # Full resolution for final render
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.resolution_percentage = 100

    bpy.context.scene.render.fps = 24


def adjust_camera_clipping(camera, clip_start=0.1, clip_end=1000):
    camera.data.clip_start = clip_start  # Minimum distance to render objects
    camera.data.clip_end = clip_end  # Maximum distance to render objects

def setup_and_animate_camera(start_frame, end_frame, start_location, end_location, start_lens, end_lens):
    # Ensure the camera exists, if not, create one and set it as the active object
    camera = None
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=start_location)
        camera = bpy.context.active_object
    else:
        camera = bpy.data.objects["Camera"]
        # Explicitly set the camera as the active object
        bpy.context.view_layer.objects.active = camera
        camera.select_set(True)

    camera.location = start_location
    camera.rotation_euler = (radians(65), 0, radians(67))
    camera.data.lens = start_lens  # This should now correctly modify the camera

    # Use this function after creating or selecting the camera, with appropriate clipping distances
    adjust_camera_clipping(bpy.data.objects['Camera'], clip_start=0.1, clip_end=5000)

    # Insert keyframes for start position and lens
    camera.keyframe_insert(data_path="location", frame=start_frame)
    camera.data.keyframe_insert(data_path="lens", frame=start_frame)
    
    # Update camera location and lens for the end position
    camera.location = end_location
    camera.data.lens = end_lens  # Adjust the lens for the end
    
    # Insert keyframes for end position and lens
    camera.keyframe_insert(data_path="location", frame=end_frame)
    camera.data.keyframe_insert(data_path="lens", frame=end_frame)


def create_sphere(radius, distance_to_sun, obj_name):
    # instantiate a UV sphere with a given
    # radius, at a given distance from the
    # world origin point
    obj = bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(distance_to_sun, 0, 0),
        scale=(1, 1, 1)
    )
    # rename the object
    bpy.context.object.name = obj_name
    # apply smooth shading
    bpy.ops.object.shade_smooth()
    # return the object reference
    return bpy.context.object

def create_torus(radius, obj_name):
    # (same as the create_sphere method)
    obj = bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, 0),
        major_radius=radius,
        minor_radius=0.1,
        major_segments=60
    )
    bpy.context.object.name = obj_name
    # apply smooth shading
    bpy.ops.object.shade_smooth()
    return bpy.context.object

def create_emission_shader(color, strength, mat_name):
    # create a new material resource (with its
    # associated shader)
    mat = bpy.data.materials.new(mat_name)
    # enable the node-graph edition mode
    mat.use_nodes = True
    
    # clear all starter nodes
    nodes = mat.node_tree.nodes
    nodes.clear()

    # add the Emission node
    node_emission = nodes.new(type="ShaderNodeEmission")
    # (input[0] is the color)
    node_emission.inputs[0].default_value = color
    # (input[1] is the strength)
    node_emission.inputs[1].default_value = strength
    
    # add the Output node
    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    
    # link the two nodes
    links = mat.node_tree.links
    link = links.new(node_emission.outputs[0], node_output.inputs[0])

    # return the material reference
    return mat

def delete_object(name):
    # try to find the object by name
    if name in bpy.data.objects:
        # if it exists, select it and delete it
        obj = bpy.data.objects[name]
        obj.select_set(True)
        bpy.ops.object.delete(use_global=False)

def find_3dview_space():
    # Find 3D_View window and its scren space
    area = None
    for a in bpy.data.window_managers[0].windows[0].screen.areas:
        if a.type == "VIEW_3D":
            area = a
            break
    return area.spaces[0] if area else bpy.context.space_data

def setup_scene():
    # (set a black background)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    # (make sure we use the EEVEE render engine + enable bloom effect)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_bloom = True
    # (set the animation start/end/current frames)
    scene.frame_start = START_FRAME
    scene.frame_end = END_FRAME
    scene.frame_current = START_FRAME
    # get the current 3D view (among all visible windows
    # in the workspace)
    space = find_3dview_space()
    # apply a "rendered" shading mode + hide all
    # additional markers, grids, cursors...
    space.shading.type = 'RENDERED'
    space.overlay.show_floor = False
    space.overlay.show_axis_x = False
    space.overlay.show_axis_y = False
    space.overlay.show_cursor = False
    space.overlay.show_object_origins = False

N_PLANETS = 6
START_FRAME = 1
END_FRAME = 400

# setup scene settings
setup_scene()

output_path = "video.mp4"  # Update this path
setup_render_settings(output_path, test_render=False)


# Update these values based on your scene's scale and desired reveal
start_location = (20, -10, 5)  # Starting close to the sun
end_location = (200, -80, 90)  # Ending location to reveal the entire solar system
start_lens = 35  # Starting lens for tighter view
end_lens = 35  # Ending lens for a wider view

setup_and_animate_camera(START_FRAME, END_FRAME, start_location, end_location, start_lens, end_lens)

# clean scene + planet materials
delete_object("Sun")
for n in range(N_PLANETS):
    delete_object("Planet-{:02d}".format(n))
    delete_object("Radius-{:02d}".format(n))
for m in bpy.data.materials:
    bpy.data.materials.remove(m)

ring_mat = create_emission_shader(
    (1, 1, 1, 1), 1, "RingMat"
)
for n in range(N_PLANETS):
    # get a random radius (a float in [1, 5])
    r = 1 + random() * 4
    # get a random distace to the origin point:
    # - an initial offset of 30 to get out of the sun's sphere
    # - a shift depending on the index of the planet
    # - a little "noise" with a random float
    d = 30 + n * 12 + (random() * 4 - 2)
    # instantiate the planet with these parameters
    # and a custom object name
    planet = create_sphere(r, d, "Planet-{:02d}".format(n))
    planet.data.materials.append(
        create_emission_shader(
            (random(), random(), 1, 1),
            2,
            "PlanetMat-{:02d}".format(n)
        )
    )
    # add the radius ring display
    ring = create_torus(d, "Radius-{:02d}".format(n))
    ring.data.materials.append(ring_mat)

    # set planet as active object
    bpy.context.view_layer.objects.active = planet
    planet.select_set(True)
    # set object origin at world origin
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    # setup the planet animation data
    planet.animation_data_create()
    planet.animation_data.action = bpy.data.actions.new(name="RotationAction")
    fcurve = planet.animation_data.action.fcurves.new(
        data_path="rotation_euler", index=2
    )
    k1 = fcurve.keyframe_points.insert(
        frame=START_FRAME,
        value=0
    )
    k1.interpolation = "LINEAR"
    k2 = fcurve.keyframe_points.insert(
        frame=END_FRAME,
        value=(2 + random() * 2) * pi
    )
    k2.interpolation = "LINEAR"

# add the sun sphere
sun = create_sphere(12, 0, "Sun")
sun.data.materials.append(
    create_emission_shader(
        (1, 0.66, 0.08, 1), 10, "SunMat"
    )
)

# Now, trigger the rendering of the animation
bpy.ops.render.render(animation=True)

# deselect all objects
bpy.ops.object.select_all(action='DESELECT')
