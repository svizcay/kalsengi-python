#version 330

in vec3 v2f_normal;

out vec4 out_color;

void main()
{
    out_color = vec4(v2f_normal, 1);
}

