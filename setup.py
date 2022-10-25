import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="sterling-utils",
    version="0.0.1",
    author="Sodiq Ridwan",
    author_email="daniel.ale@prunedge.com",
    packages=["sterling_shared"],
    description="A utilty package for sterling core",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/Prunedge-Dev-Team/retailcore-shared-python",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)