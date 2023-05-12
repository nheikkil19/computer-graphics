from OpenGL.GL import *

import glm
from utils.glut_window import GlutWindow
from utils.mvp_controller import MVPController
import random

vertex_buffer_data = [
    -1, +0, -1, +1, +0, -1, -1, +0, +1,  # Base 0
    +1, +0, -1, +1, +0, +1, -1, +0, +1,  # Base 1
    -1, +0, -1, +0, +1, +0, +1, +0, -1,  # Side 0
    +1, +0, -1, +0, +1, +0, +1, +0, +1,  # Side 1
    +1, +0, +1, +0, +1, +0, -1, +0, +1,  # Side 2
    -1, +0, +1, +0, +1, +0, -1, +0, -1,  # Side 3
]

color_buffer_data = [random.random() for _ in range(len(vertex_buffer_data))]


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
        # Get location of the MVP matrix
        self.context.mvp_location = glGetUniformLocation(
            self.shader_program, "MVP")        # Generate buffers for vertices and color data and buffer the data
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
        glUniformMatrix4fv(
            self.context.mvp_location, 1, GL_FALSE, glm.value_ptr(
                self.context.mvp)
        )

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.color_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_TRIANGLES, 0, len(vertex_buffer_data))

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glUseProgram(0)


if __name__ == "__main__":
	win = Win()
	win.controller = MVPController(win.update_if, width=win.width, height=win.height)
	win.init_opengl()
	win.init_context()
	win.run()
