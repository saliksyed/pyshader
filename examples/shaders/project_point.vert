// projects the point from world -> camera 

attribute vec3 vertex;
varying vec3 vPos;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;
    float distToCamera = -cs_position.z;
    gl_PointSize = max(2.0, (20.0 - pow(distToCamera, 0.9)));
    vPos = gl_Vertex.xyz;
}
