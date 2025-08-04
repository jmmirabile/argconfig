from setuptools import setup, find_packages

setup(
    name="argparse-yaml",
    version="0.1.0",
    description="Create argparse parsers from YAML configuration files",
    author="Jeff Mirabile",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=5.1",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'argparse-yaml=argparse_yaml.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
