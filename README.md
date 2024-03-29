# Train excitatory-inhibitory recurrent neural networks for cognitive tasks

## Requirements

This code was written in Python 2.7 originally but in this repo has been modified to python 3.8 and requires

* [Theano 1.0.5]

Optional but recommended if you plan to run many trials with the trained networks outside of Theano:

* [Cython](http://cython.org/)

Optional but recommended for analysis and visualization of the networks (including examples from the paper):

* matplotlib

The code uses (but doesn't require) one function from the [NetworkX](https://networkx.github.io/) package to check if the recurrent weight matrix is connected (every unit is reachable by every other unit), which is useful if you plan to train very sparse connection matrices.

## Installation

Because you will eventually want to modify the `pycog` source files, we recommend that you "install" by simply adding the `pycog` directory to your `$PYTHONPATH`, and building the Cython extension to (slightly) speed up Euler integration for testing the networks by typing

```
python setup.py build_ext --inplace
```

You can also perform a "standard" installation by going to the `pycog` directory and typing

```
python setup.py install
```
## NOTE 
A Documentation and code steps followed throughout from start to end of training of S1_code.py, has been provided and can be used to write similar code for the same, in Different language for ML or software like MatLab etc.
- Written by Mohit Mathuria

## Examples

Example task specifications, including those used to generate the figures in the paper, can be found in `examples/models`.

Training and testing networks involves some boring logistics, especially regarding file paths. You may find the script `examples/do.py` helpful as you start working with your own networks. For instance, to train a new network we can just type (from the `examples` directory)

```
python do.py models/sinewave train
```

For this particular example we've also directly included code for training and plotting the result, so you can simply type

```
python models/sinewave.py
```
There are other do.py functions available like run, check, clean, submit, restingstate, structure and costs
From which restingstate, structure and costs are used to generate respective graphs showing restingstate, structure and costs throughout training


## Notes

* The default recurrent noise level (used for most of the tasks in our paper) is rather high. When training a new task start with a value of `var_rec` that is small, then increase the noise for more robust solutions.

* A list of parameters and their default values can be found in `defaults.py`

* The default time step is also relatively large, so always test with a smaller time step (say 0.05) and re-train with a smaller step size if the results change.

* By default, recurrent and output biases are set to zero. If you encounter difficulties with training, try including the biases by setting `train_brec = True` and/or `train_bout = True`.

* If you still have difficulties with training, try changing the value of `lambda_Omega`, the multiplier for the vanishing-gradient regularizer.

* It's common to see the following warning when running Theano:

  ```
  RuntimeWarning: numpy.ndarray size changed, may indicate binary incompatibility
  rval = __import__(module_name, {}, {}, [module_name])
  ```
  or

  ```
  WARNING (theano.tensor.blas): Using NumPy C-API based implementation for BLAS functions.
  ERROR (theano.gpuarray): pygpu was configured but could not be imported or is too old (version 0.7 or higher required)
  ```

  This is almost always innocuous and can be safely ignored. 
  Except for the fact that it is unable to use GPU if this shows up. But it will still work around with CPU

## Acknowledgments

This code would not be possible without

* On the difficulty of training recurrent neural networks.                                         
  R. Pascanu, T. Mikolov, & Y. Bengio, ICML 2013.                                                  
  https://github.com/pascanur/trainingRNNs


## License

MIT

## Citation

* This code is the product of work carried out in the group of [Xiao-Jing Wang at New York University](http://www.cns.nyu.edu/wanglab/). If you find our code helpful to your work, consider giving us a shout-out in your publications:

* Song, H. F.\*, Yang, G. R.\*, & Wang, X.-J. "Training Excitatory-Inhibitory Recurrent Neural Networks for Cognitive Tasks: A Simple and Flexible Framework." *PLoS Comp. Bio.* 12, e1004792 (2016). (\* = equal contribution)

* It was modified to python 3.8 by:
Mohit Mathuria
Junior Undergraduate Student, IIT Jodhpur 2022
As part of summer project under prof. Shilpa Dang, Assistant Professor
School of Artificial Intelligence and Data Science (AIDE)
