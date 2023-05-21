from OpenGL.GL import *

import glm
from utils.glut_window import GlutWindow
from utils.mvp_controller_task5 import MVPController
from OpenGL.GL import shaders
import random
import time
import math

# Define eight vertices
v1 = (-1, -1, +1)
v2 = (+1, -1, +1)
v3 = (+1, +1, +1)
v4 = (-1, +1, +1)
v5 = (-1, +1, -1)
v6 = (-1, -1, -1)
v7 = (+1, -1, -1)
v8 = (+1, +1, -1)

# Define a box using triangles
vertex_buffer_data = [
    # Front face
	*v1, *v2, *v3,
	*v1, *v3, *v4,
	# Back face
	*v5, *v6, *v7,
	*v5, *v7, *v8,
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
	*v6, *v1, *v2,
	*v6, *v2, *v7,
]

# Set random colors for each of the vertices
color_buffer_data = [random.random() for _ in range(len(vertex_buffer_data))]

start_time = time.time()


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
        vertex_shader_string = read_file("shaders/vertex_shader_copy.glsl")
        fragment_shader_string = read_file("shaders/fragment_shader_copy.glsl")
        vertex_shader = shaders.compileShader(vertex_shader_string, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(
            fragment_shader_string, GL_FRAGMENT_SHADER
        )
        self.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)

        # Get location of the MVP matrix
        self.context.mvp_location = glGetUniformLocation(self.shader_program, "mvp")
        # self.context.m_location = glGetUniformLocation(self.shader_program, "M")
        # self.context.v_location = glGetUniformLocation(self.shader_program, "V")
        # Generate buffers for vertices and color data and buffer the data
        self.context.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(vertex_buffer_data) * 4,
            (GLfloat * len(vertex_buffer_data))(*vertex_buffer_data),
            GL_STATIC_DRAW,
        )

        self.context.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.color_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(color_buffer_data) * 4,
            (GLfloat * len(color_buffer_data))(*color_buffer_data),
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
        glBindBuffer(GL_ARRAY_BUFFER, self.context.color_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Draw three boxes next to each other
        body_width = 2
        body_height = 4
        body_depth = 2

        leg_width = 0.5
        leg_height = 2
        leg_depth = 0.5

        upper_leg_angle = math.sin(time.time() - start_time) * 45
        lower_leg_angle = math.sin(time.time() - start_time) * 45

        # Draw the first box (body)
        mvp_stack.append(glm.mat4(1))
        mvp_stack[-1] = glm.translate(mvp_stack[-1], glm.vec3(0, 1, 0))         # move origin to the center bottom of the box
        self.model_matrix = glm.scale(mvp_stack[-1], glm.vec3(body_width, body_height, body_depth))
        self.calc_mvp()
        glUniformMatrix4fv(self.context.mvp_location, 1, GL_FALSE, glm.value_ptr(self.context.mvp))
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        # Draw the second box (upper leg)
        mvp_stack.append(glm.translate(mvp_stack[-1], glm.vec3(0, 0, 0)))      # dont move
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(upper_leg_angle), glm.vec3(0, 0, 1))
        mvp_stack[-1] = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))                     
        self.model_matrix = mvp_stack[-1]
        self.calc_mvp()
        glUniformMatrix4fv(self.context.mvp_location, 1, GL_FALSE, glm.value_ptr(self.context.mvp))
        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        # Draw the third box (lower leg)
        # Move leg to the bottom of the upper leg
        mvp_stack.append(glm.translate(mvp_stack[-1], glm.vec3(0, -leg_height, 0)))
        # Rotate leg around the origin
        mvp_stack[-1] = glm.rotate(mvp_stack[-1], glm.radians(lower_leg_angle), glm.vec3(0, 0, 1))
        # mvp_stack[-1] = glm.scale(mvp_stack[-1], glm.vec3(leg_width, leg_height, leg_depth))
        self.model_matrix = mvp_stack[-1]
        self.calc_mvp()
        glUniformMatrix4fv(self.context.mvp_location, 1, GL_FALSE, glm.value_ptr(self.context.mvp))
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
