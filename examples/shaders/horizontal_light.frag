varying vec2 index;
uniform float iGlobalTime;
uniform vec2 iResolution;

float computeIllumination(vec2 light_start, float light_width, vec2 uv) {
    if (abs(uv.y - light_start.y) < 0.001 && (0.95*uv.x > light_start.x + light_width) || (uv.x < 0.95*light_start.x) ) {
        // correct for artifacts/banding near boundary conditions
        uv.y += 0.003;
    }
    vec2 p0 = vec2(light_start.x, light_start.y);
    vec2 p1 = vec2(light_start.x + light_width, light_start.y);
    // compute illumination based on equation:
    return log(p1.x-uv.x + length(uv - p1)) - log(p0.x-uv.x + length(uv-p0));

}

void main()
{
    // setup coordinate frame:
    vec2 uv = index;
    uv.x /= iResolution.y / iResolution.x;
    uv.y = 1. - uv.y;
    
    float illumination = 0.0;
    vec2 light_start = vec2(0.4, 0.5);
    illumination += 0.5*(0.5*sin(iGlobalTime)+1.0) * computeIllumination(light_start, 0.7, uv);
    gl_FragColor = vec4(vec3(sqrt(0.3*illumination)), 1.);
}