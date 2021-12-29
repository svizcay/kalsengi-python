#version 330

// by specifying layout, we don't need to query for location (but we need to know this order)
layout(location=0) in vec3 pos;
layout(location=1) in vec2 uv;
layout(location=2) in vec3 normal;
// layout(location=3) in vec3 color;

uniform mat4 mvp;
// out vec3 v2f_color;

// NOTE:
// we should not pass the normal like that to the fragment shader
// just to color a fragment with that 'color'.
// we should use a vertex shader that writes to some
// v2f_color and write there the normal
out vec3 v2f_normal;

void main()
{
    // gl_Position = rot * vec4(pos, 1);
    gl_Position = mvp * vec4(pos, 1);
    // v2f_color = color;

    // we are passing the unmodified normal to the fragment shader
    // (without using the model matrix)
    // just because we are going to "draw" using that raw color
    v2f_normal = normal;
}

