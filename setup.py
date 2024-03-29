import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyCosimLibrary",
    version="0.0.5",
    author="Claudio Gomes",
    author_email="claudio.gomes@eng.au.dk",
    description="A co-simulation library with the most common master algorithms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clagms/PyCosimLibrary",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'fmpy'
    ],
    python_requires='>=3.6',
)
