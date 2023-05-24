from OpenGL.GL import *

import glm
from utils.glut_window import GlutWindow
from utils.mvp_controller_task5 import MVPController
from OpenGL.GL import shaders
import time
import math

# Define eight vertices
v1 = (-0.5, -1, +0.5)
v2 = (+0.5, -1, +0.5)
v3 = (+0.5, +0, +0.5)
v4 = (-0.5, +0, +0.5)
v5 = (-0.5, +0, -0.5)
v6 = (-0.5, -1, -0.5)
v7 = (+0.5, -1, -0.5)
v8 = (+0.5, +0, -0.5)

# Define a box using triangles
vertex_buffer_data = [
    # Front face
	*v1, *v2, *v3,
	*v1, *v3, *v4,
	# Back face
	*v6, *v5, *v7,
	*v7, *v5, *v8,
	# Left face
	*v6, *v1, *v4,
	*v6, *v4, *v5,
	# Right face
	*v2, *v7, *v8,
	*v2, *v8, *v3,
	# Top face
	*v4, *v3, *v8,
	*v4, *v8, *v5,
	# Bottom face
	*v2, *v1, *v6,
	*v7, *v2, *v6,
]
# Calculate vertex normals
vertex_normal_data = []
for i in range(0, len(vertex_buffer_data), 9):
    v1 = glm.vec3([vertex_buffer_data[i+j] for j in range(3)])
    v2 = glm.vec3([vertex_buffer_data[i+j+3] for j in range(3)])
    v3 = glm.vec3([vertex_buffer_data[i+j+6] for j in range(3)])
    vertex_normal_data += glm.cross(v2 - v1, v3 - v1).to_list() * 3

start_time = time.time()

# Body dimensions
body_width = 3
body_height = 4
body_depth = 1
# Leg dimensions
leg_width = 1
leg_height = 2
leg_depth = 1

# light parameters
light_ambient = glm.vec4(0.1, 0.1, 0.1, 1.0)
light_diffuse = glm.vec4(0.2, 0.2, 0.2, 1.0)
light_specular = glm.vec4(0.3, 0.3, 0.3, 1.0)
shininess = 20.0

# Body material parameters and products
body_material_ambient = glm.vec4(0.0, 1.0, 1.0, 1.0)
body_ambient_product = light_ambient * body_material_ambient
body_material_diffuse = glm.vec4(1.0, 0.0, 1.0, 1.0)
body_diffuse_product = light_diffuse * body_material_diffuse
body_material_specular = glm.vec4(1.0, 1.0, 0.0, 1.0)
body_specular_product = light_specular * body_material_specular

# Leg material parameters and products
leg_material_ambient = glm.vec4(1.0, 0.0, 1.0, 1.0)
leg_ambient_product = light_ambient * leg_material_ambient
leg_material_diffuse = glm.vec4(1.0, 1.0, 0.0, 1.0)
leg_diffuse_product = light_diffuse * leg_material_diffuse
leg_material_specular = glm.vec4(0.0, 1.0, 1.0, 1.0)
leg_specular_product = light_specular * leg_material_specular



def read_file(file_path: str) -> str:
    """Reads a text file given a path and returns it as a string."""
    with open(file_path, mode="r") as f:
        contents = f.readlines()
    return contents


class GLContext:
    """Used for storing context data in the main window."""
    pass


