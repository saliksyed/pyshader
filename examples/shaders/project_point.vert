// projects the point from world -> camera 

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
attribute vec3 vertex;
varying vec3 vPos;

void main()
{
    gl_Position = projection * view * model * vec4(vertex.xyz, 1.);
    vPos = vertex;
    gl_PointSize = 1.0;
}
