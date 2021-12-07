# import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

# setuptools.setup(
#     name="molybdenum", # name available on pypi.org
#     version="0.0.1",
#     author="Marc Exposit",
#     author_email="author@example.com",
#     license="MIT License",
#     description="Model builder for systems biology",
#     long_description=long_description, # this goes directly from the readme file
#     long_description_content_type="text/markdown",
#     url="https://github.com/Lean-Mean-Protein-Machine-Learning/LMPM/tree/main/lmpm",
#     project_urls={
#         "Code": "https://github.com/Lean-Mean-Protein-Machine-Learning/LMPM/tree/main/lmpm",
#         "Webapp": "https://lmpm.herokuapp.com/",
#     },
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.7",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#         "Intended Audience :: Science/Research",
#     ],
#     # packages=["lmpm", "lmpm/unirep"]
#     packages=setuptools.find_packages(), #discover lmpm and subpackages in lmpm folder
#     # package_dir={"": "."}, # root package is current package so that it finds lmpm package
#     # package_data={"": ["*.pkl", "*.csv", "*.npy"]}, # if any package contains csv, npy, or pkl files include them
#     # include_package_data=True, # include data specified in MANIFEST.in
#     package_data={
#         'lmpm': ['models/*'],
#         'lmpm.unirep': ['weight_files/*']
#         },
#     python_requires=">=3.8", # pickle version used requires >3.8
#     install_requires=['pandas','numpy'] # you can also specify version numbers here
# )