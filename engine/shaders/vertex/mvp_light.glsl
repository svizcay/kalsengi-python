#version 330

// by specifying layout, we don't need to query for location (but we need to know this order)
layout(location=0) in vec3 pos;
// layout(location=1) in vec2 uv;
layout(location=2) in vec3 normal;
// layout(location=3) in vec3 color;

uniform mat4 mvp;
uniform mat4 model;
uniform vec4 light_pos;

// out vec3 v2f_color;
// out vec2 v2f_uv;

// a light shader needs to forward the direction to the light source
// and the normal of the vertex
out vec3 v2f_to_light_ws;   // ws vector representing direction to light
out vec3 v2f_normal_ws;    // ws normal

void main()
{
    // gl_Position = rot * vec4(pos, 1);
    gl_Position = mvp * vec4(pos, 1);

    vec3 transformed_normal = (model * vec4(normal, 0)).xyz;
    v2f_normal_ws = normalize(transformed_normal);

    // for a directional light (light_pos.w = 0)
    // all vertices will have the same to_light direction
    // encoded in light_pos when light_pos.w = 0
    // direction light pos encoded the direction of
    // the ray from the light source,
    // therefore, the opposite direction is the
    // from the surface to the light source
    v2f_to_light_ws = -light_pos.xyz;

    // for a point light (light_pos.w = 1)
    // direction to light is light.pos - pos_ws
    // v2f_to_light = light_pos.xyz - pos;

    // v2f_color = color;
    // v2f_uv = uv;

    // we need to trasnform the normal to a world space vector
    // and obtain the world space vector of the vector pointing to the light source
    // therefore, we need to get the model matrix
    // for now, let's just forward the direction in local space
    // light_pos.w is the flag for directional or point light
}
