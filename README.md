# Software Project Estimator

![pylint workflow](https://github.com/matthewsewell/software-project-estimator/actions/workflows/pylint.yml/badge.svg)
![unittest workflow](https://github.com/matthewsewell/software-project-estimator/actions/workflows/unittest.yml/badge.svg)

## Installing

This library has not been added to pypi yet but will be soon. For now, you can
build it locally and install the result into your local environment or into
the virtual environmnet of your choice. These instructions assume that you have
python3 installed on a *nix system. If you are on Windows, substitute `py`
for `python3`.

First, make sure you have the latest version of `pip`.
```
python3 -m pip install --upgrade pip
```

To build the distribution package, make sure you have the latest version of
`build`.
```
python3 -m pip install --upgrade build
```

Now you can run the build command from the root of this project.
```
python3 -m build
```
This will create a folder in the project named `dist` with the following
structure.
```
dist/
├── python_software_project_estimator-0.0.1-py3-none-any.whl
└── python_software_project_estimator-0.0.1-py3-none-any.tar.gz
```

Now you can now install the package to your local system using `pip`.
```
sudo pip install dist/python_software_project_estimator-0.0.1.tar.gz
```
