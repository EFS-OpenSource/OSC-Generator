from setuptools import setup, find_packages
import os

exec(open(os.path.join(os.path.dirname(__file__), 'osc_generator', 'version.py')).read())

# with os.path.join(os.path.dirname(__file__), 'README.md') as file_path:
file_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.isfile(file_path):
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            if line.startswith('version = {'):
                lines[idx] = 'version = {' + str(__version__) + '}\n'
        file.seek(0)
        file.writelines(lines)
        file.truncate()

# with os.path.join(os.path.dirname(__file__), 'CITATION.cff') as file_path:
file_path = os.path.join(os.path.dirname(__file__), 'CITATION.cff')
if os.path.isfile(file_path):
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            if line.startswith('version: '):
                lines[idx] = 'version: ' + str(__version__) + '}\n'
        file.seek(0)
        file.writelines(lines)
        file.truncate()

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

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    install_requires = [l.strip() for l in f.readlines()]

setup(name='osc_generator',
      version=str(__version__),
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
      python_requires='>=3.7',
      entry_points={'console_scripts': ['osc_generator=osc_generator.osc_generator:main']},
      install_requires=install_requires,
      )
