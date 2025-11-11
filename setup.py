from setuptools import setup, find_packages

setup(
    name='metaverso-printer',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'trimesh==4.8.2',
        'numpy==2.1.3',
        'pyautogui==0.9.54',
        'pillow==11.0.0',
        'websockets==12.0',
        'requests==2.31.0',
        'pyyaml==6.0.2',
    ],
)
