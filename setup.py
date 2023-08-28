from setuptools import setup, find_packages
import os

setup(
    name="dnada",
    version="0.1",
    maintainer="Alberto Nava",
    maintainer_email="alberto_nava@berkeley.edu",
    description=(
        "An application for creating customized "
        "synthetic biology automation instructions"
    ),
    url="https://github.com/JBEI/dnada",
    packages=find_packages(where=os.path.join("backend", "app", "app")),
    package_dir={"": os.path.join("backend", "app", "app")},
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
