from pyshader import Renderer
from example import Example


# Renders the example visualization in a GLUT window
if __name__ == '__main__':
    viz = Example(Renderer.RES720P)
    viz.run()