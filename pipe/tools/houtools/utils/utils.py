import hou
import numpy as np
import math

def houdini_main_window():
    return hou.ui.mainQtWindow()

def layout_object_level_nodes():
    node = hou.node("/obj")
    node.layoutChildren()

def convert_to_matrix(x, y, z):
    return np.matrix([  [x],
                        [y],
                        [z],
                        [1]])


def do_translate_matrix(x, y, z, point):
    t = np.matrix([  [1,0,0,x],
                        [0,1,0,y],
                        [0,0,1,z],
                        [0,0,0,1]])

    r = np.matmul(t, point)

    return r

def do_rotate_matrix(x, y, z, point):
    x_rad = x * math.pi/180
    y_rad = y * math.pi/180
    z_rad = z * math.pi/180

    cos_x = math.cos(x_rad)
    cos_y = math.cos(y_rad)
    cos_z = math.cos(z_rad)

    sin_x = math.sin(x_rad)
    sin_y = math.sin(y_rad)
    sin_z = math.sin(z_rad)

    print("sin x y z: ", sin_x, sin_y, sin_z)
    print("cos x y z: ", cos_x, cos_y, cos_z)

    rx = np.matrix([    [1,0,0,0],
                        [0,cos_x,-sin_x,0],
                        [0,sin_x,cos_x,0],
                        [0,0,0,1]])

    ry = np.matrix([    [cos_y,0,sin_y,0],
                        [0,1,0,0],
                        [-sin_y,0,cos_y,0],
                        [0,0,0,1]])

    rz = np.matrix([    [cos_z,-sin_z,0,0],
                        [sin_z,cos_z,0,0],
                        [0,0,1,0],
                        [0,0,0,1]])

    print("rx: ", rx)
    print("ry: ", ry)
    print("rz: ", rz)

    r = np.matmul(rx, point)
    print("r and point: ", r)
    r = np.matmul(ry, r)
    print("ry and r: ", r)
    r = np.matmul(rz, r)
    print("rz and r: ", r)

    return r

def do_scale_matrix(x, y, z, point):
    s = np.matrix([  [x,0,0,0],
                        [0,y,0,0],
                        [0,0,z,0],
                        [0,0,0,1]])

    r = np.matmul(s, point)

    return r
