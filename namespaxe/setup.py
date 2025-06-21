from setuptools import setup, find_packages
import os

this_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_dir, 'README.md')

try:
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'A command-line tool for interacting with cloud services.'

setup(
    name='namespaxe',
    packages=["namespaxe"],
    version='0.1.9',
    author='Gabriel Nzilantuzu',
    author_email='gabrielnzilantuzu@pyincorporation.com',
    description='A command-line tool for interacting with cloud services.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pyincorporation-com/namespaxe-cli',
    packages=find_packages(),
    install_requires=[
        'requests',
        'click',
        'pyyaml',
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'namespaxe = namespaxe.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
