#version 330

// by specifying layout, we don't need to query for location (but we need to know this order)
layout(location=0) in vec3 pos;
layout(location=1) in vec2 uv;
// layout(location=3) in vec3 color;

uniform mat4 mvp;
// out vec3 v2f_color;
out vec2 v2f_uv;

void main()
{
    // gl_Position = rot * vec4(pos, 1);
    gl_Position = mvp * vec4(pos, 1);
    // v2f_color = color;
    v2f_uv = uv;
}

