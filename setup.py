import setuptools
import os
with open("README.md", "r") as fh:
    description = fh.read()
# github_token = os.environ['GITHUB_TOKEN']

setuptools.setup(
    name="sterling-utils",
    version="0.0.1",
    author="Ridwan Sodiq",
    author_email="daniel.ale@prunedge.com",
    packages=["sterling_shared"],
    description="A utilty package for sterling core",
    long_description=description,
    long_description_content_type="text/markdown",
    # url=f"git+https://{github_token}@github.com/Prunedge-Dev-Team/retailcore-shared-python.git",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)