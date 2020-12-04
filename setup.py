import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ift6113-final-project-deepsdf",
    version="0.0.1",
    author="Sylvain Laporte",
    author_email="sylvain.laporte.2@umontreal.ca",
    description="Final project for course IFT6113",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: ",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)