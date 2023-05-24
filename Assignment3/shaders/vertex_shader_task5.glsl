#version 430 core

// Define inputs, outputs and uniform variables
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
out vec4 fColor;
uniform vec4 ambientProduct, diffuseProduct, specularProduct;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 modelMatrix;
// uniform mat4 mvp;
uniform vec4 lightPosition; // in view space: viewMat * lpos;
uniform float shininess;

void main() {
    // Transform input coordinates and vectors
    vec3 pos = (modelViewMatrix * vec4(vertexPosition, 1.0)).xyz;
    vec3 light = lightPosition.xyz; // Light position already in view coordinate frame
    vec3 L = normalize(light - pos); // Light direction
    vec3 E = normalize(-pos); // Eye is at origin -> opposite direction of vertex position
    vec3 H = normalize(L + E); // Halfway vector
    vec3 N = normalize((modelViewMatrix * vec4(vertexNormal, 1.0)).xyz);
    // Compute terms in the illumination equation
    vec4 ambient = ambientProduct;
    float Kd = max(dot(L, N), 0.0);
    vec4 diffuse = Kd * diffuseProduct;
    vec4 specular = vec4(0.0, 0.0, 0.0, 1.0);
    if (Kd > 0.0) {
        float Ks = pow(max(dot(N, H), 0.0), float(shininess));
        specular = Ks * specularProduct;
    }
    // Store results in output variables
    fColor = ambient + diffuse + specular;
    fColor.a = 1.0;
    gl_Position = projectionMatrix * modelViewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
}
