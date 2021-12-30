#version 330

// in vec3 v2f_color;
// in vec2 v2f_uv;
// these are directions and should be already normalized
// in the vertex shader
in vec3 v2f_to_light_ws;
in vec3 v2f_normal_ws;
in vec3 v2f_to_cam_ws;

out vec4 out_color;

// uniform vec3 color;
// uniform sampler2D texture0;
// uniform sampler2D texture1;
uniform vec3 light_color;

// how much the surface reflect the incomming light
uniform float reflectivity = 1.0f;  

// how much we damp the reflection the farther
// we are from the reflected ray
uniform float shine_damper = 32.0f;

void main()
{
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
    vec3 specular = (reflectivity * specular_factor) * light_color;
    out_color = vec4(specular,1);//diffuse * base color
}


