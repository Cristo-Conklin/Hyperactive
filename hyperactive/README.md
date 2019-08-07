# Advanced Features

The features listed below can be activated during the instantiation of the optimizer ([see API](https://github.com/SimonBlanke/hyperactive#hyperactive-api)) and works with every optimizer in the hyperactive package.


### [Memory](https://github.com/SimonBlanke/Hyperactive/blob/master/examples/example_memory.py)
After the evaluation of a model the position (in the hyperparameter search dictionary) and the cross-validation score are written to a dictionary. If the optimizer tries to evaluate this position again it can quickly lookup if a score for this position is present and use it instead of going through the extensive training and prediction process.


### [Scatter-Initialization](https://github.com/SimonBlanke/Hyperactive/blob/master/examples/example_scatter_init.py)
This technique was inspired by the 'Hyperband Optimization' and aims to find a good initial position for the optimization. It does so by evaluating n random positions with a training subset of 1/n the size of the original dataset. The position that achieves the best score is used as the starting position for the optimization.


### [Multiprocessing](https://github.com/SimonBlanke/Hyperactive/blob/master/examples/example_multiprocessing.py)
The multiprocessing in hyperactive works by creating additional searches, that run in parallel without any shared memory. This provides the possibility of hyperparameter-tuning of different models at the same time. If one single model should be tuned as fast as possible n_jobs in the optimizer should be set to '1', while n_jobs (of the model) in the search_config should be set to '-1'.

<details><summary>Two searches with eight cpu-cores:</summary>
<p>

```python
import numpy as np

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from hyperactive import RandomSearchOptimizer

iris_data = load_iris()
X = iris_data.data
y = iris_data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

# this defines the model and hyperparameter search space
search_config = {
    "sklearn.ensemble.RandomForestClassifier": {
        "n_estimators": range(10, 100, 10),
        "max_depth": [3, 4, 5, 6],
        "criterion": ["gini", "entropy"],
        "n_jobs": [4],
    },
    "sklearn.ensemble.GradientBoostingClassifier": {
        "n_estimators": range(10, 100, 10),
        "max_depth": range(1, 11),
        "min_samples_split": range(2, 21),
        "n_jobs": [4],
    },
}

Optimizer = RandomSearchOptimizer(search_config, n_iter=300, n_jobs=2, verbosity=0)

# search best hyperparameter for given data
Optimizer.fit(X_train, y_train)
```

</p>
</details>


<details><summary>One search with all cpu-cores:</summary>
<p>

```python
import numpy as np

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from hyperactive import RandomSearchOptimizer

iris_data = load_iris()
X = iris_data.data
y = iris_data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

# this defines the model and hyperparameter search space
search_config = {
    "sklearn.ensemble.RandomForestClassifier": {
        "n_estimators": range(10, 100, 10),
        "max_depth": [3, 4, 5, 6],
        "criterion": ["gini", "entropy"],
        "n_jobs": [-1],
    },
}

Optimizer = RandomSearchOptimizer(search_config, n_iter=300, n_jobs=1, verbosity=0)

# search best hyperparameter for given data
Optimizer.fit(X_train, y_train)
```

</p>
</details>




<details><summary>Multiple searches with all cpu-cores:</summary>
<p>

```python
import numpy as np

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from hyperactive import RandomSearchOptimizer

iris_data = load_iris()
X = iris_data.data
y = iris_data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

# this defines the model and hyperparameter search space
search_config = {
    "sklearn.ensemble.RandomForestClassifier": {
        "n_estimators": range(10, 100, 10),
        "max_depth": [3, 4, 5, 6],
        "criterion": ["gini", "entropy"],
        "min_samples_split": range(2, 21),
        "min_samples_leaf": range(2, 21),
    },
    "sklearn.neighbors.KNeighborsClassifier": {
        "n_neighbors": range(1, 10),
        "weights": ["uniform", "distance"],
        "p": [1, 2],
    },
    "sklearn.ensemble.GradientBoostingClassifier": {
        "n_estimators": range(10, 100, 10),
        "learning_rate": [1e-3, 1e-2, 1e-1, 0.5, 1.0],
        "max_depth": range(1, 11),
        "min_samples_split": range(2, 21),
        "min_samples_leaf": range(1, 21),
        "subsample": np.arange(0.05, 1.01, 0.05),
        "max_features": np.arange(0.05, 1.01, 0.05),
    },
    "sklearn.tree.DecisionTreeClassifier": {
        "criterion": ["gini", "entropy"],
        "max_depth": range(1, 11),
        "min_samples_split": range(2, 21),
        "min_samples_leaf": range(1, 21),
    },
}

Optimizer = RandomSearchOptimizer(search_config, n_iter=300, n_jobs=-1, verbosity=0)
```

</p>
</details>


### [Transfer-Learning](https://github.com/SimonBlanke/Hyperactive/blob/master/examples/example_transfer_learning.py)
In the current implementation transfer-learning works by using a predefined model (with optional pretrained weights) provided by the keras package. The import path can be inserted as a layer (with its parameters in an sub-dictionary), like in a regular search dictionary. The following snippet provides an example:

<details><summary>Transfer-learning example:</summary>
<p>

```python
from keras.datasets import cifar10
from keras.utils import to_categorical

from hyperactive import SimulatedAnnealingOptimizer

(X_train, y_train), (X_test, y_test) = cifar10.load_data()

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)


# this defines the structure of the model and the search space in each layer
search_config = {
    "keras.compile.0": {"loss": ["binary_crossentropy"], "optimizer": ["adam"]},
    "keras.fit.0": {"epochs": [1], "batch_size": [300], "verbose": [0]},
    # just add the pretrained model as a layer like this:
    "keras.applications.MobileNet.1": {
        "weights": ["imagenet"],
        "input_shape": [(32, 32, 3)],
        "include_top": [False],
    },
    "keras.layers.Flatten.2": {},
    "keras.layers.Dense.3": {
        "units": range(5, 15),
        "activation": ["relu"],
        "kernel_initializer": ["uniform"],
    },
    "keras.layers.Dense.4": {"units": [10], "activation": ["sigmoid"]},
}


Optimizer = SimulatedAnnealingOptimizer(
    search_config, n_iter=3, warm_start=False, verbosity=0
)
```

</p>
</details>


### [Warm-Start](https://github.com/SimonBlanke/Hyperactive/blob/master/examples/example_warm_start_sklearn.py)

When a search is finished the warm-start-dictionary for the best position in the hyperparameter search space (and its metric) is printed in the command line (at verbosity=1). If multiple searches ran in parallel the warm-start-dictionaries are sorted by the best metric in decreasing order. If the start position in the warm-start-dictionary is not within the search space defined in the search_config an error will occure.

<details><summary>Warm-start example for sklearn model:</summary>
<p>

```python
start_point = {
    "sklearn.ensemble.RandomForestClassifier.0": {
        "n_estimators": [30],
        "max_depth": [6],
        "criterion": ["entropy"],
        "min_samples_split": [12],
        "min_samples_leaf": [16],
    },
    "sklearn.ensemble.RandomForestClassifier.1": {
        "n_estimators": [50],
        "max_depth": [3],
        "criterion": ["entropy"],
    },
}
```

</p>
</details>


<details><summary>Warm-start example for keras model (cnn):</summary>
<p>

```python
start_point = {
    "keras.compile.0": {"loss": ["categorical_crossentropy"], "optimizer": ["adam"]},
    "keras.fit.0": {"epochs": [3], "batch_size": [500], "verbose": [0]},
    "keras.layers.Conv2D.1": {
        "filters": [64],
        "kernel_size": [3],
        "activation": ["relu"],
        "input_shape": [(28, 28, 1)],
    },
    "keras.layers.MaxPooling2D.2": {"pool_size": [(2, 2)]},
    "keras.layers.Conv2D.3": {
        "filters": [32],
        "kernel_size": [3],
        "activation": ["relu"],
        "input_shape": [(28, 28, 1)],
    },
    "keras.layers.MaxPooling2D.4": {"pool_size": [(2, 2)]},
    "keras.layers.Conv2D.5": {
        "filters": [32],
        "kernel_size": [3],
        "activation": ["relu"],
        "input_shape": [(28, 28, 1)],
    },
    "keras.layers.MaxPooling2D.6": {"pool_size": [(2, 2)]},
    "keras.layers.Flatten.7": {},
    "keras.layers.Dense.8": {"units": [50], "activation": ["softmax"]},
    "keras.layers.Dropout.9": {"rate": [0.4]},
"keras.layers.Dense.10": {"units": [10], "activation": ["softmax"]},
}
```

</p>
</details>