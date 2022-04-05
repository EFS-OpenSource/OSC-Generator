from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Natural Language :: English
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: GIS
Topic :: Software Development
Typing :: Stubs Only
Operating System :: Microsoft :: Windows
"""

setup(name='osc_generator',
      version='0.0.0',
      description='OSC-Generator can be used to generate ASAM OpenSCENARIO files from vehicle data and an ASAM OpenDRIVE file.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EFS-OpenSource/OSC-Generator',
      project_urls={
          "Bug Tracker": "https://github.com/EFS-OpenSource/OSC-Generator/issues",
          "Source Code": "https://github.com/EFS-OpenSource/OSC-Generator"},
      author='Axel Aigner et al.',
      author_email='axel.aigner@efs-auto.com',
      packages=find_packages(exclude=('tests',)),
      classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
      python_requires='>=3.7'
      )
