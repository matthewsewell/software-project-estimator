# Software Project Estimator

![pylint workflow](https://github.com/matthewsewell/software-project-estimator/actions/workflows/pylint.yml/badge.svg)
![unittest workflow](https://github.com/matthewsewell/software-project-estimator/actions/workflows/unittest.yml/badge.svg)

## Installing

This library has not been added to pypi yet but will be soon. For now, you can
build it locally and install the result into your local environment or into
the virtual environment of your choice. These instructions assume that you have
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

Now you can install the package to your local system using `pip`.
```
sudo pip install dist/python_software_project_estimator-0.0.1.tar.gz
```

 ## Usage
 Here's an extremely trivial example.
 ```
from datetime import date

from software_project_estimator import Project, Task
from software_project_estimator.simulation.monte_carlo import MonteCarlo


task = Task(name="This is the only task", optimistic=10, pessimistic=22, likely=15)
project = Project(name="My Project", start_date=date(2023, 1, 1), weeks_off_per_year=0)
project.tasks = [task]

monte = MonteCarlo(project, 100_000)
results = monte.run()

for day, result in results.items():
    print(f"{day}: {result}")
 ```

 This will print something like this.
 ```
2023-01-17: total=8 probability=8e-05
2023-01-18: total=80 probability=0.00088
2023-01-19: total=352 probability=0.0044
2023-01-20: total=1104 probability=0.01544
2023-01-23: total=3392 probability=0.04936
2023-01-24: total=7744 probability=0.1268
2023-01-25: total=12528 probability=0.25208
2023-01-26: total=18184 probability=0.43392
2023-01-27: total=19776 probability=0.63168
2023-01-30: total=16656 probability=0.79824
2023-01-31: total=11280 probability=0.91104
2023-02-01: total=5672 probability=0.96776
2023-02-02: total=2312 probability=0.99088
2023-02-03: total=712 probability=0.998
2023-02-06: total=184 probability=0.99984
2023-02-07: total=16 probability=1.0
 ```
 As you can see, the 50% probability mark is somewhere between the 26th or the
 27th of January. This is because the end date is actually the first date on
 which the project is actually finished -- not the last date on which work was
 performed. Let's take a closer look.
 `task.average` tells us that our weighted average outcome should be `15.33`
 person days. Since we only have one person working on this task and we're
 working 5 day weeks, you could look at this and say, "This will take a little
 over three weeks."

 Looking at the calendar, out project started on 1/1/2023, which was a Sunday.
 Also, New Year's day was observed in the US on 1/2. The first day we can
 actually work is 1/3. MLK Day was observed on 1/16, so that's also a day we
 don't work in the US. The 15.33 days we're actually working are 1/3/, 1/4, 1/5,
 1/6, 1/9, 1/10, 1/11, 1/12, 1/13, 1/17, 1/18, 1/19, 1/20, 1/23, 1/24, and 1/25.
 That means that, at around the 50% probability, the first day we don't work on
 this project is 1/26.

 This is all well and good but, really, do you want to commit to finishing
 at the 50% mark? You may as well flip a coin to see if you can finish on time.
 What's important here is the *shape* of the outcomes. There's close to a 2/3
 probability that this project can be completed before 1/27 based on our
 three--point estimate. This is probably a decent estimate of how long it will
 take in the real world. What you choose to communicate to the boss is up to
 you.
