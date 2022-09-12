import sys
import os
import pkg_resources

requirements = ["numpy", "pillow", "pygame"]
installed_packages = [d.project_name.lower() for d in pkg_resources.working_set]


def install(package_name):
    if sys.version_info[0] < 3:
        os.system('py -2 get-pip.py')
        os.system(f'py -2 -m pip install {package_name}')
    else:
        os.system('py -3 get-pip.py')
        os.system(f'py -3 -m pip install {package_name}')

for requirement in requirements:
    if requirement in installed_packages:
        continue
    install(requirement)


