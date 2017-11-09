import numpy as np


QUAD_VERTEX_SHADER = """
attribute vec2 points;
varying vec2 coord;
varying vec2 index;

void main() {
    index = (points + 1.0) / 2.0;
    coord = (points * vec2(1, -1) + 1.0) / 2.0;
    gl_Position = vec4(points, 0.0, 1.0);
}
"""


TEXTURE_FRAG_SHADER = """
uniform sampler2D inputImage;
varying vec2 index;

void main() {
    gl_FragColor = texture2D(inputImage, index);
}
"""

FLIPPED_TEXTURE_FRAG_SHADER = """
uniform sampler2D inputImage;
varying vec2 index;

void main() {
    gl_FragColor = texture2D(inputImage, vec2(index.x, 1.0 - index.y));
}
"""



def parse_triangle_vertex(line):
    vals = filter(lambda x : len(x) > 0, line.split("/"))
    return map(lambda x : int(x) , vals)

def parse_obj_file(path, obj_name=None, scale=1.0, translate=[0, 0, 0]):
    f = open(path, "r")
    ret = {}
    curr_obj = None
    vtx_list = []
    texcoord_list = []
    normal_list = []
    count = 0
    last_mode = None
    default_count = 0
    while True:
        line = f.readline()
        if not line:
            break
        items = line.rstrip().split()
        if len(items) <= 1:
            continue
        current_mode = items[0]
        if (current_mode == "#" and items[1] == "object") or current_mode=="o":
            if curr_obj != None:
                # reverse since vertices are indexed via negative indicies
                ret[curr_obj]["vtx_offset"] = len(vtx_list)
                ret[curr_obj]["texcoord_offset"] = len(texcoord_list)
                ret[curr_obj]["normal_offset"] = len(normal_list)
            curr_obj = items[-1]
            count += 1
            ret[curr_obj] = {
                "texture_coords": [],
                "faces": [],
                "normals": []
            }
        elif current_mode == "v":
            # handle the case where no name is specified
            if curr_obj == None:
                curr_obj = "default" + str(default_count)
                ret[curr_obj] = {
                    "texture_coords": [],
                    "faces": [],
                    "normals": []
                }
                default_count += 1
            elif last_mode=="f":
                ret[curr_obj]["vtx_offset"] = len(vtx_list)
                ret[curr_obj]["texcoord_offset"] = len(texcoord_list)
                ret[curr_obj]["normal_offset"] = len(normal_list)
                default_count += 1
                curr_obj = "default" + str(default_count)
                ret[curr_obj] = {
                    "texture_coords": [],
                    "faces": [],
                    "normals": []
                }
            vtx = map(lambda x : scale*float(x), items[1:])
            vtx[0] += translate[0]
            vtx[1] += translate[1]
            vtx[2] += translate[2]
            vtx_list.append(vtx)
        elif current_mode == "vn":
            normal_list.append(map(lambda x : float(x), items[1:]))
        elif current_mode == "vt":
            texcoord_list.append(map(lambda x : float(x), items[1:]))
        elif current_mode == "f":
            ret[curr_obj]["faces"].append(map(parse_triangle_vertex, items[1:4]))
        last_mode = current_mode
    if curr_obj != None:
        ret[curr_obj]["vtx_offset"] = len(vtx_list)
        ret[curr_obj]["texcoord_offset"] = len(texcoord_list)
        ret[curr_obj]["normal_offset"] = len(normal_list)
    return ret, vtx_list, texcoord_list, normal_list


def get_triangles(obj_objects, vtx_list, texcoord_list, normal_list, obj_name=None, return_tex_coords=False, return_normals=False):
    if obj_name:
        tmp_obj_objects = {}
        tmp_obj_objects[obj_name] = obj_objects[obj_name]
        obj_objects = tmp_obj_objects
    vertices = []
    texture_coords = []
    normals = []
    for obj_name in obj_objects:
        obj = obj_objects[obj_name]
        vtx_offset = obj_objects[obj_name]["vtx_offset"]
        texcoord_offset = obj_objects[obj_name]["texcoord_offset"]
        normal_offset = obj_objects[obj_name]["normal_offset"]
        for face in obj["faces"]:
            a = face[0][0]
            b = face[1][0]
            c = face[2][0]
            if a < 0:
                a += vtx_offset
            else:
                a -= 1

            if b < 0:
                b += vtx_offset
            else:
                b -= 1
            if c < 0:
                c += vtx_offset
            else:
                c -= 1
            va = np.array(vtx_list[a])
            vb = np.array(vtx_list[b])
            vc = np.array(vtx_list[c])
            vertices.append(va)
            vertices.append(vb)
            vertices.append(vc)
            if return_tex_coords:
                if "texture_coords" in obj and len(face[0])>1:
                    a = face[0][1]
                    b = face[1][1]
                    c = face[2][1]
                    if a < 0:
                        a += texcoord_offset
                    else:
                        a -= 1

                    if b < 0:
                        b += texcoord_offset
                    else:
                        b -= 1
                    if c < 0:
                        c += texcoord_offset
                    else:
                        c -= 1
                    ta = texcoord_list[a]
                    tb = texcoord_list[b]
                    tc = texcoord_list[c]
                else:
                    ta = [0.0,0.0, 0.0]
                    tb = [0.0,0.0, 0.0]
                    tc = [0.0,0.0, 0.0]
                
                if len(ta) < 3: #force 3D tex coords if 2D found
                    ta.append(0.0)
                if len(tb) < 3:
                    tb.append(0.0)
                if len(tc) < 3:
                    tc.append(0.0)
                texture_coords.append(np.array(ta))
                texture_coords.append(np.array(tb))
                texture_coords.append(np.array(tc))

            if return_normals:
                if "normals" in obj and len(face[0])>2:
                    a = face[0][2]
                    b = face[1][2]
                    c = face[2][2]
                    if a < 0:
                        a += normal_offset
                    else:
                        a -= 1

                    if b < 0:
                        b += normal_offset
                    else:
                        b -= 1
                    if c < 0:
                        c += normal_offset
                    else:
                        c -= 1
                    ta = normal_list[a]
                    tb = normal_list[b]
                    tc = normal_list[c]
                else:
                    ta = [0.0,0.0, 0.0]
                    tb = [0.0,0.0, 0.0]
                    tc = [0.0,0.0, 0.0]
                
                if len(ta) < 3: #force 3D tex coords if 2D found
                    ta.append(0.0)
                if len(tb) < 3:
                    tb.append(0.0)
                if len(tc) < 3:
                    tc.append(0.0)
                normals.append(np.array(ta))
                normals.append(np.array(tb))
                normals.append(np.array(tc))
    return vertices, texture_coords, normals

def get_triangles_from_obj(file, obj_name=None, return_tex_coords=False, return_normals=False, scale=1.0, translate=[0, 0, 0]):
    obj_objects, vtx_list, texcoord_list, normal_list = parse_obj_file(file, scale=scale, translate=translate)
    vertices, texture_coords, normals = get_triangles(obj_objects, vtx_list, texcoord_list, normal_list, obj_name, return_tex_coords, return_normals)
    return vertices, texture_coords, normals


def read_points_from_ply(fname):
    vertices = []
    header_ended = False
    with open(fname, "r") as f:
        for line in f.readlines():
            line = line.rstrip()
            if header_ended:
                vertices.append(map(float, line.split()))
            elif line == "end_header":
                header_ended = True
            else:
                continue
    return vertices

def nearest_pow2(aSize):
    return math.pow(2, round(math.log(aSize) / math.log(2))) 
