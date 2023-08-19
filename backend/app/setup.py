from setuptools import setup, find_packages

setup(
    name="dnada",
    version="0.1",
    author="Alberto Nava",
    author_email="alberto_nava@berkeley.edu",
    description="An application for creating customized synthetic biology automation instructions",
    url="https://github.com/JBEI/dnada",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    license="Apache 2.0",
)
