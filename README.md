exp-base
========



`expbase` is a Python framework that implements a commonly used boilerplate for machine learning experiments.
To that end, it takes care of preparing the usual experimental setup for you, and thus significantly reduces the amount
of code you have to write in order to run your experiments.
More precisely, `expbase` implements the following setup tasks:

1. parse command-line args, and create a config object,
1. prepare the results directory,
1. store the used config as JSON file in the results directory,
1. set up logging,
1. launch the training procedure in a separate process, and
1. wait for checkpoints to be created and launch the evaluation of each in a separate process as it is created.



Installation
------------


The package `expbase` can be installed via pip as follows:

```bash
pip install expbase
```



How-To
------


### Step 1: Define Your Config Class

`expbase` uses [`argmagiq`](https://github.com/phohenecker/arg-magiq) to parse command-line args into a configuration
object, which means that you have to define a config class that describes the user-defined configuration for running an
experiment.
If you should not be familiar with `argmagiq`, then please read about it
[here](https://github.com/phohenecker/arg-magiq).
To that end, your configuration class has to extend the class
[`expbase.BaseConfig`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/base_config.py),
which defines several configurations that are either used by `expbase` directly or required for all machine learning
experiments.
(Make sure to familiarize yourself with those.)


### Step 2: Implement The `TrainingExecutor` And The `EvaluationExecutor`

To provide the code for training and evaluation of your models, you have to implement two classes, one extending
[`expbase.TrainingExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/training_executor.py)
and one extending
[`expbase.EvaluationExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/evaluation_executor.py).
Those are abstract classes that require you to implement the methods `_run_training` and `_run_evaluation`,
respectively.
When an experiment is launched, your `TrainingExecutor` is run in a separate process, and whenever a training checkpoint
is delivered, your implementation of `EvaluationExecutor` is launched (in parallel) in another process in order to
evaluate the same.
In addition to this, both `TrainingExecutor` and `EvaluationExecutor` have a method `_init`, which may be overridden to
run code that would usually go into `__init__`.
The reason why we recommend using `_init` instead of `__init__` is that instances might be moved between processes
before `_run_*` is invoked, which occasionally results in issues, if certain objects are created in the
constructor.
However, `_init` is guaranteed to be invoked just before and in the same process as `_run_*`.

All created instances of `TrainingExecutor` and `EvaluationExecutor` are provided with an instance of your config class
that has been populated based on the given command-lines args.
Both classes store this config object in the attribute `_conf`, which you can use to access the user-defined
configuration of an experiment from your implementations of `_init` and `_run_*`.

For additional details, please have a look at the docstrings of
[`expbase.TrainingExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/training_executor.py)
and
[`expbase.EvaluationExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/evaluation_executor.py).


### Step 3: Launch The Experiment

Once you defined all required classes, launching an experiment is as easy as creating an instance of
[`expbase.Experiment`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/experiment.py), and
invoking it's `run` method:

```python
import expbase as xb

xb.Experiment(
        YourTrainingExecutorClass,
        YourEvaluationExecutorClass,
        YourConfigClass,
        app_name,
        app_description
).run()
```

In this code snippet, `app_name` and `app_description` are two strings that define the name of your application, which
is used in its synopsis (the usage instruction at the beginning of the help), as well as a description of the same,
which is displayed as part of the help text.


### Delivering Checkpoints

As pointed out above already, evaluation is launched automatically (in a parallel process) whenever a checkpoint is
delivered.
In order to deliver a checkpoint, the class
[`expbase.TrainingExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/training_executor.py)
(which you are extending with your own training code) provides the method `_deliver_ckpt`, which expects a single `str`
argument that allows for locating an according checkpoint file, usually a file path.
As it depends on the particular experiment, you have to create the checkpoint file in your implementation of
`_run_training` before you invoke `_deliver_ckpt`.
The checkpoint string is then provided to the `EvaluationExecutor` that is launched to evaluate the according
checkpoint and stored in the attribute `_ckpt`.
Therefore, your own implementation of
[`expbase.EvaluationExecutor`](https://github.com/phohenecker/exp-base/blob/master/src/main/python/expbase/evaluation_executor.py).
(more precisely, your `_init` and `_run_evaluation`) will find the checkpoint string stored in `self._ckpt`.


### Running Tests

If you just want to run a test (without training), for example, to evaluate your model on the test partition, then you
can use the command-line option `--test`, which causes `expbase` to launch only a single `EvaluationExecutor`.
Notice that, in this case, the attribute `_ckpt` of your `EvaluationExecutor` will be `None`.
Instead, however, you are required to manually specify a checkpoint when you run the application using the option
`--ckpt <CKPT>`, which is then accessible via the config, i.e., `self._conf.ckpt`.



Results Directory
-----------------


`expbase` creates a results directory for you, which is also used to store any files that are generated automatically
(e.g., log files, config, etc.).
By default, `./results/` is used as results directory, and can be adjusted by means of the arg `--results-dir`.
Notice further that, for every training run, a subdirectory is created within the results dir, named according to when
the experiment was conducted.
For example, when you run an experiment with `--results-dir ./fancy-results`, then results will be stored in
`./fancy-results/2020-06-22--10-11-28` (using the actual timestamp, of course).
Please notice that the config object passed to `TrainingExecutor` and `EvaluationExecutor`s contains the actual
results directory **including** the particular subdirectory.

Finally, you can (and should) use a title to be appended to your result directories in order to make them easier to
find.
To that end, use the arg `--title` to define a label to be appended to the directory that your experiment writes results
to.
For example, `--results-dir ./fancy-results --title project-ice-cream` defines the results directory to be
`./fancy-results/2020-06-22--10-11-28--project-ice-cream` (again, using the actual timestamp, of course).



Config File
-----------


To make it easier to rerun a conducted experiment, `expbase` stores the configuration that was used to run one as a
JSON file named `config.json` in the results directory.
This file is produced by means of [`argmagiq`](https://github.com/phohenecker/arg-magiq), and can thus be used
directly to launch the same experiment once again.
For example, if you ran an experiment from the terminal using the command
```bash
$ python main.py --results-dir results/ --seed 12345 ...
```
then you can rerun it with the exact same configuration using
```bash
$ python main.py -- path/to/the/config.json
```
Notice that, for experiments with a lot of configuration, it might be easier to only use config files in the first
place.



Logging
-------


`expbase` uses the package [`streamtologger`](https://github.com/phohenecker/stream-to-logger) to automatically log all
outputs produced via `print("...")` or by an exception, and stores them in three different log files in the results
directory:

1. `experiment.log` is a top-level log file used by the controller of the experiment,
2. `train.log` captures outputs produced by the `TrainingExecutor`, and
3. `eval.log` stores outputs produced by `EvaluationExecutor`s.

If you, for some reason, wish you to change the names of those files, you can use the options `--general-log`,
`--training-log`, and `--evaluation-log` to do so.  
