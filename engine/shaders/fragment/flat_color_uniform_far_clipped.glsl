#version 330

// in vec3 v2f_color;
// in vec2 v2f_uv;

out vec4 out_color;

uniform vec3 color;
uniform float clip_distance = 75f;
// uniform sampler2D texture0;
// uniform sampler2D texture1;

void main()
{
    if (gl_FragCoord.z/gl_FragCoord.w > clip_distance) discard;
    out_color = vec4(color, 1);
}
