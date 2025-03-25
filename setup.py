from setuptools import setup, find_packages

setup(
    name="circuitcraft",
    version="1.3.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    description="CircuitCraft: A lightweight framework for economic models with backward/forward solving",
    author="Akshay Shanker",
    author_email="",
    python_requires=">=3.8",
    install_requires=[
        "networkx>=2.6.0",
        "numpy>=1.20.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
) 