#version 330

in vec2 v2f_uv;
in vec3 v2f_to_light_ws;
in vec3 v2f_normal_ws;
in vec3 v2f_to_cam_ws;

out vec4 out_color;

uniform sampler2D texture0;
uniform vec3 color;
// hidden
uniform vec3 _light_color;

uniform float slider_0_1_ambient_strength = 0.1f;
uniform float slider_0_1_reflectivity = 1.0f;  
uniform float slider_1_32_shine_damper = 32.0f; // [1,32]

void main()
{
    // alias
    float shine_damper = slider_1_32_shine_damper;
    float reflectivity = slider_0_1_reflectivity;
    float ambient_strength = slider_0_1_ambient_strength;

    // ambient light
    vec3 ambient_light = ambient_strength * _light_color;

    // diffuse light
    float brightness = dot(
        v2f_to_light_ws,
        v2f_normal_ws
    );
    brightness = max(brightness, 0.0);
    vec3 diffuse_light = brightness * _light_color;// light_color

    // specular light

    // reflect incomming light ray
    // reflect takes as parameter the incomming light ray
    // i.e, -light_pos in our case
    // it also takes the normal
    // both parameters needs to be in the same space
    // (world in our case)
    vec3 reflected_ray = reflect(
        -v2f_to_light_ws,
        v2f_normal_ws
    );
    float specular_factor = max(
        dot(reflected_ray, v2f_to_cam_ws),
        0
    );
    specular_factor = pow(specular_factor, shine_damper);
    vec3 specular_light = (reflectivity * specular_factor) * _light_color;

    vec4 texture_color = texture(texture0, v2f_uv);

    out_color = vec4((ambient_light + diffuse_light + specular_light) * color * texture_color.rgb, 1);
}
