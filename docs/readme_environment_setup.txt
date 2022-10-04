Erik Plesko 27.7.2022


General notes (to type into notin)
- I partially followed this guide on good python practices:
https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/




# Creating the environment on the PC in the lab (Windows 7)

1. Python 3.6 was installed on the system prior to my work

2. I installed poetry with (using the terminal in Pycharm):
Command: curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
Output: Poetry (1.1.14) is installed now. Great!


Restarted Pycharm (install folder of poetry was added to path automatically)

Check the installation with
Command: poetry -V

3. Create a new project with poetry
Command: poetry new magneticTweezers

4. Installed python version 3.8.10 (downloading the win installer from the website, it wasn't so easy to install pyenv)
Set it as active in Pycharm (File -> Settings, Project -> Project Interpreter) (and maybe restart Pycharm)

5. Install the project with:
specify the packages and versions in the pyproject.toml
And then run
Command: poetry update
((Command: poetry install     - not sure if you need this one..))

6. Run the notebook
first activate the environment with poetry shell.
The first time you should also add a new kernel (with the command):
Command: python -m ipykernel install --user --name <kernel_name> --display-name "<Name_to_display>"
I used: python -m ipykernel install --user --name python_magtw --display-name "Magnetic tweezers"

And then run the notebook:
Command: jupyter notebook

When the notebook opens, change the kernel to the one you created.




-------------------------------------------------------------------------------------
# Some additional tweaks:
1. Changed jupyther color theme to monokai (onedork is also nice):
Command: jt -t monokai
https://stackoverflow.com/questions/46510192/change-the-theme-in-jupyter-notebook



-------------------------------------------------------------------------------------
Next time I wanted to create new poetry environment and I had some problems.
- First wrong python was used on path (I changed the path so that 3.8 is used, instead of 3.6)
- Then The poetry update was successful, and I also added a new kernel.
