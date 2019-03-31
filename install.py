import pip
import subprocess

ui_packages = [
            ('PyQt5', 'pipenv', 'pyqt5'),
            ('Qt.py', 'git', 'https://github.com/mottosso/Qt.py'),
            ]

testing_packages = [
            ('Termgraph', 'pipenv', 'termgraph'),
            ('Loguru', 'pipenv', 'loguru'),
            ('PyTest', 'pipenv', 'pytest'),
            ]

documenation_packages = [
            ('Sphinx', 'pipenv', 'Sphinx'),
            ]

refactoring_packages = [
            ('QtPyConvert', 'git', 'https://github.com/digitaldomain/QtPyConvert'),
            ('Black', 'pipenv', 'black'),
            ('Bowler', 'pipenv', 'bowler'),
            ]

# https://stackoverflow.com/questions/12332975/installing-python-module-within-code
def install(package, args):
    arguments = ['install', package]
    arguments.extend(args)
    if hasattr(pip, 'main'):
        pip.main(arguments)
    else:
        pip._internal.main(arguments)

install('pipenv', ['--user'])

for package in ui_packages:
    #install packages
    import subprocess
    print("Installing: " + package[0])
    if package[1] == 'pipenv':
        subprocess.run([package[1], 'install', package[2]])
    elif package[1] == 'git':
        subprocess.run([package[1], 'clone', package[2]])
    else:
        print('Unexpected installation method:' + package[1])
