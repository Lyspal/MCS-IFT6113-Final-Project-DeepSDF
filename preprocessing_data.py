# author: Sylvain Laporte
# program: deepSDF_single_shape.py
# date: 2020-12-08
# object: Functions to preprocess data for DeepSDF.

import json
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

def dump_samples(points, sdfs, output_file):
    """Save samples to a JSON file.

    Args:
        points (np.ndarray): sample spatial points
        sdfs (np.ndarray): respective SDF values
        output_file (string): path to the output file
    """
    data = {
	    "points": points.tolist(),
	    "sdfs": sdfs.tolist()
    }

    with open(output_file, "w+") as f:
	    json.dump(data, f)

def main(input_file, output_file, nb_samples):
    """Run data preprocessing from command line"""
    import pyrender

    # Load the mesh
    mesh = trimesh.load(input_file)

    # Normalize mesh to a unit sphere
    mesh = normalize_to_unit_sphere(mesh)

    # Sample spatial points
    points, sdfs = sample_points(mesh, nb_samples=nb_samples)

    print("size")

    dump_samples(points, sdfs, output_file)

    mesh_to_render = pyrender.Mesh.from_trimesh(mesh)
    colors = np.zeros(points.shape)
    colors[sdfs < 0, 2] = 1
    colors[sdfs > 0, 0] = 1
    point_cloud = pyrender.Mesh.from_points(points, colors=colors)
    scene = pyrender.Scene()
    scene.add(mesh_to_render)
    scene.add(point_cloud)
    pyrender.Viewer(scene, use_raymond_lighting=True, point_size=2)

if __name__ == "__main__":
    import argparse

    # Setup command line arguments
    parser = argparse.ArgumentParser(description="Sample spatial points from mesh")
    parser.add_argument("--input", "-i", default="input-meshes/cube.obj",
        help="path to input mesh")
    parser.add_argument("--samples", "-s", default="500000",
        help="path to input mesh")
    args = parser.parse_args()

    input_file = args.input
    input_file_name = input_file.split(".")[0].split("/")[-1]
    output_file = f"dataset/{input_file_name}-samples.json"
    nb_samples = int(args.samples)

    # Run sampling
    main(input_file, output_file, nb_samples)
