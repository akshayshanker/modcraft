from setuptools import setup, find_packages

setup(
    name="circuitcraft",
    version="0.2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    description="A framework for computational graphs focused on economic modeling",
    author="CircuitCraft Team",
    author_email="info@circuitcraft.org",
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