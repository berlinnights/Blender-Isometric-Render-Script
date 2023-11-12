# Isometric Animation Renderer, Export working in 3.0.0, but not in 3.6.3
# Script for automatically setting up Camera and Light Positions, based on angle and direction

"How To Use"
# 1. Enter your Setup Variables, expecially the export_folder ! ( It will be automatically created)
# 2. Start the script
# 3. Shortcut N to open the sidebar, Go to Anim Renderer
# 4. Set the Animation on the Armature
# 5. Save the Animation. The Animation will be exported as single frames.
# 6. Aseprite can import the animation automatically, when opening the first frame.


""" SETUP VARIABLES """

export_folder = "" 
# e.g.: C:/Users/<Your User Name>/Desktop/BlenderFiles/

project_name  = "TestProject"
character_name = "TestCharacter"
# Names for file_name generation

armature_name = 'Armature'
# Name in the Scene Tree

resolution = 128 
# pixel

directions = 4  
# variable for the file_name generation
# set to 1 if you only want to render from one direction. 
# The direction won't be added to the file_name

camDistance = 5

camAngle = 45

cam_shift_y = 0  
# Positive Values will lower the model on the frame in percent
# 0 => Center ; 0.25 => Lower half ; 0.5 => Bottom Edge

sunlightShift = 25  
# Degrees; Rotation compared to the camera ; 0° => Sun is behind the camera

sun_angle = 20      
# Degrees ; Height above the horizon ; 0 => Sun above character ; 90 => Sun on Horizon

sunStrength = 2     
# Leave on 2 or above for the ShadowCatcherMaterial

frame_reducing = 3 # Animation_Length / x => Frames Output ; 30/x => FPS

motion_blur = True
motion_blur_shutter = 0.5 # 0 defined - 1 smeared/blurred
motion_blur_steps = 8 # Higher number, means more render time

filter_size = 0.25 # 0.01 for hard edges - 1.5 for blurred edges



"""ADDON : IS SET FROM THE MENU 
-> 3D VIEW/SIDEBAR [Shortcut: N] /Anim Renderer"""

import bpy
from bpy.app.handlers import persistent
import os
import math

SQR2 = 1.41421356237
dir = "SW"

scene = bpy.context.scene
pi = math.pi

sun = bpy.data.objects['Sun']
sun["Shift"] = sunlightShift

cam = bpy.data.objects['Camera']
z_pos = cam.location[2]

bpy.context.scene.render.resolution_x = resolution
bpy.context.scene.render.resolution_y = resolution

ortho = True

if ortho:
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = camDistance
    cam.data.shift_y = cam_shift_y
else:
    cam.data.type = 'PERSP'

bpy.context.scene.eevee.use_gtao = True

for obj in list(bpy.data.lights):
    if obj.name.find("Sun") != -1:
        obj.energy = sunStrength


def setup_film():
    bpy.context.scene.eevee.use_motion_blur = motion_blur
    if motion_blur:
        bpy.context.scene.eevee.motion_blur_shutter = motion_blur_shutter
        bpy.context.scene.eevee.motion_blur_steps = motion_blur_steps
    bpy.data.scenes["Scene"].render.resolution_x = resolution
    bpy.data.scenes["Scene"].render.resolution_y = resolution
    bpy.context.scene.render.filter_size = filter_size
    
    bpy.data.scenes["Scene"].render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format='PNG'


"""Get Data"""


def get_last_key_frame():
    fcurves = bpy.data.objects[armature_name].animation_data.action.fcurves
    for fcurve in fcurves:
        point = fcurve.keyframe_points[-1]
        return int(point.co.x)


def get_current_animation_name():
    return bpy.data.objects[armature_name].animation_data.action.name


def get_save_path(_dir):
    path = ""
    if directions == 1:
        path = export_folder+project_name+"/"+character_name+"/"+get_current_animation_name()+"/"+character_name+"_"+get_current_animation_name()+"_"
    else:
        path = export_folder+project_name+"/"+character_name+"/"+get_current_animation_name()+"/"+_dir+"/"+character_name+"_"+get_current_animation_name()+"_"+_dir+"_"
    bpy.context.scene.render.filepath = path
    return path


save_path = get_save_path(dir) 
bpy.context.scene.render.filepath = save_path


