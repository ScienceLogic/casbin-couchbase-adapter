from codecs import open
from os import path
from setuptools import setup, find_packages

desc_file = "README.md"

here = path.abspath(path.dirname(__file__))
# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x and '#' not in x and '--' != x[:2:]]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

with open(desc_file, "r") as fh:
    long_description = fh.read()

setup(
    name="casbin_couchbase_adapter",
    version="0.1.4",
    author='ScienceLogic',
    url="https://github.com/ScienceLogic/casbin-couchbase-adapter",
    description="Couchbase Adapter for PyCasbin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["casbin", "Couchbase", "casbin-adapter", "rbac", "access control", "abac", "acl", "permission"],
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.5",
    license="Apache2",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    data_files=[desc_file],
)
