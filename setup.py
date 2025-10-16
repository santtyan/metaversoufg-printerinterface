# setup.py
from setuptools import setup, find_packages

setup(
    name='k1max-controller',
    version='1.0.0',
    description='Biblioteca controle Creality K1 Max',
    author='Yan Santos',
    author_email='leiteyan@discente.ufg.br',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.13',
    install_requires=[
        'websockets>=12.0',
        'pyyaml>=6.0',
        'pyautogui>=0.9',
        'requests>=2.31',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.13',
    ],
)