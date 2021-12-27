#version 330

in vec2 v2f_uv;

out vec4 out_color;

void main()
{
    out_color = vec4(v2f_uv, 0, 1);
}

