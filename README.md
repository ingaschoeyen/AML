# AML
code, writing, and results from the project "AI-powered search and analysis of infrastructure asset archives" for the Machine Learning Challenge '26


# Python version
We will use a Python 3.13.12 .venv

Required libraries and their versions should be placed in the requirement.txt file

I got my Python 3.13.12 .venv using uv. The process looked like this:

(using my laptops native python)
python -m pip install uv

(while in the root AML folder)

python -m uv venv --python 3.13.12

.\.venv\Scripts\activate

Then installing the requirements :

pip install -r requirements.txt

# Configs
Make sure to set the paths in configs/filePaths.py to the correct paths on your system
