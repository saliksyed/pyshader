# pyshader

##A library for experimenting with OpenGL shaders



NOTES: 
* You must have ffmpeg installed for this to work.
* Not tested on Windows or Linux.
* The library is aimed primarily at 2D or computational shaders
* You MUST use unique names for textures and videos ... internally
  videos are stored using texture names so you can't have 
  both a texture and a video named 'foobar' for example.

USAGE:

You just need to import and extend Renderer from pyshader and add a `draw` method
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