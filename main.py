# Requires "Blender" to run. Open file inside blender,
# set output_path, and run. Output format is a text file
# with each block of rows/columns representing a 2D slice
# of the binary specimen mask. Each block is separated
# by an empty line. Currently working in Blender 2.78a

import mathutils, numpy, bpy
import random as rnd

PI = numpy.pi


def pointInsideMesh(point, ob):
    axes = [mathutils.Vector((1, 0, 0))]
    outside1 = False
    for axis in axes:

        mat1 = mathutils.Matrix(ob.matrix_world)
        mat = mat1.invert()

        orig = mat1 * point

        count = 0
        while True:
            result, location, normal, index = ob.ray_cast(orig, axis * 10000.0)
            if index == -1: break
            count += 1

            orig = location + axis * 0.00001

        if (count % 2 == 0):
            outside1 = True
            break

    axes = [mathutils.Vector((0, 1, 0))]
    outside2 = False
    for axis in axes:

        mat1 = mathutils.Matrix(ob.matrix_world)
        mat = mat1.invert()

        orig = mat1 * point

        count = 0
        while True:
            result, location, normal, index = ob.ray_cast(orig, axis * 10000.0)
            if index == -1: break
            count += 1

            orig = location + axis * 0.00001

        if (count % 2 == 0):
            outside2 = True
            break

    outside = outside1 or outside2
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
    M = 64
    num_specimens = 10000
    start_number = 0

    output_path = '/output/path/'

    for i in range(num_specimens):
        fileOut = output_path + 'particle(' + str(i + start_number) + ')'

        scale = (
            rnd.uniform(0.12, 0.14),
            rnd.uniform(0.12, 0.14),
            rnd.uniform(0.12, 0.14)
        )
        radius = rnd.uniform(0.12, 0.14)
        offset = 0.05
        location = (
            rnd.uniform(-offset, offset),
            rnd.uniform(-0.05, 0.05),
            rnd.uniform(-offset, offset)
        )
        rotation = (
            rnd.uniform(0, 2 * PI),
            rnd.uniform(0, 2 * PI),
            rnd.uniform(0, 2 * PI)
        )

        bpy.ops.mesh.primitive_cube_add(
            location=location,
            rotation=rotation,
            radius=radius
        )

        ob_base = bpy.context.active_object
        fracture = False  # bool(rnd.randint(0, 1))
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

        construct = True
        if construct:
            fo = open(fileOut, "w")
            for n in range(0, M):
                for m in range(0, M):
                    for l in range(0, M):
                        if pointInsideMesh(mathutils.Vector(((l + 1) / M - 0.5, (m + 1) / M - 0.5, (n + 1) / M - 0.5)),
                                           ob):
                            fo.write("1")
                        else:
                            fo.write("0")
                        if l < M - 1:
                            fo.write(" ")
                    fo.write("\n")
                fo.write("\n")
            fo.close()
            bpy.ops.object.delete()


# bpy.ops.object.delete()
main()







