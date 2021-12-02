#version 330

in vec3 v2f_color;
in vec2 v2f_uv;

out vec4 out_color;

// uniform vec3 color;
uniform sampler2D texture0;
// uniform sampler2D texture1;

void main()
{
    out_color = texture(texture0, v2f_uv) * vec4(v2f_color, 1);
}

