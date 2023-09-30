#define NUM_SAMPLES 8
#define NUM_RADIUS_SAMPLES 8
#define MAX_GRAD 0.01
#define texture texture2D
varying vec2 index;
uniform float iGlobalTime;
uniform vec2 iResolution;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;

// Finds the shortest path through the heat
vec2 compute_gradient(vec2 uv, sampler2D b) {
    vec2 gradient = vec2(0., 0.);
    float magnitude = -1.0;
    float mult = sin(iGlobalTime * 0.25) * 0.5 + 0.5;
    for(int i = 0; i <= NUM_SAMPLES; i++) {
        float t = (float(i)/float(NUM_SAMPLES)) * 6.28;
        for(int j = 0; j < NUM_RADIUS_SAMPLES; j++) {
            float r = float(j)/float(NUM_RADIUS_SAMPLES) * MAX_GRAD * mult;
            vec2 a = r * vec2(cos(t), sin(t));
            float l = length(texture(b, uv+a).rgb);
            if (magnitude < 0. || l < magnitude) {
                 magnitude = l;
                gradient = a;
            }
        }
    }
    return gradient;
}

vec3 compute_final_color(vec2 uv) {
    vec2 g = uv;
    // the total offset through 3 layers of heat
    g += 0.25*compute_gradient(g, iChannel0);
    g += 0.5*compute_gradient(g, iChannel0);
    g += (0.3 + 0.2*(sin(iGlobalTime)*0.5 + 0.5))*compute_gradient(g, iChannel0);
    return texture(iChannel1, g).rgb;
}


void main()
{
    vec2 uv = index;
    gl_FragColor = vec4(compute_final_color(uv), 1.);
}