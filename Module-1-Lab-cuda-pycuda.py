# -*- coding: utf-8 -*-
"""Module-1-Lab-cuda-pycuda.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BWpNoEg6BLged24Ovnntv0weDAZZP7B4

# **Introduction to CUDA and PyCUDA**

PyCUDA gives you easy, Pythonic access to Nvidia’s CUDA parallel computation API. 

*   Abstractions make CUDA programming easier
*   Full power of CUDA API if needed
*   Automatic error checking and cleanup

## **Initialization**
A few modules have to be loaded to initialize communication to the GPU:

*   import pycuda.driver as cuda
*   import pycuda.autoinit

The pycuda.driver module has methods that:
1. Allocate memory on the GPU (cuda.mem alloc())
2. Copy numpy arrays to the GPU (cuda.memcpy htod())
3. Execute kernels on the GPU described by CUDA code (see compiler.SourceModule)
4. Copy data from the GPU back to numpy arrays (cuda.memcpy dtoh()).
"""

# Import PyCUDA and several modules associated with the PyCUDA
!pip install pycuda 
import pycuda
import pycuda.driver as cuda
cuda.init()

import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.gpuarray as gpuarray
from pycuda.curandom import rand as curand
from pycuda.elementwise import ElementwiseKernel

import numpy as np
import numpy.linalg as la

"""## **CUDA device query**

A GPU query is a very basic operation that will tell us the specific technical details of our GPU, such as available GPU memory and core count.
"""

