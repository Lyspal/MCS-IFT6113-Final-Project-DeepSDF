# author: marian42
# program: pyrender_wrapper.py
# date: 
# object: The following code is taken and slightly adapted from the "mesh-to-sdf"
# DeepSDF implementation by marian42. This solely contains classes and functions
# associated with data preprocessing. The original code is available at
# https://github.com/marian42/mesh_to_sdf

import os
import pyrender

def render_normal_and_depth_buffers(mesh, camera, camera_transform, resolution):
    global suppress_multisampling
    suppress_multisampling = True
    scene = pyrender.Scene()
    scene.add(pyrender.Mesh.from_trimesh(mesh, smooth = False))
    scene.add(camera, pose=camera_transform)

    renderer = pyrender.OffscreenRenderer(resolution, resolution)
    renderer._renderer._program_cache = CustomShaderCache()

    color, depth = renderer.render(scene, flags=pyrender.RenderFlags.SKIP_CULL_FACES)
    suppress_multisampling = False
    return color, depth

class CustomShaderCache():
    def __init__(self):
        self.program = None

    def get_program(self, vertex_shader, fragment_shader, geometry_shader=None, defines=None):
        if self.program is None:
            shaders_directory = os.path.join(os.path.dirname(__file__), 'shaders')
            self.program = pyrender.shader_program.ShaderProgram(os.path.join(shaders_directory, 'mesh.vert'), os.path.join(shaders_directory, 'mesh.frag'), defines=defines)
        return self.program