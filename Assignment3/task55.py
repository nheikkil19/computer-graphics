from OpenGL.GL import *

import glm
from utils.glut_window import GlutWindow
from utils.mvp_controller import MVPController
from OpenGL.GL import shaders
import random
import time

# Define eight vertices
v1 = (-1, -2, +1)
v2 = (+1, -2, +1)
v3 = (+1, +2, +1)
v4 = (-1, +2, +1)
v5 = (-1, +2, -1)
v6 = (-1, -2, -1)
v7 = (+1, -2, -1)
v8 = (+1, +2, -1)

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
        self.model_matrix = glm.mat4(1)



    def draw(self):
        """
        The main drawing function. Is called whenever an update occurs.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.calc_mvp()
        glUseProgram(self.shader_program)
        mvp_stack = []


        # Draw the first box
        mvp_stack.append(glm.mat4(1))
        # self.model_matrix = glm.translate(self.model_matrix, glm.vec3(0, 0, 0))
        # self.model_matrix = glm.rotate()
        # self.model_matrix = glm.scale(self.model_matrix, glm.vec3(1, 1, 1))
        self.model_matrix = mvp_stack[-1]
        glUniformMatrix4fv(self.context.mvp_location, 1, GL_FALSE, glm.value_ptr(self.context.mvp))
        # glUniformMatrix4fv(self.context.m_location, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        # glUniformMatrix4fv(self.context.v_location, 1, GL_FALSE, glm.value_ptr(self.controller.view_matrix))
        # light_view = self.controller.view_matrix * (self.model_matrix * self.light_position)
        # glUniform4fv(self.context.light_location, 1, glm.value_ptr(light_view))
        # glUniform3f(self.context.color_location, 1, 1, 0)
        # glUniform1f(self.context.light_bool_location, -1.0)


        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # glEnableVertexAttribArray(1)
        # glBindBuffer(GL_ARRAY_BUFFER, self.context.color_buffer)
        # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        glDisableVertexAttribArray(0)
        # glDisableVertexAttribArray(1)
        glUseProgram(0)


if __name__ == "__main__":
    win = Win()
    win.controller = MVPController(win.update_if, width=win.width, height=win.height)
    win.init_opengl()
    win.init_context()
    win.run()
