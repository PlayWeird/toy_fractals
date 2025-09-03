from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fractal-explorer",
    version="0.1.0",
    author="Fractal Explorer Team",
    description="Interactive multi-fractal visualization framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fractal-explorer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "numba>=0.56.0",
        "matplotlib>=3.5.0",
        "pillow>=9.0.0",
        "scipy>=1.7.0",
        "PyQt5>=5.15.0",
        "pyqtgraph>=0.12.0",
        "colorcet>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fractal-explorer=fractal_explorer.main:main",
        ],
    },
)