""" SET """


def set_savepath():
    bpy.context.scene.render.filepath = get_save_path(dir)


def set_cam_location(x,y,z):
    cam.location[0] = x
    cam.location[1] = y
    cam.location[2] = z
    cam.data.ortho_scale = abs(camDistance)


def set_cam_rotation_z(z):
    cam.rotation_euler[2] = z*pi/180
    cam.rotation_euler[0] = (90-cam["Angle"])*pi/180
    for obj in list(bpy.data.objects):
        if obj.name.find("Sun") != -1:
            obj.rotation_euler[2] = (z+bpy.data.objects['Sun']["Shift"])*pi/180


def calculate_z(d,a):
    camDistanceOnPlane = math.sqrt(d*d+d*d)
    tanValue = math.tan((a)*pi/180)
    z_pos = tanValue*camDistanceOnPlane
    cam["Distance"] = d
    cam["Angle"] = a
    cam["Height"] = z_pos
    set_cam_location(d,-d,z_pos)
    set_cam_rotation_z(45)
    return z_pos


replaceArray = ["SW","WN","NE","ES","S","W","N","E"]
def replace_file_path(_new):
    dir = _new
    save_path = get_save_path(_new)
    bpy.context.scene.render.filepath = save_path


""" SAVE ANIMATION """


def save_animation():
    start_frame = bpy.data.scenes["Scene"].frame_start
    end_frame = bpy.data.scenes["Scene"].frame_end
    bpy.data.scenes["Scene"].frame_end = get_last_key_frame()
    i = 0
    id = 0
    CurrentSavePath = bpy.context.scene.render.filepath
    while i <= get_last_key_frame()-bpy.data.scenes["Scene"].frame_start:
        bpy.data.scenes["Scene"].frame_current = i+bpy.data.scenes["Scene"].frame_start
        bpy.context.scene.render.filepath = CurrentSavePath+str(id).zfill(4)
        bpy.ops.render.render(use_viewport = True, write_still=True)
        i += frame_reducing
        id += 1
        print(CurrentSavePath+str(id).zfill(4))
    
    bpy.context.scene.render.filepath = CurrentSavePath



""" SUN """


def set_sun_props(i,c,a,s):
    for obj in list(bpy.data.lights):
        if obj.name.find("Sun") != -1:
            obj.energy = i
            obj.color = c
            obj["Shift"] = s
    for obj in list(bpy.data.objects):
        if obj.name.find("Sun") != -1:
            obj.rotation_euler[0] = a
            obj.rotation_euler[2] = (bpy.data.objects['Camera'].rotation_euler[2]+s)
            bpy.data.objects['Sun']["Shift"] = s*180/pi


class WM_OT_SunPropsPopup(bpy.types.Operator):
    bl_label = "Sun"
    bl_idname = "wm.sunpropspopup"
    bl_description = "Set Sun Properties"
    shift: bpy.props.FloatProperty(name="Z Angle (Camera Shift)", subtype='ANGLE',default=sunlightShift*pi/180)
    angle: bpy.props.FloatProperty(name="X Angle", subtype='ANGLE',default=sun_angle*pi/180)
    strength: bpy.props.FloatProperty(name="Strength",default=sunStrength)
    color: bpy.props.FloatVectorProperty(name="Color",subtype='COLOR',default=(1.0,1.0,1.0))
    def execute(self,context):
        set_sun_props(self.strength,self.color,self.angle,self.shift)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

set_sun_props(sunStrength,(1.0,1.0,1.0),sun_angle*pi/180,sunlightShift*pi/180)

""" CAMERA """


