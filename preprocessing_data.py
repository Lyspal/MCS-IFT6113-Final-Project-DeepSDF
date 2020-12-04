# author: Sylvain Laporte
# program: deepSDF_single_shape.py
# date: 2020-12-08
# object: Functions to preprocess data for DeepSDF.

import trimesh
import numpy as np
import third_party.surface_point_cloud as spc

def normalize_to_unit_sphere(mesh):
    """Normalize a mesh to a unit sphere.

    Args:
        mesh (trimesh.Trimesh): the nesh to normalize

    Returns:
        trimesh.Trimesh: the normalized mesh
    """
    # Move the origin to the center of the mesh bounding box
    vertices = mesh.vertices - mesh.bounding_box.centroid

    # Normalize by dividing by the largest magnitude
    magnitudes = np.linalg.norm(vertices, axis=1)
    vertices /= np.max(magnitudes) * (1./1.03)  # add margin to unit sphere

    return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)

def sample_points(mesh, nb_samples):
    """Samples spatial points and their SDF values for a mesh to train.

    Args:
        mesh (trimesh.Trimesh): the mesh
        nb_samples (number): the number of samples to take

    Returns:
        np.ndarray: the sampled points
        np.ndarray: the corresponding SDF value
    """
    # Set up equally spaced virtual cameras around the mesh to get a point cloud
    # of the surface
    surface_point_cloud = get_mesh_point_cloud(mesh)

    # Densely sample surface points P_s
    return surface_point_cloud.sample_sdf_near_surface(nb_samples)

def get_mesh_point_cloud(mesh):
    """Constructs a point cloud for a mesh using virtual cameras.

    Args:
        mesh (trimesh.Trimesh): the mesh

    Returns:
        SurfacePointCloud: the resulting point cloud
    """
    scan_count = 100
    return spc.get_surface_point_cloud(mesh, bounding_radius=1, scan_count=scan_count)
