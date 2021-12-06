#version 330

in vec2 v2f_uv;

out vec4 out_color;

// maybe we should follow as rule to
// initialize all colors to white by default
uniform vec3 color = vec3(1.0, 1.0, 1.0);
uniform sampler2D texture0;
// uniform sampler2D texture1;

void main()
{
    out_color = texture(texture0, v2f_uv) * vec4(color, 1);
}
