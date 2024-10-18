from setuptools import setup, find_packages

setup(
    name='namespaxe',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'namespaxe = namespaxe.cli:main',
        ],
    },
    description='A CLI tool for interacting with pyincorporation servers.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='pyincorporation',
    author_email='contact@pyincorporation.com',
    url='https://github.com/pyincorporation/namespaxe',
)
