varying float distToCamera;

void main()
{
 	gl_FragColor = vec4(vec3(distToCamera/500.0), 1);
}