#version 330

// in vec3 v2f_color;
// in vec2 v2f_uv;
// these are directions and should be already normalized
// in the vertex shader
in vec3 v2f_to_light_ws;
in vec3 v2f_normal_ws;
in vec3 v2f_to_cam_ws;

out vec4 out_color;

// uniform sampler2D texture0;
// uniform sampler2D texture1;
uniform vec3 color;
// if uniform starts with '_' is hidden
uniform vec3 _light_color;

// thinking how we can add decorators
// for uniforms
// maybe by default, of hte value is a float, just show it

// uniform float ambient_strength = 0.1f;
uniform float slider_0_1_ambient_strength = 0.1f;

// how much the surface reflect the incomming light
uniform float slider_0_1_reflectivity = 1.0f;  

// how much we damp the reflection the farther
// we are from the reflected ray
// struct Slider
// {
//     float shine_damper;
//     // if these are not used, they are going to be discarded
//     float min_val;  
//     float max_val;
// };

// we need a different way to communicate the
// slider data in the uniform
// final VARIABLE name has to follow this type:
// slider_<min>_<max>_<name>

// the only way to set default values for uniforms correctly in cpu
// is by setting up the material property at setup time

// float shine_damper = 32.0f;
// float min_val = 1.0f;
// float max_val = 32.0f;
// uniform Slider shine_damper;// = Slider(32.0f, 1.0f, 32.0f);
// uniform Slider shine_damper = Slider(32.0f, 1.0f, 32.0f);
uniform float slider_1_32_shine_damper = 32.0f; // [1,32]
// shine_damper.shine_damper = 32.0f;
// shine_damper.min_val = 1.0f;
// shine_damper.max_val = 32.0f;

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

    out_color = vec4((ambient_light + diffuse_light + specular_light) * color, 1);
}

