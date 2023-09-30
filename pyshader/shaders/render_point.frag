#version 120

// renders the fragment for the point
varying vec3 vPos;
uniform float iGlobalTime;
void main()
{
	vec2 coord = gl_PointCoord - vec2(0.5);  
	float dist_squared = dot(coord, coord);
	if (dist_squared > 0.25) {
		discard;
	}
	float c = pow((1.0 - gl_FragCoord.z), 0.5);


	float m1 = sin(iGlobalTime * 2.5)  * 0.5 + 0.5;

	float modulation = 0.6 + 0.4 * m1;

	float d = modulation * pow(vPos.y / 15.0, 0.5);
	vec4 mixColor = vec4(14.0/255.0, 116.0/255.0, 132.0/255.0, 1.0);
 	gl_FragColor = mix(vec4(d, d, d, 1.), mixColor , 0.3);
}