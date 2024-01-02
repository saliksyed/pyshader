pyshader : OpenGL shaders made easy
====================

### Features
* Quickly build shader pipelines: shader 1-> shader2 -> shader3
* Easily import video and images into shaders as textures
* Write shader output to MPEG video, EXR (floating point images) or a variety of other formats (JPEG, PNG)
* Preview shader output using GLUT
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

        # render to screen
        (self.shader('lights')
                .use()
                .tick(self.tick)
                .draw()) # <- draw to screen or video frame

        # render to texture
        (self.shader('lights')
                .use()
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


### Installing on Mac OSX:
You can use Homebrew (https://brew.sh/) to install the required packages, Python dependencies will automatically be installed by the setup script.
```
brew install portaudio openexr libjpeg ffmpeg
git clone git@github.com:saliksyed/pyshader.git
sudo python setup.py install
```
### Installing on Linux: 
You will need to install a few required packages using apt-get before running the setup script (instructions for Ubuntu). Python dependencies will automatically be installed by the setup script.
```
sudo apt-get install python-dev libasound-dev python-pyaudio openexr libopenexr-dev zlib1g-dev libjpeg-dev freeglut3 freeglut3-dev ffmpeg
git clone git@github.com:saliksyed/pyshader.git
sudo python setup.py install
```


### Dependencies
* PyOpenGL(https://github.com/mcfletch/pyopengl)
* Pillow(https://github.com/python-pillow/Pillow)
* numpy(https://github.com/numpy/numpy)
* OpenEXR(http://www.excamera.com/sphinx/articles-openexr.html)
* PyAudio (https://people.csail.mit.edu/hubert/pyaudio/)

### Notes
The library is a work in progress and is aimed primarily at 2D or computational shaders, 
eventually I want to make this plug-and-play compatible with ShaderToy shaders but some work
is needed to get the different features (audio).

* You must have ffmpeg installed for video output to work.
* Not tested on Windows

Inspired by shadertoy(http://www.shadertoy.com) and igloojs(https://github.com/skeeto/igloojs)

Licensed under GPL 3.0(https://www.gnu.org/licenses/gpl-3.0.en.html)
