# DNAda

DNAda is a web application that integrates the [j5](https://j5.jbei.org)
DNA assembly software with robotic liquid handlers.

## Background

J5 is a powerful DNA assembly software that can be used to design
and optimize DNA assembly protocols. However, it is not directly compatible with
robotic liquid handlers. DNAda is a web/command-line application
that integrates j5 with robotic liquid handlers by converting a
j5 assembly design into a series of liquid handler compatible instructions.
This enables a user without progamming experience to design DNA assembly
protocols on a user-friendly
canvas, [DeviceEditor](https://j5.jbei.org/DeviceEditor_manual/index.html),
and then convert the design using J5 and subsequently DNAda into a series
of instructions that can be executed on a liquid handler.

## CLI Installation

Note, it is highly recommended to use a virtual environment to install the dependencies.

For example,

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh
source ~/mambaforge/bin/activate
mamba create -y -n dnada
conda activate dnada
mamba install -y python==3.11
```

```bash
pip install dnada
```

Alternatively, setup from the source code by running

```bash
git clone https://github.com/JBEI/dnada.git
cd dnada/backend/app
python setup.py install
```

Note, there is [currently a bug](https://github.com/autoprotocol/autoprotocol-python/pull/396)
in autoprotocol-python. To temporarily resolve this bug until it gets patched, identify the
location of the autoprotocol library identified in your virtual environment and apply the
fix-oligosynthesizeolig-serialization.patch file. For example,

```bash
cd ~/mambaforge/envs/dnada/lib/python3.11/site-packages/
patch -p1 < ~/dnada/backend/app/fix-oligosynthesizeoligo-serialization.patch
```

## Quick Start

There is a sample J5 design file available in the `examples/` directory in the github repo.
After installing the DNAda CLI through pip or github, to run DNAda on that design file,
execute:

```bash
cd dnada/examples
dnada_cli example_j5_output.zip
```

After a few seconds you should see a new `.zip` archive generated with the
name `automation_instructions.zip`.
