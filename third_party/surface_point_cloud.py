# author: marian42
# program: surface_point_cloud.py
# date: 
# object: The following code is taken and slightly adapted from the "mesh-to-sdf"
# DeepSDF implementation by marian42 for the purpose of testing only. This solely
# contains classes and functions associated with data preprocessing. The original
# code is available at https://github.com/marian42/mesh_to_sdf

import math
import numpy as np
from sklearn.neighbors import KDTree
import trimesh
import pyrender
import third_party.scan as scan
import third_party.utils as utils

class BadMeshException(Exception):
    pass

class SurfacePointCloud:
    def __init__(self, mesh, points, normals=None, scans=None):
        self.mesh = mesh
        self.points = points
        self.normals = normals
        self.scans = scans

        self.kd_tree = KDTree(points)

    def get_random_surface_points(self, count, use_scans=True):
        if use_scans:
            indices = np.random.choice(self.points.shape[0], count)
            return self.points[indices, :]
        else:
            return self.mesh.sample(count)

    def get_sdf(self, query_points, use_depth_buffer=False, sample_count=11):
        if use_depth_buffer:
            distances, _ = self.kd_tree.query(query_points)
            distances = distances.astype(np.float32).reshape(-1) * -1
            distances[self.is_outside(query_points)] *= -1
            return distances
        else:
            distances, indices = self.kd_tree.query(query_points, k=sample_count)
            distances = distances.astype(np.float32)

            closest_points = self.points[indices]
            direction_to_surface = query_points[:, np.newaxis, :] - closest_points
            inside = np.einsum('ijk,ijk->ij', direction_to_surface, self.normals[indices]) < 0
            inside = np.sum(inside, axis=1) > sample_count * 0.5
            distances = distances[:, 0]
            distances[inside] *= -1
            return distances

    def get_sdf_in_batches(self, query_points, use_depth_buffer=False, sample_count=11, batch_size=1000000):
        if query_points.shape[0] <= batch_size:
            return self.get_sdf(query_points, use_depth_buffer=use_depth_buffer, sample_count=sample_count)
        
        result = np.zeros(query_points.shape[0])
        for i in range(int(math.ceil(query_points.shape[0] / batch_size))):
            start = int(i * batch_size)
            end = int(min(result.shape[0], (i + 1) * batch_size))
            result[start:end] = self.get_sdf(query_points[start:end, :], use_depth_buffer=use_depth_buffer, sample_count=sample_count)
        return result

    def get_voxels(self, voxel_resolution, use_depth_buffer=False, sample_count=11, pad=False, check_result=False):
        from third_party.utils import get_raster_points, check_voxels
        
        sdf = self.get_sdf_in_batches(get_raster_points(voxel_resolution), use_depth_buffer, sample_count)
        voxels = sdf.reshape((voxel_resolution, voxel_resolution, voxel_resolution))

        if check_result and not check_voxels(voxels):
            raise BadMeshException()

        if pad:
            voxels = np.pad(voxels, 1, mode='constant', constant_values=1)

        return voxels

    def sample_sdf_near_surface(self, number_of_points=500000, use_scans=True, sign_method='normal', normal_sample_count=11, min_size=0):
        query_points = []
        surface_sample_count = int(number_of_points * 47 / 50) // 2
        surface_points = self.get_random_surface_points(surface_sample_count, use_scans=use_scans)
        query_points.append(surface_points + np.random.normal(scale=0.0025, size=(surface_sample_count, 3)))
        query_points.append(surface_points + np.random.normal(scale=0.00025, size=(surface_sample_count, 3)))
        
        unit_sphere_sample_count = number_of_points - surface_points.shape[0] * 2
        unit_sphere_points = utils.sample_uniform_points_in_unit_sphere(unit_sphere_sample_count)
        query_points.append(unit_sphere_points)
        query_points = np.concatenate(query_points).astype(np.float32)

        if sign_method == 'normal':
            sdf = self.get_sdf_in_batches(query_points, use_depth_buffer=False, sample_count=normal_sample_count)
        elif sign_method == 'depth':
            sdf = self.get_sdf_in_batches(query_points, use_depth_buffer=True)
        else:
            raise ValueError('Unknown sign determination method: {:s}'.format(sign_method))
        
        if min_size > 0:
            model_size = np.count_nonzero(sdf[-unit_sphere_sample_count:] < 0) / unit_sphere_sample_count
            if model_size < min_size:
                raise BadMeshException()

        return query_points, sdf

    def show(self):
        scene = pyrender.Scene()
        scene.add(pyrender.Mesh.from_points(self.points, normals=self.normals))
        pyrender.Viewer(scene, use_raymond_lighting=True, point_size=2)
        
    def is_outside(self, points):
        result = None
        for scan in self.scans:
            if result is None:
                result = scan.is_visible(points)
            else:
                result = np.logical_or(result, scan.is_visible(points))
        return result

