# MCS-IFT6113-Final-Project-DeepSDF

Final project on DeepSDF for the course IFT6113 - Modélisation géométrique et analyse de formes.

Author: Sylvain Laporte  

Due date: December 8th, 2020
Presentation date: December 8th, 2020, 11h10

## About this project

This project implements the paper "DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation", arXiv:1901.05103 [cs.CV].

The project is divided in three parts:

### `preprocessing_data.py`

A script to preprocess the data from an input mesh.

To run the script, use the following command:

```bash
python preprocessing_data.py -i input-meshes/cube.obj -s 250000
```

with the following options:

- `--input`, `-i`: the path to the input mesh file
- `--samples`, `-s`: the number of spatial sample points to return

### `deepSDF_single_shape_colab.ipynb`

A Jupyter nodebook containg the script to build and train the single-shape DeepSDF on Google Colab.

The dataset, generated locally, needs to be downloaded to the virtual Colab machine.

The notebook saves the trained model, which can then be downloaded and run locally for inference.

### `reconstruct_mesh_from_model.py`

A script to generate a mesh from a trained DeepSDF network.

```bash
python reconstruct_mesh_from_model.py -n trained-models/cube-model-5.pt
```

with the following options:

- `--net`, `-n`: the path to the trained network

## Content

This repository contains the following directories and files:

- `input-meshes/`: input meshes.
- `trained-models/`: trained DeepSDF networks.
- `screenshots/`: screenshots of results and bugs.
- `third_party/`: contains code from `mesh-to-sdf` project for data preprocessing only. See the *Credits* section below.
- `pyglet/`: provided only for the third-party code.
- `deepSDF_model.py`: the DeepSDF model definition for local use.
- `deepSDF_single_shape_colab.ipynb`: a Jupyter notebook for building and training DeepSDF networks on Google Colab.
- `preprocessing_data.py`: a script to generate a dataset from a mesh for the network.
- `reconstruct_mesh_from_model.py`: a script to generate a mesh from a trained network.
- `ift6113-final-project-pres.pdf`: the slides used during the presentation on December, 8th, 2020.

## Requirements

The following libraries where used:

- `numpy`: for math operations.
- `pytorch`: for neural network building and training.
- `trimesh`: for loading triangle meshes.
- `skimage`: for marching cubes algorithm.
- `json`: for handling of JSON files.

## Credits

The paper implemented for this project:

@InProceedings{Park_2019_CVPR,
author = {Park, Jeong Joon and Florence, Peter and Straub, Julian and Newcombe, Richard and Lovegrove, Steven},
title = {DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation},
booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
month = {June},
year = {2019}
}

The PyTorch code structure used in this project is adapted from the tutorial "PyTorch: Zero to GANs" by Aakash N.S. for freeCodeCamp.org. The tutorial is available at <https://jovian.ai/aakashns/01-pytorch-basics>.

We only used the data preprocessing classes and functions from the "mesh-to-sdf" DeepSDF implementation by marian42. The code we used is available in the `third-party/` directory. The original code is available at <https://github.com/marian42/mesh_to_sdf>.
