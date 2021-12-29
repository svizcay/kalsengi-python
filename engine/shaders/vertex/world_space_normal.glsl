#version 330

// by specifying layout, we don't need to query for location (but we need to know this order)
layout(location=0) in vec3 pos;
// layout(location=1) in vec2 uv;
layout(location=2) in vec3 normal;
// layout(location=3) in vec3 color;

uniform mat4 mvp;
uniform mat4 model;
out vec3 v2f_color;
// out vec2 v2f_uv;

void main()
{
    // gl_Position = rot * vec4(pos, 1);
    gl_Position = mvp * vec4(pos, 1);
    vec3 transformed_normal = (model * vec4(normal, 0)).xyz;

    // NOTE: this only work when we have uniform scaling!
    transformed_normal = normalize(transformed_normal);

    v2f_color = transformed_normal;
    // v2f_uv = uv;
}

