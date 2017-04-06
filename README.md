pyshader : OpenGL shaders made easy
====================

### Features
* Quickly build shader pipelines: shader1->shader2->shader3
* Easily import video and images into shaders as textures
* Write shader output to MPEG video
* Preview shader output using GLUT

The library is a work in progress and is aimed primarily at 2D or computational shaders, 
eventually I want to make this plug-and-play compatible with ShaderToy shaders but some work
is needed to get the different features (audio).

A lot of the structure is inspired by shadertoy (http://www.shadertoy.com) and igloojs (https://github.com/skeeto/igloojs)

### Setup

```
sudo python setup.py install
```

Dependencies:
* PyOpenGL (https://github.com/mcfletch/pyopengl)
* Pillow (PIL) (https://github.com/python-pillow/Pillow)
* numpy (https://github.com/numpy/numpy)

(these will automatically be installed by the setup script)

### Notes
* You must have ffmpeg installed for this to work.
* Not tested on Windows or Linux.
* You MUST use unique names for textures and videos ... internally
  videos are stored using texture names so you can't have 
  both a texture and a video named 'foobar' for example.

### Usage

You just need to import and extend `Renderer` from `pyshader` and add a `draw` method
to your class:

```
from pyshader import Renderer

class Example(Renderer):
    def __init__(self, resolution):
        Renderer.__init__(self, resolution)
        self.tick = 0
        self.shader('lights','shaders/horizontal_light.frag')
    	self.texture('outputTexture')
    def draw(self):
        self.tick += 1.0 / 30.0

        
        (self.shader('lights')
                .tick(self.tick)
                .draw('light_rendered')) # <- draw to screen or video frame

        # render to texture
		(self.shader('lights')
                .tick(self.tick)
                .drawTo('outputTexture')) # <- draw to texture

viz = Example(Renderer.RES720P)
viz.run()
```

Alternatively you can render frames:

```
viz = Example(Renderer.RES4K)
viz.render_frames('video.mp4', 75) # <- render 75 frames to video.mp4
```

You can find a more complicated example in the examples directory