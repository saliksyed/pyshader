from pyshader import Renderer
from example import Example


# Render 75 frames of the example visualization into an mp4 file
if __name__ == '__main__':
    viz = Example(Renderer.RES4K)
    viz.render_frames('video.mp4', 75)