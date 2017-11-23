import mathutils, numpy, bpy


def pointInsideMesh(point, ob):
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


ob = bpy.context.active_object
M = 512
fileOut = 'path\\to\\file'

fo = open(fileOut, "w")
for n in range(0, M):
    for m in range(0, M):
        for l in range(0, M):
            if pointInsideMesh(mathutils.Vector(((l + 1) / M - 0.5, (m + 1) / M - 0.5, (n + 1) / M - 0.5)), ob):
                fo.write("1")
            else:
                fo.write("0")
            if l < M - 1:
                fo.write(" ")
        fo.write("\n")
    fo.write("\n")
fo.close()





