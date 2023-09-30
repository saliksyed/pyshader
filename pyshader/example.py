from pyshader import Renderer

"""
    This example shows a multi-pass shader that renders a light 
    shining through heat ... the heat blurs the light creating a cool effect.

    A video is used to read in the "heat" data
    The light is rendered to a texture
    The light+heat texture is then sent to another shader for final rendering
"""
class Example(Renderer):
    def __init__(self, resolution):
        Renderer.__init__(self, resolution)
        self.tick = 0
        # Load a fragment shader for rendering the light
        self.shader('lights','shaders/horizontal_light.frag')

        # Load a fragment shader for rendering a heat blur
        self.shader('heat_blur','shaders/heat_blur.frag')
        
        # Load a video for the heat data (just simulated clouds)
        self.video('heat_texture', 'data/video.mp4')
        
        # setup an output texture for the light
        self.texture('light_rendered')
    
    def draw(self):
        # Extend the draw method with your rendering logic!
        self.tick += 1.0 / 30.0
        # step to the next frame of the video
        self.video('heat_texture').next_frame()

        # We first render the light using horizontal_light.frag into a texture
        (self.shader('lights')
                .use()
                .tick(self.tick)
                .drawTo('light_rendered'))

        # Next we pass the rendered light into the heat blur shader, along with the video texture
        # representing the heat:
        (self.shader('heat_blur')
                .use()
                .input('heat_texture', withName='iChannel0')
                .input('light_rendered', withName='iChannel1')
                .tick(self.tick)
                .draw())