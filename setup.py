import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="molybdenum", # name available on pypi.org
    version="0.0.1",
    author="Marc Exposit",
    author_email="author@example.com",
    license="MIT License",
    description="Model builder for systems biology",
    long_description=long_description, # this goes directly from the readme file
    long_description_content_type="text/markdown",
    url="https://github.com/mexposit/molybdenum/tree/main/molybdenum",
    project_urls={
        "Code": "https://github.com/mexposit/molybdenum/tree/main/molybdenum",
        "Webapp": "https://telmb.herokuapp.com/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    # packages=["molybdenum"]
    packages=setuptools.find_packages(), #discover molybdenum and subpackages in molybdenum folder
    # package_dir={"": "."}, # root package is current package so that it finds molybdenum package
    # package_data={"": ["*.pkl", "*.csv", "*.npy"]}, # if any package contains csv, npy, or pkl files include them
    # include_package_data=True, # include data specified in MANIFEST.in
    # package_data={
    #     'molybdenum': ['models/*'],
    #     'molybdenum.unirep': ['weight_files/*']
    #     },
    python_requires="==3.7", # pickle version used requires >3.8
    install_requires=['pandas','numpy'] # you can also specify version numbers here
)