def get_surface_point_cloud(mesh, surface_point_method='scan', bounding_radius=None, scan_count=100, scan_resolution=400, sample_point_count=10000000, calculate_normals=True):
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump().sum()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("The mesh parameter must be a trimesh mesh.")

    if bounding_radius is None:
        bounding_radius = np.max(np.linalg.norm(mesh.vertices, axis=1)) * 1.1
        
    if surface_point_method == 'scan':
        return create_from_scans(mesh, bounding_radius=bounding_radius, scan_count=scan_count, scan_resolution=scan_resolution, calculate_normals=calculate_normals)
    # elif surface_point_method == 'sample':
    #     return surface_point_cloud.sample_from_mesh(mesh, sample_point_count=sample_point_count, calculate_normals=calculate_normals)        
    # else:
    #     raise ValueError('Unknown surface point sampling method: {:s}'.format(surface_point_method))

def create_from_scans(mesh, bounding_radius=1, scan_count=100, scan_resolution=400, calculate_normals=True):
    scans = []

    for phi, theta in get_equidistant_camera_angles(scan_count):
        camera_transform = scan.get_camera_transform_looking_at_origin(phi, theta, camera_distance=2 * bounding_radius)
        scans.append(scan.Scan(mesh,
            camera_transform=camera_transform,
            resolution=scan_resolution,
            calculate_normals=calculate_normals,
            fov=1.0472,
            z_near=bounding_radius * 1,
            z_far=bounding_radius * 3
        ))

    return SurfacePointCloud(mesh, 
        points=np.concatenate([scan.points for scan in scans], axis=0),
        normals=np.concatenate([scan.normals for scan in scans], axis=0) if calculate_normals else None,
        scans=scans
    )

def get_equidistant_camera_angles(count):
    increment = math.pi * (3 - math.sqrt(5))
    for i in range(count):
        theta = math.asin(-1 + 2 * i / (count - 1))
        phi = ((i + 1) * increment) % (2 * math.pi)
        yield phi, theta

def sample_sdf_near_surface(self, number_of_points=500000, use_scans=True, sign_method='normal', normal_sample_count=11, min_size=0):
    query_points = []
    surface_sample_count = int(number_of_points * 47 / 50) // 2
    surface_points = self.get_random_surface_points(surface_sample_count, use_scans=use_scans)
    query_points.append(surface_points + np.random.normal(scale=0.0025, size=(surface_sample_count, 3)))
    query_points.append(surface_points + np.random.normal(scale=0.00025, size=(surface_sample_count, 3)))
    
    unit_sphere_sample_count = number_of_points - surface_points.shape[0] * 2
    unit_sphere_points = utils.sample_uniform_points_in_unit_sphere(unit_sphere_sample_count)
    query_points.append(unit_sphere_points)
    query_points = np.concatenate(query_points).astype(np.float32)

    if sign_method == 'normal':
        sdf = self.get_sdf_in_batches(query_points, use_depth_buffer=False, sample_count=normal_sample_count)
    elif sign_method == 'depth':
        sdf = self.get_sdf_in_batches(query_points, use_depth_buffer=True)
    else:
        raise ValueError('Unknown sign determination method: {:s}'.format(sign_method))
    
    if min_size > 0:
        model_size = np.count_nonzero(sdf[-unit_sphere_sample_count:] < 0) / unit_sphere_sample_count
        if model_size < min_size:
            raise BadMeshException()

    return query_points, sdf