// projects the point from world -> camera 

attribute vec3 vertex;
varying vec3 vPos;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vPos = vertex;
    gl_PointSize = 0.5;
}
