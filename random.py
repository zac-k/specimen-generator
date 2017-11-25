

import mathutils, numpy, bpy
import random as rnd

PI = numpy.pi


def point_inside_mesh(point, ob):
    """
    Determines if a given point is inside the mesh
    of an object using a ray casting algorithm.
    Parameters
    ----------
    point : Mathutils.Vector()
        Three dimensional vector corresponding to the location in
        space being tested.
    ob : bpy.types.Object
        Object whose mesh defines the boundaries of the region.
        Mesh must have a well defined interior/exterior for
        predictable results. Typically, being closed would be
        sufficient.

    Returns
    -------
    bool
        True means that the point was inside ob,
        and False means that it was not.
    """

    # Additional axes can be added to this list if exterior points are
    # erroneously counted as being interior. This can occur due to
    # numerical errors under some (rare) circumstances.

    axes = [mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0))]
    outside = False
    for axis in axes:

        mat1 = mathutils.Matrix(ob.matrix_world)
        mat = mat1.invert()

        orig = mat1 * point

        count = 0
        while True:
            result, location, normal, index = ob.ray_cast(orig, axis * 10000.0)
            if index == -1:
                break
            count += 1

            orig = location + axis * 0.00001

        if (count % 2 == 0):
            outside = True
            break

    return not outside


def get_override(area_type, region_type):
    for area in bpy.context.screen.areas:
        if area.type == area_type:
            for region in area.regions:
                if region.type == region_type:
                    override = {'area': area, 'region': region}
                    return override
    # error message if the area or region wasn't found
    raise RuntimeError("Wasn't able to find", region_type, " in area ", area_type,
                       "\n Make sure it's open while executing script.")


def main():
    """
    Procedurally generates specimen simulations.
    Requires "Blender" to run. Open file inside Blender,
    set output_path, and run. Output format is a text file
    with each block of rows/columns representing a 2D slice
    of the binary specimen mask. Each block is separated
    by an empty line. Currently working in Blender 2.78a
    """
    M = 64  # Number of pixels along each dimension of the output file.
    num_specimens = 10  # Number of specimens to simulate.
    numpy_output = True

    # Index of first output file. Only needs to be changed if
    # the process was interrupted or if additional specimens
    # are required.
    start_number = 0

    # Path to place the output files in. Must exist.
    output_path = '/output/path/'  # e.g., 'C:\simulations\\'

    # Generate the specimens.
    for i in range(num_specimens):
        # File output path. Each file contains the specimen number to
        # differentiate it from the other specimens.
        fileOut = output_path + 'particle(' + str(i + start_number) + ')'

        # Generate pseudo-random numbers for size, position, and rotation
        # of the specimen
        radius = rnd.uniform(0.12, 0.14)
        offset = 0.05
        location = (
            rnd.uniform(-offset, offset),
            rnd.uniform(-offset, offset),
            rnd.uniform(-offset, offset)
        )
        rotation = (
            rnd.uniform(0, 2 * PI),
            rnd.uniform(0, 2 * PI),
            rnd.uniform(0, 2 * PI)
        )

        # Spawn cube.
        bpy.ops.mesh.primitive_cube_add(
            location=location,
            rotation=rotation,
            radius=radius
        )

        # Define and apply modifiers.
        ob_base = bpy.context.active_object
        fracture = False
        if fracture:
            bpy.ops.object.add_fracture_cell_objects(
                use_layer_next=False,
                use_sharp_edges_apply=False,
                source_noise=1,
                source_limit=2
            )
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
            frac_scale = rnd.uniform(0.4, 0.6)

            override = get_override('VIEW_3D', 'WINDOW')
            print(override)

            bpy.ops.transform.resize(
                override,
                value=(frac_scale, frac_scale, frac_scale)
            )
            bpy.ops.object.join()

            ob = bpy.context.active_object
            bpy.context.scene.objects.active = ob_base
            ob_base.select = True
            ob.select = False
            bpy.ops.object.delete()
            bpy.context.scene.objects.active = ob
            ob.select = True
        else:
            ob = ob_base

        num_cuts = rnd.randint(0, 8)

        mesh = ob.data
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.subdivide(
            number_cuts=num_cuts,
            smoothness=0
        )

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='DISPLACE')
        ob.modifiers['Displace'].mid_level = 0.9
        ob.modifiers['Displace'].strength = rnd.uniform(-0.2, 0.7)

        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        ob.modifiers['SimpleDeform'].limits[0] = rnd.uniform(0, 1)

        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        ob.modifiers['SimpleDeform.001'].limits[0] = rnd.uniform(0, 0.7)
        ob.modifiers['SimpleDeform.001'].angle = rnd.uniform(0, 100 * 2 * PI / 360)
        ob.modifiers['SimpleDeform.001'].lock_y = True

        bpy.ops.object.modifier_add(type='SUBSURF')
        ob.modifiers['Subsurf'].levels = 3

        # Iterate over voxels to determine if each is inside the mesh, and write
        # result to file.
        if numpy_output:
            mask = numpy.zeros((M, M, M), dtype=bool)
            for n in range(0, M):
                for m in range(0, M):
                    for l in range(0, M):
                        if point_inside_mesh(mathutils.Vector(((l + 1) / M - 0.5, (m + 1) / M - 0.5, (n + 1) / M - 0.5)),
                                           ob):
                            mask[l, m, n] = True
            numpy.save(fileOut, mask)
        else:
            fo = open(fileOut, "w")
            for n in range(0, M):
                for m in range(0, M):
                    for l in range(0, M):
                        if point_inside_mesh(mathutils.Vector(((l + 1) / M - 0.5, (m + 1) / M - 0.5, (n + 1) / M - 0.5)),
                                           ob):
                            fo.write("1")
                        else:
                            fo.write("0")
                        if l < M - 1:
                            fo.write(" ")
                    fo.write("\n")
                fo.write("\n")
            fo.close()

        # Remove object after file is written.
        bpy.ops.object.delete()



main()







