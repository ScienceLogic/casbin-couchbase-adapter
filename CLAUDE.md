# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A [PyCasbin](https://github.com/casbin/pycasbin) storage adapter that persists policy rules to Couchbase.

## Dev Setup

```bash
pip install -r dev_requirements.txt -r requirements.txt
pip install -e .
pre-commit install
```

## Running Tests

Tests require a live Couchbase instance:
- URL: `couchbase://localhost` (port 8091)
- Bucket: `content`
- Credentials: `isadmin` / `isadmin`

```bash
pytest tests/                          # all tests
pytest tests/test_adapter.py::test_str # single test
pytest --cov=casbin_couchbase_adapter tests/  # with coverage
```

Before tests will pass, the N1QL index must exist in the Couchbase bucket:
```sql
CREATE INDEX idx_casbin ON content(meta().id, ptype) WHERE meta().id LIKE "casbin_rule%"
```

Pre-commit hooks run `black`, `flake8`, and `pytest` on commit/push.

## Architecture

Two classes in `casbin_couchbase_adapter/adapter.py`:

**`CasbinRule`** — document model. The document key is `casbin_rule_<sha256 of underscore-joined values>`. The `__dict__()` method returns the Couchbase-stored shape: `{"ptype": ..., "values": [...]}`.

**`Adapter`** — implements `casbin.persist.Adapter`. Key behaviors:
- `load_policy`: N1QL query with `REQUEST_PLUS` scan consistency; retries on `HTTPException` (up to 10×)
- `save_policy` / `add_policy`: upserts via `bucket.upsert(key, doc)`; retries on `TransactionException` by refreshing the bucket connection
- `remove_policy`: removes by the deterministic document key
- `remove_filtered_policy`: **not implemented** (stub, returns `None`)
- Connection to Couchbase is lazy for the bucket (cached in `_bucket`); the `Cluster` object is created at init with retry on `UnAmbiguousTimeoutException`

## Versioning and Publishing

Version is in `setup.cfg` (`version = ...`). Use `bumpversion patch|minor|major` to bump — it updates `setup.cfg` and `.bumpversion.cfg` together. CI (`build.yml`) publishes the wheel to PyPI on every push to `master` via `twine`.
