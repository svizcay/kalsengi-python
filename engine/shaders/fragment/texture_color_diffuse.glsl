#version 330

// these are directions and should be already normalized
// in the vertex shader
in vec3 v2f_to_light_ws;
in vec3 v2f_normal_ws;
in vec2 v2f_uv;

out vec4 out_color;

uniform sampler2D texture0;
uniform vec3 _light_color;

void main()
{
    // brightness [0,1]
    float brightness = dot(
        v2f_to_light_ws,
        v2f_normal_ws
    );
    brightness = max(brightness, 0.0);

    vec3 diffuse_light = brightness * _light_color;// light_color
    out_color = vec4(diffuse_light, 1) * texture(texture0, v2f_uv); // diffuse * object color
}

