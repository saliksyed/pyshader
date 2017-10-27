from array import array
import json

def load(filename):
    input_file = open(filename, 'rb')
    line = input_file.readline()
    header = json.loads(line)
    # TODO: shouldn't be hard coded
    FLOAT_SIZE_BYTES = 8
    ret = {}
    for key in header:
        float_array = array('d')
        float_array.fromstring(input_file.read(header[key]*FLOAT_SIZE_BYTES))
        print float_array
        vertices = []
        for i in xrange(0, len(float_array)/3):
            vertices.append([float_array[i*3], float_array[i*3 + 1], float_array[i*3 + 2]])
        ret[key] = vertices
    return ret

def dump(data, filename):
    header = {}
    for key in data:
        header[key] = len(data[key]) * 3
    header_str = json.dumps(header) + '\n'

    output_file = open(filename, 'wb')
    output_file.write(header_str.encode('ascii'))
    for key in data:
        flattened = []
        for sample in data[key]:
            flattened += sample
        float_array = array('d', flattened)
        float_array.tofile(output_file)
        
if __name__ == '__main__':
	# simple sanity check:
	a = {"vtx":[[1,2,3],[2,3,4]], "foo":[[1,2,3]]}
	dump(a, "test")
	b = load("test")
	print b
	print a
