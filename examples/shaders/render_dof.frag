varying vec2 index;
uniform vec2 iResolution;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;

uniform float minDistInFocus;
uniform float maxDistInFocus;
uniform float maxNearBlur;
uniform float maxFarBlur;


// Gaussian blur shader based on : https://www.shadertoy.com/view/XdfGDH

float normpdf(in float x, in float sigma)
{
	return 0.39894*exp(-0.5*x*x/(sigma*sigma))/sigma;
}


void main() 
{

    // setup coordinate frame:
    vec2 uv = index;
	
	const int mSize = 11;
	const int kSize = (mSize-1)/2;
	float kernel[mSize];
	vec3 final_colour = vec3(0.0);
	
	//create the 1-D kernel
	float dist = texture2D(iChannel1, uv.xy).r;
	float sigma = 1.0;
	if (dist > maxDistInFocus) {
		sigma = max(1.0, ((dist - maxDistInFocus) / maxDistInFocus) * maxFarBlur);
	} else if (dist < minDistInFocus) {
		sigma = max(1.0, ((minDistInFocus - dist) / minDistInFocus) * maxNearBlur);
	} else {
		gl_FragColor = vec4(texture2D(iChannel0, uv.xy).rgb, 1.0);
		return;
	}

	float Z = 0.0;
	for (int j = 0; j <= kSize; ++j)
	{
		kernel[kSize+j] = kernel[kSize-j] = normpdf(float(j), sigma);
	}
	
	//get the normalization factor (as the gaussian has been clamped)
	for (int j = 0; j < mSize; ++j)
	{
		Z += kernel[j];
	}
	
	//read out the texels
	for (int i=-kSize; i <= kSize; ++i)
	{
		for (int j=-kSize; j <= kSize; ++j)
		{
			vec2 delta = vec2(float(i),float(j))/iResolution.xy;
			final_colour += kernel[kSize+j]*kernel[kSize+i]*texture2D(iChannel0, uv.xy + delta).rgb;

		}
	}
	
	
	gl_FragColor = vec4(final_colour/(Z*Z), 1.0);


}
