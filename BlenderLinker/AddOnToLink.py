import bpy
import math
import numpy as np

def distanceFormula(x1, y1, z1, x2, y2, z2):
    d = (x1-x2)**2 + (y1-y2)**2 +(z1-z2)**2
    d = d**.5
    return d

def centerList(list):
    topx = None
    bottomx = None
    topy = None
    bottomy = None
    topz = None
    bottomz = None
    for point in list:
        (x,y,z) = (point[0],point[1],point[2])
        if topx == None or x > topx:
            topx = x
        if topy == None or y > topy:
            topy = y
        if topz == None or z > topz:
            topz = z
        if bottomx == None or x < bottomx:
            bottomx = x
        if bottomy == None or y < bottomy:
            bottomy = y
        if bottomz == None or z < bottomz:
            bottomz = z
    return [(topx + bottomx)/2.0, (topy + bottomy)/2.0, (topz + bottomz)/2.0]

def cylinder_between(x1, y1, z1, x2, y2, z2, r):

  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1
  dist = math.sqrt(dx**2 + dy**2 + dz**2)

  bpy.ops.mesh.primitive_cylinder_add(
      radius = r,
      depth = dist,
      location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)
  )

  phi = math.atan2(dy, dx)
  theta = math.acos(dz/dist)

  bpy.context.object.rotation_euler[1] = theta
  bpy.context.object.rotation_euler[2] = phi




def getOuterPoints(obj1, obj2):
    coords1 = [(obj1.matrix_world * v.co) for v in obj1.data.vertices]
    coords1 = np.asarray(coords1)
    center1 = (np.mean(coords1, axis=0))

    coords2 = [(obj2.matrix_world * v.co) for v in obj2.data.vertices]
    coords2 = np.asarray(coords2)
    center2 = (np.mean(coords2, axis=0))

    minimumDistanceObj1 = dict()
    minimumDistanceObj2 = dict()

    for coord1 in coords1:
        minimumDistance = None
        for coord2 in coords2:
            distance = distanceFormula(coord1[0],coord1[1],coord1[2], coord2[0],coord2[1],coord2[2])
            if minimumDistance == None or distance < minimumDistance:
                minimumDistance = distance
        (minimumDistanceObj1)[minimumDistance] = coord1

    for coord2 in coords2:
        minimumDistance = None
        for coord1 in coords1:
            distance = distanceFormula(coord1[0],coord1[1],coord1[2], coord2[0],coord2[1],coord2[2])
            if minimumDistance == None or distance < minimumDistance:
                minimumDistance = distance
        (minimumDistanceObj2)[minimumDistance] = coord2


    threshold1 = int(len(minimumDistanceObj1) * .3)
    threshold2 = int(len(minimumDistanceObj2) * .3)

    minimumDistanceObj1List = (sorted(minimumDistanceObj1))[:threshold1]
    minimumDistanceObj2List = (sorted(minimumDistanceObj2))[:threshold2]


    obj1List = []
    obj2List = []

    for distance in minimumDistanceObj1List:
        obj1List += [minimumDistanceObj1[distance]]

    for distance in minimumDistanceObj2List:
        obj2List += [minimumDistanceObj2[distance]]



    center1 = centerList(obj1List)
    center2 = centerList(obj2List)

    cylinder_between(center1[0],center1[1],center1[2],center2[0],center2[1],center2[2], .1)



def connectObjects(object1,object2):

    getOuterPoints(object1,object2)


def addOn():

    NumSelectedObjects = 0

    for ob in bpy.context.scene.objects:
        if ob.select == True:
            NumSelectedObjects += 1
            if NumSelectedObjects == 1:
                object1 = ob
            elif NumSelectedObjects == 2:
                object2 = ob
            else:
                NumSelectedObjects = 0
                break

    if NumSelectedObjects == 2:
        connectObjects(object1,object2)






bl_info = {
    "name": "Link Two Objects",
    "category": "Object",
}


class ObjectLinker(bpy.types.Operator):
    """Object Linker"""
    bl_idname = "object.link_objects"
    bl_label = "Link Two Objects"
    bl_options = {'REGISTER', 'UNDO'}

    total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self,context):

        addOn()


        return {'FINISHED'}


addon_keymaps = []


def register():
    bpy.utils.register_class(ObjectLinker)


    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(ObjectLinker.bl_idname, 'L', 'PRESS', ctrl=True, shift=True)
    kmi.properties.total = 4
    addon_keymaps.append(km)

def unregister():
    bpy.utils.unregister_class(ObjectLinker)


    # handle the keymap
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    # clear the list
    del addon_keymaps[:]


if __name__ == "__main__":
    register()