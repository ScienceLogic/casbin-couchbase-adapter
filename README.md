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


### Getting Help

- [PyCasbin](https://github.com/casbin/pycasbin)

### License

TBD

### TODO
* logging