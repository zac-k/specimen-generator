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


def objectMask(ob, path):
    # ob = bpy.context.active_object

    M = 64
    fileOut = path + 'particle.txt'

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
    return




M = 64
path = '/output/path/'
filename = 'moment'
mask = bpy.data.objects['Cube.002']
objectMask(mask, path)
fox = open(path + filename + "_x.txt", "w")
foy = open(path + filename + "_y.txt", "w")
foz = open(path + filename + "_z.txt", "w")

veclist = bpy.context.selected_objects

for n in range(0, M):
    for m in range(0, M):
        for l in range(0, M):

            voxel = mathutils.Vector(((l + 1) / M - 0.5, (m + 1) / M - 0.5, (n + 1) / M - 0.5))
            if pointInsideMesh(voxel, mask):
                closestVec = veclist[0]
                distanceToPrevious = numpy.sqrt(
                    (veclist[0].location[0] - voxel[0]) * (veclist[0].location[0] - voxel[0]) + (
                    veclist[0].location[1] - voxel[1]) * (veclist[0].location[1] - voxel[1]) + (
                    veclist[0].location[2] - voxel[2]) * (veclist[0].location[2] - voxel[2]))

                for i in range(1, len(veclist)):
                    distanceSq = (veclist[i].location[0] - voxel[0]) * (veclist[i].location[0] - voxel[0]) \
                               + (veclist[i].location[1] - voxel[1]) * (veclist[i].location[1] - voxel[1]) \
                               + (veclist[i].location[2] - voxel[2]) * (veclist[i].location[2] - voxel[2])
                    distance = numpy.sqrt(distanceSq)
                    if distance < distanceToPrevious:
                        closestVec = veclist[i]
                    distanceToPrevious = distance

                rot = closestVec.rotation_euler
                rotMat = mathutils.Euler(rot).to_matrix()
                direction = rotMat * mathutils.Vector((0, 0, 1))

                fox.write(str(direction[0]))
                foy.write(str(direction[1]))
                foz.write(str(direction[2]))
            else:
                fox.write("0")
                foy.write("0")
                foz.write("0")
            if l < M - 1:
                fox.write(" ")
                foy.write(" ")
                foz.write(" ")
        fox.write("\n")
        foy.write("\n")
        foz.write("\n")
    fox.write("\n")
    foy.write("\n")
    foz.write("\n")
fox.close()
foy.close()
foz.close()




