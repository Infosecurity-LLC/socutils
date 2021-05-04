from setuptools import setup, find_packages
import os.path

current_dir = os.path.abspath(os.path.dirname(__file__))
# with open(os.path.join(current_dir, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='socutils',
    version='1.5.10',
    description='SOC services utilities',
    # long_description=long_description,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='SOC services utils',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['tests']),
    #   py_modules=["my_module"],

    install_requires=['requests', 'pyyaml', 'jinja2', 'raven', 'bson'],
)
