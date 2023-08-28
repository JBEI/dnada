from setuptools import setup, find_packages
import os
import io

DESCRIPTION = (
    "An application for creating customized "
    "synthetic biology automation instructions"
)
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name="dnada",
    version="0.1.2",
    maintainer="Alberto Nava",
    maintainer_email="alberto_nava@berkeley.edu",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JBEI/dnada",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "autoprotocol",
        "alembic",
        "bcrypt",
        "biopython",
        "celery",
        "emails",
        "email_validator",
        "fastapi",
        "k_means_constrained",
        "openpyxl",
        "pandas",
        "pandera",
        "passlib",
        "psycopg2-binary",
        "pydantic",
        "python_jose",
        "pytz",
        "raven",
        "requests",
        "scipy",
        "seaborn",
        "SQLAlchemy",
        "tenacity",
        "typer",
    ],
    license="Apache 2.0",
    entry_points={
        "console_scripts": [
            "dnada_cli = app.dnada_cli:cli",
        ],
    },
)
