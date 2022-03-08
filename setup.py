import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sdmaster',
    version='1.0.3',
    packages=setuptools.find_packages(),
    url='https://github.com/RedrumSherlock/stockdatamaster',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    author='Mike Wang',
    author_email='wml816@gmail.com',
    description='Stock Data Master',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    install_requires=["pandas", "plotly", "matplotlib", "numpy", "pytz"],
    package_dir={'sdmaster':'sdm'},
)