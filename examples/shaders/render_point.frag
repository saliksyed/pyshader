// renders the fragment for the point
varying vec3 vPos;

void main()
{
    gl_FragColor = vec4(1., 0., vPos.z, 1.0);
}