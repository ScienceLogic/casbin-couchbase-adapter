Couchbase Adapter for PyCasbin 
====

Couchbase storage adapter for PyCasbin

## Installation

```
pip install casbin_couchbase_adapter

# Create secondary index in Couchbase to support N1QL queries
CREATE INDEX idx_casbin ON content(meta().id, ptype) WHERE meta().id LIKE "casbin_rule%"
```


## Simple Example

```python
import casbin_couchbase_adapter
import casbin

adapter = casbin_couchbase_adapter.Adapter('couchbase://localhost:8091', 'bucket', 'user', 'password')

e = casbin.Enforcer('path/to/model.conf', adapter, True)

sub = "alice"  # the user that wants to access a resource.
obj = "data1"  # the resource that is going to be accessed.
act = "read"  # the operation that the user performs on the resource.

if e.enforce(sub, obj, act):
    # permit alice to read data1
    pass
else:
    # deny the request, show an error
    pass
```

## Development

1. Fork
2. Install Dev ENV
```python
# Install Flask-Casbin with Dev packages
pip install -r dev_requirements.txt
pip install -r requirements.txt
pip install -e .
# Install Pre-commits
pre-commit install
# Create feature branch
git checkout -b feature-more-cool-stuff
# Code stuff
```
Then push your changes and create a PR

#### Manually Bump Version
```
bumpversion major  # major release
or
bumpversion minor  # minor release
or
bumpversion patch  # hotfix release
```
