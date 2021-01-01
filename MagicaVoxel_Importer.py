import os

import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, CollectionProperty
from bpy.types import Operator

import struct

bl_info = {
    "name": "MagicaVoxel VOX Importer",
    "author": "TechnistGuru",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import MagicaVoxel .vox files",
    "wiki_url": "",
    "category": "Import-Export"}


class ImportVox(Operator, ImportHelper):
    bl_idname = "import_scene.vox"
    bl_label = "Import Vox"
    bl_options = {'PRESET', 'UNDO'}
    
    files: CollectionProperty(name="File Path",
                              description="File path used for importing the VOX file",
                              type=bpy.types.OperatorFileListElement) 

    directory: StringProperty()
    
    filename_ext = ".vox"
    filter_glob: StringProperty(
        default="*.vox",
        options={'HIDDEN'},
    )

    voxel_size: FloatProperty(name = "Voxel Size", default=1.0)

    gamma_correct: BoolProperty(name="Gamma Correct Colors", default=True)
    gamma_value: FloatProperty(name="Gamma Correction Value", default=2.2, min=0)
    
    # Determins if palette colors are used.
    import_palette: BoolProperty(name="Import Palette", default=True) 
    # Determins if palette materials are used. Requires import_palette to be true and dosen't support all materials.
    import_materials: BoolProperty(name="Import Materials", default=True)
    
    override_materials: BoolProperty(name="Override Existing Materials", default=True)

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)
        
        for path in paths:
            import_vox(path, self.voxel_size, self.gamma_correct, self.gamma_value, self.import_palette, self.import_materials, self.override_materials)
        
        return {"FINISHED"}


class Vec3:
    x, y, z = 0.0, 0.0, 0.0
    
    def __init__(self, X, Y, Z):
        self.x, self.y, self.z = X, Y, Z

