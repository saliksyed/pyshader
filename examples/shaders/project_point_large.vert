// projects the point from world -> camera 

attribute vec3 vertex;
varying float distToCamera;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;
    distToCamera = -cs_position.z;
    gl_PointSize = 1.0;
}
