from setuptools import setup, find_packages

setup(
    name='namespaxe',
    version='0.1.2',
    author='Gabriel Nzilantuzu',
    author_email='gabrielnzilantuzu@pyincorporation.com',
    description='A command-line tool for interacting with cloud services.',
    long_description=open('../README.md').read(),
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