class VoxelObject:
    position = Vec3(0, 0, 0)
    size = Vec3(0, 0, 0)
    voxels = []
    
    def __init__(self, Size, Voxels):
        self.size = Size
        self.voxels = []
        for x in range(self.size.x):
            self.voxels.append([])
            for y in range(self.size.y):
                self.voxels[x].append([])
                for z in range(self.size.z):
                    self.voxels[x][y].append(0)
        
        for vox in Voxels:
            #              x       y       z        id
            self.voxels[vox[0]][vox[1]][vox[2]] = vox[3]
    
    def getVox(self, pos):
        if pos.x<0 or pos.x>=self.size.x or pos.y<0 or pos.y>=self.size.y or pos.z<0 or pos.z>=self.size.z:
            return 0
        return self.voxels[pos.x][pos.y][pos.z]
    
    def generate(self, use_mat, file_name, vox_size):
        objects = []
        
        for Col in range(1, 256): # Create an object for each color and then join them.
            
            mesh = bpy.data.meshes.new(file_name) # Create mesh
            obj = bpy.data.objects.new(file_name, mesh) # Create object
            bpy.context.scene.collection.objects.link(obj) # Link object to scene
            
            objects.append(obj) # Keeps track of created objects for joining.
            
            verts = []
            faces = []
            
            for x in range(self.size.x):
                for y in range(self.size.y):
                    for z in range(self.size.z):
                        
                        colID = self.voxels[x][y][z]
                        if colID != Col:
                            continue
                        
                        if self.getVox(Vec3(x+1, y, z)) == 0:
                            verts.append( (x+1, y, z) )
                            verts.append( (x+1, y+1, z) )
                            verts.append( (x+1, y+1, z+1) )
                            verts.append( (x+1, y, z+1) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                        
                        if self.getVox(Vec3(x, y+1, z)) == 0:
                            verts.append( (x+1, y+1, z) )
                            verts.append( (x+1, y+1, z+1) )
                            verts.append( (x, y+1, z+1) )
                            verts.append( (x, y+1, z) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                        
                        if self.getVox(Vec3(x, y, z+1)) == 0:
                            verts.append( (x, y, z+1) )
                            verts.append( (x, y+1, z+1) )
                            verts.append( (x+1, y+1, z+1) )
                            verts.append( (x+1, y, z+1) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                        
                        if self.getVox(Vec3(x-1, y, z)) == 0:
                            verts.append( (x, y, z) )
                            verts.append( (x, y+1, z) )
                            verts.append( (x, y+1, z+1) )
                            verts.append( (x, y, z+1) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                        
                        if self.getVox(Vec3(x, y-1, z)) == 0:
                            verts.append( (x, y, z) )
                            verts.append( (x, y, z+1) )
                            verts.append( (x+1, y, z+1) )
                            verts.append( (x+1, y, z) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                        
                        if self.getVox(Vec3(x, y, z-1)) == 0:
                            verts.append( (x, y, z) )
                            verts.append( (x+1, y, z) )
                            verts.append( (x+1, y+1, z) )
                            verts.append( (x, y+1, z) )
                            
                            faces.append( [len(verts)-4,
                                            len(verts)-3,
                                            len(verts)-2,
                                            len(verts)-1] )
                                        
            mesh.from_pydata(verts, [], faces)
            obj.scale = [vox_size, vox_size, vox_size]
            
            if use_mat:
                obj.data.materials.append(bpy.data.materials.get(file_name + " #" + str(Col)))
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True) # Select all objects that were generated.
        bpy.context.view_layer.objects.active = objects[0] # Make the first one active.
        bpy.ops.object.join() # Join selected objects.


def import_vox(path, voxel_size=1, gamma_correct=True, gamma_value=2.2, import_palette=True, import_materials=True, override_materials=True):
    
    with open(path, 'rb') as file:
        file_name = os.path.basename(file.name).replace('.vox', '')
        file_size = os.path.getsize(path)
        
        voxels = []
        palette = []
        materials = [[0, 0, 0, 0]]*255 # [roughness, metallic, glass, emission] * 255
        
        # Makes sure it's supported vox file
        assert (struct.unpack('<4ci', file.read(8)) == (b'V', b'O', b'X', b' ', 150))
        
        # MAIN chunk
        assert (struct.unpack('<4c', file.read(4)) == (b'M', b'A', b'I', b'N'))
        N, M = struct.unpack('<ii', file.read(8))
        assert (N == 0)
        
        objects = []
        
        while file.tell() < file_size:
            *name, h_size, h_children = struct.unpack('<4cii', file.read(12))
            name = b"".join(name)
            
            if name == b'SIZE':
                x, y, z = struct.unpack('<3i', file.read(12))
                size = Vec3(x, y, z)
            
            elif name == b'XYZI':
                num_voxels, = struct.unpack('<i', file.read(4))
                for voxel in range(num_voxels):
                    voxel_data = struct.unpack('<4B', file.read(4))
                    voxels.append(voxel_data)
                obj = VoxelObject(size, voxels)
                objects.append(obj)
            
            elif name == b'RGBA':
                for _ in range(255):
                    palette.append(struct.unpack('<4B', file.read(4)))
                file.read(4)
            
            elif name == b'MATL':
                id = struct.unpack('<i', file.read(4))[0]
                dict_size = struct.unpack('<i', file.read(4))[0] # Number of key:value pairs in material dictionary.
                
                for _ in range(dict_size):
                    key_size = struct.unpack('<i', file.read(4))[0]
                    key = struct.unpack('<'+str(key_size)+'c', file.read(key_size))
                    key = b"".join(key)
                    
                    value_size = struct.unpack('<i', file.read(4))[0]
                    value = struct.unpack('<'+str(value_size)+'c', file.read(value_size))
                    value = b"".join(value)
                    
                    if id > 255: # Why are there material values for id 256?
                        continue
                    
                    mat = materials[id-1]
                    
                    if key == b'_rough':
                        materials[id-1] = [float(value), mat[1], mat[2], mat[3]] # Roughness
                    elif key == b'_metal':
                        materials[id-1] = [mat[0], float(value), mat[2], mat[3]] # Metalic
                    elif key == b'_alpha':
                        materials[id-1] = [mat[0], mat[1], float(value), mat[3]] # Glass
                    elif key == b'_emit':
                        materials[id-1] = [mat[0], mat[1], mat[2], float(value)] # Emission
                    elif key == b'_flux':
                        materials[id-1] = [mat[0], mat[1], mat[2], mat[3]*(float(value)+1)] # Emission Power

            else:
                file.read(h_size)
    
    if not gamma_correct:
        gamma_value = 1
    
    if import_palette:
        for id, col in enumerate(palette):
            
            col = (pow(col[0]/255, gamma_value), pow(col[1]/255, gamma_value), pow(col[2]/255, gamma_value), col[3]/255)
            
            name = file_name + " #" + str(id+1)
            
            if name in bpy.data.materials:
                if not override_materials:
                    continue
                mat = bpy.data.materials[name]
            else:
                mat = bpy.data.materials.new(name = name)
                mat.use_nodes = True
            
            nodes = mat.node_tree.nodes
            bsdf = nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = col
            bsdf.inputs["Emission Strength"].default_value = 0
            
            if import_materials:
                bsdf.inputs["Roughness"].default_value = materials[id][0]
                bsdf.inputs["Metallic"].default_value = materials[id][1]
                bsdf.inputs["Transmission"].default_value = materials[id][2]
                bsdf.inputs["Emission Strength"].default_value = materials[id][3] * 20
                bsdf.inputs["Emission"].default_value = col
            
            mat.diffuse_color = col
    
    for obj in objects:
        obj.generate(import_palette, file_name, voxel_size)


def menu_func_import(self, context):
    self.layout.operator(ImportVox.bl_idname, text="MagicaVoxel (.vox)")

def register():
    bpy.utils.register_class(ImportVox)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportVox)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
