#version 330

// in vec3 v2f_color;
// in vec2 v2f_uv;
// these are directions and should be already normalized
// in the vertex shader
in vec3 v2f_to_light_ws;
in vec3 v2f_to_camera_ws;
in vec3 v2f_normal_ws;

out vec4 out_color;

// uniform vec3 color;
// uniform sampler2D texture0;
// uniform sampler2D texture1;
uniform vec3 _light_color;

void main()
{
    // let's output for now just the light color
    // v2f_to_light = vec3(1);
    // out_color = vec4(v2f_to_light, 1) * vec4(light_color,1);
    float brightness = dot(
        v2f_to_light_ws,
        v2f_normal_ws
    );
    brightness = max(brightness, 0.0);
    // vec3 diffuse = brightness * vec3(1);// light_color
    vec3 diffuse = brightness * _light_color;// light_color
    out_color = vec4(diffuse * vec3(1, 1, 1),1);//diffuse * base color

    // what if we get the fragment position here
    // and we calculate the ray towards the light also here
    // in the fragment.
    // right now, the vector representing the incomming ray
    // was caculated per vertex and then interpolated for each fragment
    // for directional lighting, all these ray (direcitons) were
    // the same independently of the vertex position
}