class WM_OT_CamPopup(bpy.types.Operator):
    bl_label = "Settings"
    bl_idname = "wm.campopup"
    bl_description = "CamProperties"
    Distance: bpy.props.FloatProperty(name="Distance", default = camDistance, subtype='DISTANCE',min= 0,soft_min = 3,soft_max = 100)
    Angle: bpy.props.FloatProperty(name="Angle", subtype='ANGLE',default = camAngle*pi/180)
    def execute(self,context):
        calculate_z(self.Distance,self.Angle*180/pi)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_CamSetter(bpy.types.Operator):
    bl_idname = "object.camsetter"
    bl_label = "Cam Location Setter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets the camera position to the precalculated points. \n(Change Script Parameters for different cam angle or cam distance)"
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    #rot_x: bpy.props.FloatProperty(name="X.Rot")
    rot_z: bpy.props.FloatProperty(name="Z Rot.")
    nameExt: bpy.props.StringProperty(name="Name Ext.")
    #my_bool: bpy.props.BoolProperty(name="Toggle Option")
    #my_string: bpy.props.StringProperty(name="String Value")
    
    def execute(self, context):
        self.report(
            {'INFO'}, 'X: %.2f  Y: %.2f  Z: %.2f' %
            (self.x, self.y, self.rot_z)
        )
        cam = bpy.data.objects['Camera']
        set_cam_location(self.x*cam["Distance"],self.y*cam["Distance"],cam["Height"])
        set_cam_rotation_z(self.rot_z)
        replace_file_path(self.nameExt)
        return {'FINISHED'}



""" ANIMATION RENDER BUTTONS """


class OBJECT_OT_CamRenderer1(bpy.types.Operator):
    bl_idname = "object.camrenderer1"
    bl_label = "Save Animation"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Saves the animation in the current direction"
    bpy.data.scenes["Scene"].frame_end = int(get_last_key_frame())
    def execute(self, context):
        if export_folder == "":
            self.report(
                {'ERROR'}, 'No Save Path! Enter a path in the export_folder variable inside the script.'
            )
            return {'FINISHED'}
        self.report(
            {'INFO'}, 'Render Animations in 1 Directions')
        
        self.report(
            {'INFO'}, 'Saved from Frame %.0f  to %.0f ' %
        (bpy.data.scenes["Scene"].frame_start, get_last_key_frame())
    )
        save_animation()
        return {'FINISHED'}


