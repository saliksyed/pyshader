
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
    return map(lambda x : abs(int(x)) - 1, vals)

def parse_obj_file(path, obj_name=None):
    f = open(path, "r")
    ret = {}
    curr_obj = None
    count = 0
    while True:
        line = f.readline()
        if not line:
            break
        items = line.rstrip().split()
        if len(items) <= 1:
            continue
        current_mode = items[0]
        if curr_obj and obj_name and curr_obj != obj_name:
            continue
        if current_mode == "#":
            if items[1] == "object":
                if curr_obj != None:
                    # reverse since vertices are indexed via negative indicies
                    ret[curr_obj]["vertices"].reverse()
                curr_obj = items[2]
                count += 1
                print("Parsing object: %s" % curr_obj)
                ret[curr_obj] = {
                    "vertices": [],
                    "texture_coords": [],
                    "faces": [],
                    "normals": []
                }
        elif current_mode == "v":
            ret[curr_obj]["vertices"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "vn":
            ret[curr_obj]["normals"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "vt":
            ret[curr_obj]["texture_coords"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "f":
            ret[curr_obj]["faces"].append(map(parse_triangle_vertex, items[1:4]))

    return ret


def get_triangles_from_obj(file, obj_name=None, return_tex_coords=False):
    obj_objects = parse_obj_file(file)
    if obj_name:
        tmp_obj_objects = {}
        tmp_obj_objects[obj_name] = obj_objects[obj_name]
        obj_objects = tmp_obj_objects
    vertices = []
    texture_coords = []
    for obj_name in obj_objects:
        obj = obj_objects[obj_name]
        for face in obj["faces"]:
            a = face[0][0]
            b = face[1][0]
            c = face[2][0]
            va = np.array(obj["vertices"][a])
            vb = np.array(obj["vertices"][b])
            vc = np.array(obj["vertices"][c])
            vertices.append(va)
            vertices.append(vb)
            vertices.append(vc)
            if return_tex_coords:
                if "texture_coords" in obj:
                    ta = obj["texture_coords"][a]
                    tb = obj["texture_coords"][b]
                    tc = obj["texture_coords"][c]
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
                texture_coords.append(ta)
                texture_coords.append(tb)
                texture_coords.append(tc)
    return vertices, texture_coords


def read_faces_and_vertices_from_obj(path, verbose=False):
    f = open(path, "r")
    ret = {}
    curr_obj = None
    while True:
        line = f.readline()
        if not line:
            break
        items = line.rstrip().split()
        if len(items) <= 1:
            continue
        current_mode = items[0]
        if current_mode == "#":
            if items[1] == "object":
                curr_obj = items[2]
                if verbose:
                    print("Parsing object: %s" % curr_obj)
                ret[curr_obj] = {
                    "vertices": [],
                    "faces": []
                }
        elif current_mode == "v":
            ret[curr_obj]["vertices"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "f":
            ret[curr_obj]["faces"].append(map(lambda x : int(abs(x)), items[1:4]))
    return ret

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
