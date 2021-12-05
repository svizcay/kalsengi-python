#version 330

// in vec3 v2f_color;
// in vec2 v2f_uv;

out vec4 out_color;

uniform float time;
// uniform sampler2D texture0;
// uniform sampler2D texture1;

void main()
{
    float red_ch = sin(time) / 2f + 0.5f;
    out_color = vec4(red_ch, 0, 0, 1);
}

