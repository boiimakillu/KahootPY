import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="KahootPY",
    version="0.0.1",
    author="theusaf",
    author_email="theusafyt@gmail.com",
    description="A python package to interact with Kahoot!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/theusaf/kahoot.js-updated/tree/python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords=["kahoot","bot"],
    install_requires=["websocket-client","pymitter"],
)
