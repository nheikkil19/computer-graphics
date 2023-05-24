#version 430 core

in vec4 fColor;		// Interpolated between vertex values for each fragment
out vec4 gl_FragColor;
void main(void)
{
    gl_FragColor = fColor;
}
