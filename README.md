# Bee Swarm Navigation

## About
This repository is for a final project for CU Boulder's Dynamic Models in Biology class.
  
The swarm model will be based on the model from the paper [*Honeybee swarms: how do scouts guide a swarm of uninformed bees?*](https://www.sciencedirect.com/science/article/abs/pii/S0003347205001016) by Stephan Janson, Martin Middendorf and Madeleine Beekman.
  
We are using the [mesa](https://github.com/projectmesa/mesa) Python library for multi-agent simulation for this project.
  
Since one of the core parts of the model is essentially just the ["boids" model](https://team.inria.fr/imagine/files/2014/10/flocks-hers-and-schools.pdf). we are using the mesa [example implementation of boids](https://github.com/projectmesa/mesa/tree/main/examples/boid_flockers) as a starting point.  The behavior of the agents is our implementation (in progress) of the Janson et al. paper cited above.  The visualization is what came with the example and probably will continue to remain very similar in the future to avoid reinventing the wheel. (scouts will need a different color though).
  
## Setup
There's a good chance that if you're reading this you know more about dependency management with Python than I do.  But I will do my best to explain my own setup and update this section as I get better with this.
  
The first thing to do is to clone this repository.
  
After that navigate into the
I am using the Anaconda distribution of Python, but mesa as far as I'm aware needs to be installed using `pip`.
  
I would highly recommend using a virtual environment for this project (and every project) since global dependency management is a massive headache.  If you're using anaconda, to make a virtual environment use:
```
conda create -n <environment-name> python=3.7.10
```
(If you're like me and care what the flags stand for `-n` is shorthand for `--name`).
  
If conda doesn't come up on your command line you may need to use anaconda prompt (I think this is installed by default with anaconda).
  
To activate your virtual environment use:
```
conda activate <environment-name>
```
If you want to deactivate it you can use:
```
conda deactivate
```
Finally, if you made some horrible mistake and need to delete the environment you can use:
```
conda env remove -n <environment-name>
```
  
As far as I can tell, anaconda should put the default pacakges for the anaconda distribution into your virtual environment.  When your environment is activated, you can check what is installed by using:
```
conda list
```
When I do this, there are quite a few packages installed already, if for some reason there aren't any, you will at least want to install `numpy`, `matplotlib`, and probably `pandas` (it's not being used right now, but it's often useful).
  
Conda and pip can have issues working together, Anaconda's advice as of now is that if you need to use them together, you should install everything you can with `conda` first, then use `pip` afterwards as needed.
  
There are two installs you should do with conda.  First if you don't have pip in your virtual environment use:
```
conda install pip
```
Second, in order for Jupyter notebook to be able to find your virtual environment, you will probably need to run:
```
conda install -c anaconda ipykernel
```
Then run the command:
```
python -m ipykernel install --user --name=<your-environment>
```
  
finally you will need to use `pip` to install mesa:
```
pip install mesa
```
  
This process can be made simpler in the future with requirements files, but I'm not exactly sure how they work when using anaconda and pip together.

## Setup with pip

This actually seems like an easier option.  Clone the repo and create a virtual environment for it.  Then activate the virtual environment.  Inside of the virtual environment, you should just need to `pip install` `numpy`, `matplotlib`, and `mesa`.

## Issues / Further work
Right now only uninformed bees are implemented.  Scouts will still need to be added.  We will also need to add a goal location in order to see if the simulated bees are able to slow down when they reach their new home.