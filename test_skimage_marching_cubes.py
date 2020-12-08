from skimage import measure
from skimage.draw import ellipsoid
import trimesh

ellip = ellipsoid(5, 2, 2, levelset=False)

vertices, faces, normals, _ = measure.marching_cubes(ellip, 0)

mesh = trimesh.Trimesh(vertices, faces, normals)

trimesh.repair.fix_normals(mesh)

mesh.show()