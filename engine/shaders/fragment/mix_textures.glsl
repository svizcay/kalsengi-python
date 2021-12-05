#version 330

in vec2 v2f_uv;

out vec4 out_color;

// uniform vec3 color;
uniform sampler2D texture0;
uniform sampler2D texture1;

void main()
{
    vec4 color_a = texture(texture0, v2f_uv);
    vec4 color_b = texture(texture1, v2f_uv);
    out_color = mix(color_a, color_b, 0.5);
    out_color.a = 1f;
}

