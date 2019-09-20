import setuptools

desc_file = "README.md"

with open(desc_file, "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="casbin_couchbase_adapter",
    version="0.1.0",
    author='Jesse Cooper',
    author_email='jesse.cooper@sciencelogic.com',
    description="Couchbase Adapter for PyCasbin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["casbin", "Couchbase", "casbin-adapter", "rbac", "access control", "abac", "acl", "permission"],
    packages=setuptools.find_packages(),
    install_requires=['casbin>=0.2', 'couchbase'],
    python_requires=">=3.5",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    data_files=[desc_file],
)
