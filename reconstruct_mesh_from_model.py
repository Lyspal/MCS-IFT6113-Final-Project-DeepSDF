# author: Sylvain Laporte
# program: reconstruct_mesh_from_model.py
# date: 2020-12-08
# object: Reconstructs a mesh from the trained DeepSDF model.

import torch
import deepSDF_model
import trimesh
from skimage import measure

# Load the model

PATH = "trained_models/horse-1-model-10.pt"

input_size = 3
hidden_size = 512
out_size = 1

model = deepSDF_model.DeepSDF_single(input_size, hidden_size=hidden_size, out_size=out_size)
model.load_state_dict(torch.load(PATH, map_location=torch.device('cpu')))
model.eval()

# Generate voxels

RESOLUTION = 100
voxels = torch.zeros(RESOLUTION, RESOLUTION, RESOLUTION)

intervals = [x / RESOLUTION for x in range(RESOLUTION)]
points = [[x, y, z] for x in intervals for y in intervals for z in intervals]
points = torch.tensor(points)

sdfs = model(points)

voxels = sdfs.view(RESOLUTION, RESOLUTION, RESOLUTION).detach().numpy()

# Generate mesh using marching cubes

vertices, faces, normals, _ = measure.marching_cubes(voxels, 0)
mesh = trimesh.Trimesh(vertices, faces, normals)
trimesh.repair.fix_normals(mesh)

# Show the resulting mesh

mesh.show()