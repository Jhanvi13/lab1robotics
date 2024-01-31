# -*- coding: utf-8 -*-
"""Module-1-Lab-space-shuttle-class.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pLjBibao3Byncj2NJqWSJPngM5AhXY1_

Time-series forecasting and prediction on tabular data using PyTorch. Supports Jetson Nano, TX1/TX2, AGX Xavier, and Xavier NX.

# Space Shuttle Classification

This classification [dataset](https://archive.ics.uci.edu/ml/datasets/Statlog+%28Shuttle%29) from the UCI Machine Learning Repository contains the values from 9 sensors and has 7 state classes:
"""

class distribution:
  [0] 'Rad Flow' - 45586 samples
  [1] 'Fpv Close' - 50 samples
  [2] 'Fpv Open' - 171 sampless
  [3] 'High' - 8903 samples
  [4] 'Bypass' - 3267 samples
  [5] 'Bpv Close' - 10 samples
  [6] 'Bpv Open' - 13 samples

total:  58000 samples

"""The goal is to predict the state of the system from the current sensor data. Given the unbalanced distribution of data between the classes, this example is akin to anomoly detection.

# Getting Started

## Software Requirement

- PyTorch
- CUDA

## Starting the container
"""

!git clone https://github.com/dusty-nv/pytorch-timeseries

cd pytorch-timeseries

!docker/run.sh

cd pytorch-timeseries

"""# Running the training script

Train.py allows you to:

- pick any number of inputs / outputs
- support both regression and classification
- easily change the model
- automatic plotting
"""

!python3 train.py --data data/shuttle.csv --inputs 0,1,2,3,4,5,6,7,8 --outputs class --classification --epochs 100

"""# Notes

* We provide the model files for GRU RNN model and linear model in this repo.Please check the model files in ../models/

# What's next?

* For the lab exercise, we encourage you to source
your own data, prepare it, and then make a model with train.py.   

* Datasets typically require a little preparation, you can see those
scripts here:

  https://github.com/dusty-nv/pytorch-timeseries/tree/main/scripts
"""
