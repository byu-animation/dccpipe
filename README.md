# dccpipe
Open DCC Pipeline management tools

## Description
DCC's (Digital Content Creation tools) have similar needs in a pipeline. They typically contain a Python API, allow for custom tools/plugins, and need to interact by passing data to eachother. These similar functions have been abstracted into a suite of tools in a virtual environment which can be deployed in film, game and VFX pipelines.

We created dccpipe with the intention of being cross-platform, compatible and easy for collaboration. We are attempting to adhere to style standards we have observed in other open-source repositories, and would appreciate feedback in that regard.

## Install Instructions
Before starting, you'll need to make sure that your $PATH environment variable is set to be able to read local modules. Do this:
1. Open terminal in your home directory
2. Type:
```
vim .bashrc
```
3. Insert the following in the file:
```
export PATH=~/.local/bin:$PATH
```
4. Type Esc, followed by :wq to save the changes
5. Back in the terminal, enter the following command and proceed with the instructions below.
```
source .bashrc
```
### Basic install for developers
To install all development packages, execute the following in a bash terminal:
```
git clone https://github.com/byu-animation/dccpipe
cd dccpipe
source config/unix/fedora/install.sh --dev
```
To activate and test the virtual environment:
```
source launch/unix/env.sh
python
>>import PySide2
>>import pipe.tools
```

### Release/update in production directory
```
git clone https://github.com/byu-animation/dccpipe
cd dccpipe
source config/unix/fedora/install.sh --clean
```

### Optional Arguments
#### --dev/-d
Installs all development packages
```
source config/unix/fedora/install.sh --dev
```

#### --clean/-c
Cleans the previous installation by deleting .venv folder
```
source config/unix/fedora/install.sh --clean
```

#### --installmissing/-im
Installs missing packages with pip/yum. Note: if you are missing an rpm, you must run this as root. If you are only missing pip packages, you can run this as a normal user.
```
sudo config/unix/fedora/install.sh --installmissing
```

## Compatibility
This project was inspired by previous BYU Animation pipeline repositories, such as [BYU Animation Tools](https://github.com/byu-animation/byu-animation-tools) and [BYU Pipeline Tools](https://github.com/byu-animation/byu-pipeline-tools). Therefore, it is created with a very specific use case. However, the pipeline is built in such a way that other distros/operating systems could be supported in a future release.

### System Requirements

| Requirements    | Description                                                                         |
|:----------------|:------------------------------------------------------------------------------------|
| Fedora 27/RHEL  | The current Linux distro at BYU. (RHEL distros should be supported.)                |
| Python 2.7.5    | Most DCCs depend on Python 2.7 for the time being, so by extension, so does DCCPipe |
| pip*            | Required for pipenv                                                                 |
| pipenv*         | Virtualenv manager for python dependencies                                          |                                 
| qt-qtbase-devel*| Required for PySide2                                                                |
| libxml2-devel*  | Required for PySide2                                                                |

\* Will be automatically installed using the `--installmissing/-im` flag.

### Supported DCC's

| DCC                             | Version | Module          |
|:--------------------------------|--------:|:----------------|
| Autodesk Maya                   | 2018    | pipe.tools.maya |
| SideFX Houdini                  | 17.5    | pipe.tools.hou  |
| Foundry Nuke                    | 11.3    | pipe.tools.nuke |
| Allegorithmic Substance Painter | 2018.3  | pipe.tools.sbs  |

### Packages Managed by Pipenv
Note: All packages will be installed in the project's directory in the .venv folder.

| Pipenv Package | `--dev` only |
|:---------------|:----------:|
| [pyside2](https://pypi.org/project/PySide2/)*      | no |
| [shiboken2](https://pypi.org/project/shiboken2/)*  | no |
| [qt-py](https://github.com/mottosso/Qt.py)         | no |
| [termgraph](https://github.com/mkaz/termgraph)     | yes |
| [loguru](https://github.com/Delgan/loguru)         | yes |
| [pytest](https://github.com/pytest-dev/pytest)     | yes |
| [sphinx](https://github.com/sphinx-doc/sphinx)     | yes |

\* Due to a virtualenv limitation, pyside2 and shiboken2 will be installed to user, and then copied into the project directory. The script that handles this is `config/unix/fedora/install_pyside.sh`
