// projects the point from world -> camera 

attribute vec3 vertex;
varying vec3 vPos;
varying float distToCamera;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;
    distToCamera = -cs_position.z;
    if (distToCamera < 55.0) {
    	gl_PointSize = 2.0; 
    } else {
    	gl_PointSize = 1.0; 
    }
    
    vPos = gl_Vertex.xyz;
}
