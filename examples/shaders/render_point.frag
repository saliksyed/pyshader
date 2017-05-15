#version 120

// renders the fragment for the point
varying vec3 vPos;
uniform float iGlobalTime;
void main()
{
	vec2 coord = gl_PointCoord - vec2(0.5);  
	float dist_squared = dot(coord, coord);
	if (dist_squared > 0.25) discard;
	float c = pow((1.0 - gl_FragCoord.z), 0.5);


	float m1 = sin(iGlobalTime * 2.5)  * 0.5 + 0.5;

	float modulation = 0.8 + 0.2 * m1;
 	gl_FragColor = vec4(modulation * pow(vPos.y / 15.0, 0.5), c, c, 0.5); //
}