class Win(GlutWindow):
    """The main application. Inherits from glut_window.py."""
    def __init__(self, width: int = 800, height: int = 480):
        super().__init__(width, height)
        self.context = GLContext()
        self.model_matrix = glm.mat4(1.0)

    def init_context(self):
        # Read shader files and compile them
        vertex_shader_string = read_file("shaders/vertex_shader_task5.glsl")
        fragment_shader_string = read_file("shaders/fragment_shader_task5.glsl")
        vertex_shader = shaders.compileShader(vertex_shader_string, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(
            fragment_shader_string, GL_FRAGMENT_SHADER
        )
        self.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)

        # Get location of the MVP matrix
        self.ambient_product_location = glGetUniformLocation(self.shader_program, "ambientProduct")
        self.diffuse_product_location = glGetUniformLocation(self.shader_program, "diffuseProduct")
        self.specular_product_location = glGetUniformLocation(self.shader_program, "specularProduct")
        self.model_view_matrix_location = glGetUniformLocation(self.shader_program, "modelViewMatrix")
        self.projection_matrix_location = glGetUniformLocation(self.shader_program, "projectionMatrix")
        self.model_matrix_location = glGetUniformLocation(self.shader_program, "modelMatrix")
        self.light_position_location = glGetUniformLocation(self.shader_program, "lightPosition")
        self.shininess_location = glGetUniformLocation(self.shader_program, "shininess")

        # Generate buffer for vertices and buffer the data
        self.context.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(vertex_buffer_data) * 4,
            (GLfloat * len(vertex_buffer_data))(*vertex_buffer_data),
            GL_STATIC_DRAW,
        )

        # Define normal buffer
        self.context.normal_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.normal_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(vertex_normal_data) * 4,
            (GLfloat * len(vertex_normal_data))(*vertex_normal_data),
            GL_STATIC_DRAW,
        )

    def calc_mvp(self):
        self.calc_model()
        self.context.mvp = self.controller.calc_mvp(self.model_matrix)

    def resize(self, width, height):
        glViewport(0, 0, width, height)
        self.calc_mvp()

    def calc_model(self):
        pass


    def draw(self):
        """
        The main drawing function. Is called whenever an update occurs.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.calc_mvp()
        glUseProgram(self.shader_program)
        mvp_stack = []

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.normal_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Define light position
        light_position = glm.vec4(20.0, 20.0, 20.0, 1.0)
        light_position = self.controller.view_matrix * light_position

        # Calculate leg angles
        t = (time.time() - start_time) * 4
        left_upper_leg_angle = math.sin(t) * 45
        left_lower_leg_angle = max(-math.sin(t*2) * 45 * (1 if math.cos(t) < 0 else 0), 0)
        right_upper_leg_angle = math.sin(t + math.pi) * 45
        right_lower_leg_angle = max(-math.sin((t + math.pi)*2) * 45 * (1 if math.cos(t + math.pi) < 0 else 0), 0)

        # Draw the first box (body)
        mvp_stack.append(glm.mat4(1))
        # Scale but don't change the original box
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(body_width, body_height, body_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.projection_matrix))
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        # glUniformMatrix4fv(self.mvp_matrix_location, 1, GL_FALSE, glm.value_ptr(self.context.mvp))
        glUniform4f(self.ambient_product_location, body_ambient_product.x, body_ambient_product.y, body_ambient_product.z, body_ambient_product.w)
        glUniform4f(self.diffuse_product_location, body_diffuse_product.x, body_diffuse_product.y, body_diffuse_product.z, body_diffuse_product.w)
        glUniform4f(self.specular_product_location, body_specular_product.x, body_specular_product.y, body_specular_product.z, body_specular_product.w)
        glUniform4f(self.light_position_location, light_position.x, light_position.y, light_position.z, light_position.w)
        glUniform1f(self.shininess_location, shininess)
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))


        # Draw the left upper leg
        mvp_stack.append(mvp_stack[-1])
        mvp_stack[-1] = glm.translate(mvp_stack[-1], glm.vec3(-(body_width-leg_width)/2, -body_height, 0))
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(left_upper_leg_angle), glm.vec3(1, 0, 0))
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.projection_matrix))
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        glUniform4f(self.ambient_product_location, leg_ambient_product.x, leg_ambient_product.y, leg_ambient_product.z, leg_ambient_product.w)
        glUniform4f(self.diffuse_product_location, leg_diffuse_product.x, leg_diffuse_product.y, leg_diffuse_product.z, leg_diffuse_product.w)
        glUniform4f(self.specular_product_location, leg_specular_product.x, leg_specular_product.y, leg_specular_product.z, leg_specular_product.w)
        glUniform4f(self.light_position_location, light_position.x, light_position.y, light_position.z, light_position.w)
        glUniform1f(self.shininess_location, shininess)
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        # Draw the left lower leg
        mvp_stack.append(glm.translate(mvp_stack[-1], glm.vec3(0, -leg_height, 0)))
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(left_lower_leg_angle), glm.vec3(1, 0, 0))
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.projection_matrix))
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        glUniform4f(self.ambient_product_location, leg_ambient_product.x, leg_ambient_product.y, leg_ambient_product.z, leg_ambient_product.w)
        glUniform4f(self.diffuse_product_location, leg_diffuse_product.x, leg_diffuse_product.y, leg_diffuse_product.z, leg_diffuse_product.w)
        glUniform4f(self.specular_product_location, leg_specular_product.x, leg_specular_product.y, leg_specular_product.z, leg_specular_product.w)
        glUniform4f(self.light_position_location, light_position.x, light_position.y, light_position.z, light_position.w)
        glUniform1f(self.shininess_location, shininess)
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        # Draw the right upper leg
        mvp_stack.append(mvp_stack[0])
        mvp_stack[-1] = glm.translate(mvp_stack[-1], glm.vec3((body_width-leg_width)/2, -body_height, 0))
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(right_upper_leg_angle), glm.vec3(1, 0, 0))
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.projection_matrix))
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        glUniform4f(self.ambient_product_location, leg_ambient_product.x, leg_ambient_product.y, leg_ambient_product.z, leg_ambient_product.w)
        glUniform4f(self.diffuse_product_location, leg_diffuse_product.x, leg_diffuse_product.y, leg_diffuse_product.z, leg_diffuse_product.w)
        glUniform4f(self.specular_product_location, leg_specular_product.x, leg_specular_product.y, leg_specular_product.z, leg_specular_product.w)
        glUniform4f(self.light_position_location, light_position.x, light_position.y, light_position.z, light_position.w)
        glUniform1f(self.shininess_location, shininess)
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        # Draw the left lower leg
        mvp_stack.append(glm.translate(mvp_stack[-1], glm.vec3(0, -leg_height, 0)))
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(right_lower_leg_angle), glm.vec3(1, 0, 0))
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(self.controller.projection_matrix))
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        glUniform4f(self.ambient_product_location, leg_ambient_product.x, leg_ambient_product.y, leg_ambient_product.z, leg_ambient_product.w)
        glUniform4f(self.diffuse_product_location, leg_diffuse_product.x, leg_diffuse_product.y, leg_diffuse_product.z, leg_diffuse_product.w)
        glUniform4f(self.specular_product_location, leg_specular_product.x, leg_specular_product.y, leg_specular_product.z, leg_specular_product.w)
        glUniform4f(self.light_position_location, light_position.x, light_position.y, light_position.z, light_position.w)
        glUniform1f(self.shininess_location, shininess)
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)

        glUseProgram(0)


if __name__ == "__main__":
    win = Win()
    win.controller = MVPController(win.update_if, width=win.width, height=win.height)
    win.controller.position = glm.vec3(0, 0, 10)
    win.controller.pitch = 0
    win.controller.yaw = 0
    win.controller.calc_view_projection()
    win.init_opengl()
    win.init_context()
    win.run()