print('CUDA device query (PyCUDA version) \n')
print('Detected {} CUDA Capable device(s) \n'.format(cuda.Device.count()))
for i in range(cuda.Device.count()):
    
    gpu_device = cuda.Device(i)
    print('Device {}: {}'.format( i, gpu_device.name() ) )
    compute_capability = float( '%d.%d' % gpu_device.compute_capability() )
    print('\t Compute Capability: {}'.format(compute_capability))
    print('\t Total Memory: {} megabytes'.format(gpu_device.total_memory()//(1024**2)))

"""## **Basics of GPU programming**

We'll see how to write and read data to and from the GPU's memory, and how to write some very simple elementwise GPU functions in CUDA C.

### PyCUDA's gpuarray class

PyCUDA's gpuarray class has important role within GPU programming in Python. This has all of the features from NumPy—multidimensional vector/matrix/tensor shape structuring, array-slicing, array unraveling, and overloaded operators for point-wise computations (for example, +, -, *, /, and **).

### Transfering data to and from the GPU with gpuarray

GPU has its own memory apart from the host computer's memory, which is known as device memory. 
In CUDA C, data is transfferd back and forth between the CPU to the GPU (with commands such as cudaMemcpyHostToDevice and cudaMemcpyDeviceToHost).

Fortunately, PyCUDA covers all of the overhead of memory allocation, deallocation, and data transfers with the gpuarray class.
"""

#contain the host data
host_data = np.array([1,2,3,4,5], dtype=np.float32)
#transfer the host data to the GPU and create a new GPU array
device_data = gpuarray.to_gpu(host_data)
#perform pointwise multiplication on the GPU
device_data_x2 = 2* device_data
#retrieve the GPU data into a new with the gpuarray.get function
host_data_x2 = device_data_x2.get()
print(host_data_x2)

"""## **Example: Doubling the value of elements in an array**

Here, we will take an array and double the element of it on the GPU.

### Step1: Getting started
"""

# Declare the array as follows:
np.random.seed(1729)
a = np.random.randn(4,4).astype(np.float32)

"""### Step 2: Transferring Data to the GPU

The next step in most programs is to transfer data onto the device. In PyCuda, you will mostly transfer data from numpy arrays on the host.
"""

# firstly, we need to allocate memory on the device
a_gpu = cuda.mem_alloc(a.nbytes)

# we need to transfer the data to the GPU
cuda.memcpy_htod(a_gpu, a)

"""### Step 3: Executing a Kernel

For this tutorial, we will write code to double each entry in a_gpu. To this end, we write the corresponding CUDA C code, and feed it into the constructor of a [pycuda.compiler.SourceModule](https://documen.tician.de/pycuda/driver.html#pycuda.compiler.SourceModule):
"""

# Double each entry in the variable a_gpu
mod = SourceModule("""
  __global__ void twice(float *a)
  {
    int idx = threadIdx.x + threadIdx.y*4;
    a[idx] *= 2;
  }
  """)

"""If there aren’t any errors, the code is now compiled and loaded onto the device. We find a reference to [pycuda.driver.Function](https://documen.tician.de/pycuda/driver.html#pycuda.driver.Function) and call it, specifying a_gpu as the argument, and a block size of 4x4:"""

func = mod.get_function("twice")
func(a_gpu, block=(4,4,1))

"""Finally, we fetch the data back from the GPU and display it, together with the original a:"""

a_doubled = np.empty_like(a)
cuda.memcpy_dtoh(a_doubled, a_gpu)

print("a",a)
print("\nDoubled value",a_doubled)

"""### Abstracting Away the Complications

Using a [pycuda.gpuarray.GPUArray](https://documen.tician.de/pycuda/array.html#pycuda.gpuarray.GPUArray), the same effect can be achieved with much less writing:
"""

# implementing with gpu_array
a_gpu = gpuarray.to_gpu(a)
a_doubled = (2*a_gpu).get()
print("a",a)
print("\nDoubled value",a_doubled)

"""### Shortcuts for Explicit Memory Copies

The [pycuda.driver.In](https://documen.tician.de/pycuda/driver.html#pycuda.driver.In), [pycuda.driver.Out](https://documen.tician.de/pycuda/driver.html#pycuda.driver.Out), and [pycuda.driver.InOut](https://documen.tician.de/pycuda/driver.html#pycuda.driver.InOut) argument handlers can simplify some of the memory transfers. For example, instead of creating a_gpu, if replacing a is fine, the following code can be used:
"""

# implementing with InOut
func(cuda.InOut(a), block=(4, 4, 1))
print("a",a)

"""## **Example: Addition of two 1D arrays**

Here, we will add two 1D arrays and execute it on GPU.
"""

# declare arrays
m = np.random.randn(10).astype(np.float32)
n = np.random.randn(10).astype(np.float32)

# execute the kernel
mod2_1D = SourceModule("""
__global__ void sum2arr(float *sum, float *m, float *n)
{
  const int i = threadIdx.x;
  sum[i] = m[i] + n[i];
}
""")

func = mod2_1D.get_function("sum2arr")

# handle memory transfer with 'Out()'
sum_1D = np.zeros_like(m)
func(cuda.Out(sum_1D),
     cuda.In(m), cuda.In(n),
     block=(10,1,1))

# print result
print("m",m)
print("\nn",n)
print("\nsum",sum_1D)

"""## **Example: Addition of matrices**

Here, we will add two matrices and execute it on GPU.
"""

# declare matrices
b = np.random.randn(4,4).astype(np.float32)
c = np.random.randn(4,4).astype(np.float32)

# execute the kernel
mod2_2D = SourceModule("""
  __global__ void add2(float *a, float *b)
  {
    int idx = threadIdx.x + threadIdx.y*4;
    a[idx] += b[idx];
  }
  """)

func = mod2_2D.get_function("add2")

# transfer the data to the GPU
b_gpu = cuda.mem_alloc(b.nbytes)
c_gpu = cuda.mem_alloc(c.nbytes)

cuda.memcpy_htod(b_gpu, b)
cuda.memcpy_htod(c_gpu, c)

func(b_gpu,c_gpu, block=(4,4,1))

sum_2D = np.empty_like(b)
cuda.memcpy_dtoh(sum_2D, b_gpu)

# print result
print("b",b)
print("\nc",c)
print("\nsum",sum_2D)

"""##**Example: Multiplication of matrices**

Here, we will multiple two matrices and execute it on GPU.
"""

# declare matrices
r = np.random.randn(10).astype(np.float32)
s = np.random.randn(10).astype(np.float32)

# execute kernel
mod3 = SourceModule("""
__global__ void multiply2arr(float *dest, float *r, float *s)
{
  const int i = threadIdx.x;
  dest[i] = r[i] * s[i];
}
""")

func = mod3.get_function("multiply2arr")

product = np.zeros_like(r)

# handle memory transfer
func(cuda.Out(product),
     cuda.In(r), cuda.In(s),
     block=(10,1,1))

# print result
print("r",r)
print("\ns",s)
print("\nproduct",product)

"""## **Example: Linear combination of variables**

The functionality in the module [pycuda.elementwise](https://documen.tician.de/pycuda/array.html#module-pycuda.elementwise) contains tools to help generate kernels that evaluate multi-stage expressions on one or several operands in a single pass. Here's a usage example:
"""

# generate arrays of random numbers using curand()
n1_gpu = curand((10,))
n2_gpu = curand((10,))

# generate a kernel that takes a number of scalar or vector arguments and performs the scalar operation on each entry of its arguments, if that argument is a vector.
linear_combination = ElementwiseKernel(
        "float a, float *x, float b, float *y, float *z",
        "z[i] = my_f(a*x[i], b*y[i])",
        "linear_combination",
        preamble="""
        __device__ float my_f(float x, float y)
        { 
          return sin(x*y);
        }
        """)

# make a new, uninitialized GPUArray having the same properties as other_ary
c_gpu = gpuarray.empty_like(n1_gpu)

# call the function
linear_combination(5, n1_gpu, 6, n2_gpu, c_gpu)

# test for a particular condition
assert la.norm(c_gpu.get() - np.sin((5*n1_gpu*6*n2_gpu).get())) < 1e-5

"""## **Example: Numba and PyCUDA**

The module [pycuda.autoprimaryctx](https://documen.tician.de/pycuda/util.html#module-pycuda.autoprimaryctx) is similar to [pycuda.autoinit](https://documen.tician.de/pycuda/util.html#module-pycuda.autoinit), except that it retains the device primary context instead of creating a new context in [pycuda.tools.make_default_context()](https://documen.tician.de/pycuda/util.html#pycuda.tools.make_default_context). Notably, it also has device and context attributes.
"""

from numba import cuda

# Using autoprimaryctx instead of autoinit since Numba can only operate on a primary context
import pycuda.autoprimaryctx  

# Creating a PyCUDA gpuarray
print("a",a_gpu)

# Numba kernel
@cuda.jit
def double(x):
    i, j = cuda.grid(2)

    if i < x.shape[0] and j < x.shape[1]:
        x[i, j] *= 2

# Calling the Numba kernel on the PyCUDA gpuarray, using the CUDA Array Interface transparently
double[(4, 4), (1, 1)](a_gpu)
print("Doubling values using numba: ",a_gpu)

"""# **Exercise**

- Write a cuda kernel to find the elementwise square of a matrix
- Write a cuda kernel to find a matrix, which when added to the given matrix results in every element being equal to zero
- Write a cuda kernel to multiply two matrices:
  - Assume square matrices, with dimensions < 1024
  - Assume square matrices, with dimensions > 1024
  - Assume non-square matrices, with dimensions > 1024
"""

# Write your own code here