# Co-sim library

A co-simulation library with the most common master algorithms.

# Install from PyPi:

```
pip install PyCosimLibrary
```

# Install from local source

```
pip install -e .
```

# Publishing this package on pypi

```
python setup.py sdist bdist_wheel
python -m twine upload dist/*
set user and password according to pypi's api token