class OBJECT_OT_CamRenderer4(bpy.types.Operator):
    bl_idname = "object.camrenderer4"
    bl_label = "Save 4 Animations (iso)"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Saved the animation for 4 Directions (This can take a while!)"
    
    def execute(self, context):
        if export_folder == "":
            self.report(
                {'ERROR'}, 'No Save Path! Enter a path in the export_folder variable inside the script.'
            )
            return {'FINISHED'}
        self.report(
            {'INFO'}, 'Rendered Animations in 4 Directions')
        save_path = get_save_path(dir)
        start_frame = bpy.data.scenes["Scene"].frame_start
        end_frame = bpy.data.scenes["Scene"].frame_end
        
        set_cam_location(cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(45)
        replace_file_path("SW")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved SW")
        
        set_cam_location(cam["Distance"],cam["Distance"],cam["Height"])
        set_cam_rotation_z(135)
        replace_file_path("WN")
        bpy.ops.object.camrenderer1()
        print("Saved WN")
        
        set_cam_location(-cam["Distance"],cam["Distance"],cam["Height"])
        set_cam_rotation_z(225)
        replace_file_path("NE")
        bpy.ops.object.camrenderer1()
        print("Saved NE")
        
        set_cam_location(-cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(315)
        replace_file_path("ES")
        bpy.ops.object.camrenderer1()
        print("Saved ES")
        
        set_cam_location(cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(45)
        replace_file_path("SW")
        
        print("Saved 4 Anims")
        return {'FINISHED'}


class OBJECT_OT_CamRenderer8(bpy.types.Operator):
    bl_idname = "object.camrenderer8"
    bl_label = "Save 8 Animations"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Saved the animation for 8 Directions (This can take a while!)"
    
    def execute(self, context):
        if export_folder == "":
            self.report(
                {'ERROR'}, 'No Save Path! Enter a path in the export_folder variable inside the script.'
            )
            return {'FINISHED'}
        self.report(
            {'INFO'}, 'Rendered Animations in 8 Directions')
        #save_path = get_save_path()
        start_frame = bpy.data.scenes["Scene"].frame_start
        end_frame = bpy.data.scenes["Scene"].frame_end
        
        set_cam_location(0,-cam["Distance"]*SQR2,cam["Height"])
        set_cam_rotation_z(0)
        replace_file_path("S")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved S")
        
        set_cam_location(cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(45)
        replace_file_path("SW")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved SW")
        
        set_cam_location(cam["Distance"]*SQR2,0,cam["Height"])
        set_cam_rotation_z(90)
        replace_file_path("W")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved W")
        
        set_cam_location(cam["Distance"],cam["Distance"],cam["Height"])
        set_cam_rotation_z(135)
        replace_file_path("WN")
        bpy.ops.object.camrenderer1()
        print("Saved WN")
        
        set_cam_location(0,cam["Distance"]*SQR2,cam["Height"])
        set_cam_rotation_z(180)
        replace_file_path("N")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved N")
        
        set_cam_location(-cam["Distance"],cam["Distance"],cam["Height"])
        set_cam_rotation_z(225)
        replace_file_path("NE")
        bpy.ops.object.camrenderer1()
        print("Saved NE")
        
        set_cam_location(-cam["Distance"]*SQR2,0,cam["Height"])
        set_cam_rotation_z(270)
        replace_file_path("E")
        current_frame = start_frame
        bpy.ops.object.camrenderer1()
        print("Saved E")
        
        set_cam_location(-cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(315)
        replace_file_path("ES")
        bpy.ops.object.camrenderer1()
        print("Saved ES")
        
        set_cam_location(cam["Distance"],-cam["Distance"],cam["Height"])
        set_cam_rotation_z(45)
        replace_file_path("SW")
        
        print("Saved 8 Anims")
        return {'FINISHED'}


class BUTTON_AnimSetter(bpy.types.Operator):
    bl_idname = 'wm.setanimend'
    bl_label = 'Update Anim Length'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        bpy.data.scenes["Scene"].frame_end = int(get_last_key_frame())
        save_path = get_save_path("SW")
        bpy.context.scene.render.filepath = save_path
        return {"FINISHED"}



""" MAIN PANEL """


class MAIN_PANEL(bpy.types.Panel):
    bl_label = "Animation Renderer"
    bl_idname = "OBJECT_PT_CamSetter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Anim Renderer"
    
    def draw(self,context):
        self.layout.label(text="Sun", icon = 'LIGHT')
        self.layout.operator('wm.sunpropspopup')
        
        self.layout.label(text="Camera", icon = 'OUTLINER_DATA_CAMERA')
        self.layout.operator('wm.campopup')
        
        cam_setter_s = self.layout.operator('object.camsetter', text = "S")
        cam_setter_s.x = 0
        cam_setter_s.y = -1.41421356237
        cam_setter_s.z = z_pos
        cam_setter_s.rot_z = 0
        cam_setter_s.nameExt = "S"
        
        cam_setter_sw = self.layout.operator('object.camsetter', text = "SW")
        cam_setter_sw.x = 1
        cam_setter_sw.y = -1
        cam_setter_sw.z = z_pos
        cam_setter_sw.rot_z = 45
        cam_setter_sw.nameExt = "SW"
        
        cam_setter_w = self.layout.operator('object.camsetter', text = "W")
        cam_setter_w.x = 1.41421356237
        cam_setter_w.y = 0
        cam_setter_w.z = z_pos
        cam_setter_w.rot_z = 90
        cam_setter_w.nameExt = "W"
               
        cam_setter_wn = self.layout.operator('object.camsetter',text = "WN")
        cam_setter_wn.x = 1
        cam_setter_wn.y = 1
        cam_setter_wn.z = z_pos
        cam_setter_wn.rot_z = 135
        cam_setter_wn.nameExt = "WN"

        self.layout.label(text="Render", icon = 'RENDER_ANIMATION')
        self.layout.operator('object.camrenderer1')
        self.layout.operator('object.camrenderer4')
        self.layout.operator('object.camrenderer8')
        self.layout.operator('wm.setanimend')

                                                                          

#set_cam_location(camDistance,-camDistance,z_pos)
#set_cam_rotation_z(45)  

set_savepath()
setup_film()

bpy.utils.register_class(WM_OT_SunPropsPopup)
bpy.utils.register_class(WM_OT_CamPopup)

bpy.utils.register_class(BUTTON_AnimSetter)
bpy.utils.register_class(OBJECT_OT_CamRenderer4)
bpy.utils.register_class(OBJECT_OT_CamRenderer8)
bpy.utils.register_class(OBJECT_OT_CamRenderer1)
bpy.utils.register_class(OBJECT_OT_CamSetter)
bpy.utils.register_class(MAIN_PANEL)
