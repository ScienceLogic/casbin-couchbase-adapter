"""Adapter: Casbin Couchbase Adapter
   TODO:
    * Logging
    * Add retry
"""
import logging
from hashlib import sha256
from retry import retry
from casbin import persist
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.n1ql import QueryScanConsistency
from couchbase.exceptions import (
    CouchbaseException,
    TransactionException,
    HTTPException,
    RequestCanceledException,
    UnAmbiguousTimeoutException
)


class CasbinPoliciesNotFound(Exception):
    pass


class CasbinRule:
    id = "casbin_rule"
    ptype = ""
    values = []

    def __init__(self, ptype: str, values: list):
        self.id = "%s_%s" % (self.id, sha256("_".join(values).encode()).hexdigest())
        self.ptype = ptype
        self.values = values

    def __str__(self):
        return "%s, %s" % (self.ptype, ", ".join(self.values))

    def __dict__(self):
        return {"ptype": self.ptype, "values": self.values}

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))


class Adapter(persist.Adapter):
    """the interface for Casbin adapters."""

    __bucket = None

    def __init__(self, host, bucket, user, passwd):
        self.logger = logging.getLogger()
        self._cluster = self.initialize_db_connection(host, user, passwd)
        self._bucket_name = bucket

    @retry(UnAmbiguousTimeoutException, tries=3, delay=1, backoff=1, max_delay=3)
    def initialize_db_connection(self, host, user, passwd):
        # by default 8091 PORT is used
        cluster = Cluster(host,
                          ClusterOptions(PasswordAuthenticator(user, passwd))
                          )
        return cluster

    @property
    def _bucket(self):
        return self.__bucket

    @_bucket.setter
    def _bucket(self, conn):
        self.__bucket = conn

    def get_bucket(self, refresh_conn=False):
        if self._bucket and not refresh_conn:
            return self._bucket
        else:
            self._bucket = self._cluster.bucket(self._bucket_name).default_collection()
            return self._bucket

    @retry(HTTPException, tries=10, delay=1, backoff=1, max_delay=5)
    def load_policy(self, model):
        """loads all policy rules from the storage."""
        query = (
            r"SELECT meta().id, ptype, `values` FROM %s WHERE meta().id "
            r'LIKE "casbin_rule%%"' % self._bucket_name
        )
        query_opts = QueryOptions(scan_consistency=QueryScanConsistency.REQUEST_PLUS)
        try:
            for line in self._cluster.query(query, query_opts):
                try:
                    rule = CasbinRule(ptype=line["ptype"], values=line["values"])
                except KeyError as err:
                    self.logger.error(
                        "skipping policy: %s not formatted properly and has no: %s"
                        % (line["id"], err)
                    )
                    continue
                else:
                    persist.load_policy_line(str(rule), model)
        except (CouchbaseException, TransactionException):
            # refresh stale connection
            for line in self._cluster.query(query, query_opts):
                try:
                    rule = CasbinRule(ptype=line["ptype"], values=line["values"])
                except KeyError as err:
                    self.logger.error(
                        "skipping policy: %s not formatted properly and has no: %s"
                        % (line["id"], err)
                    )
                    continue
                else:
                    persist.load_policy_line(str(rule), model)

    def _save_policy_line(self, ptype, rule):
        line = CasbinRule(ptype=ptype, values=rule)
        line.values = rule
        bucket = self.get_bucket()
        try:
            bucket.upsert(line.id, line.__dict__())
        except TransactionException:
            # refresh stale connection
            bucket = self.get_bucket(refresh_conn=True)
            bucket.upsert(line.id, line.__dict__())

    def save_policy(self, model):
        """saves all policy rules to the storage."""
        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    self._save_policy_line(ptype, rule)
        return True

    def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        self._save_policy_line(ptype, rule)

    def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        bucket = self.get_bucket()
        query = "%s_%s" % ("casbin_rule", sha256("_".join(rule).encode()).hexdigest())
        try:
            bucket.remove(query)
        except TransactionException:
            # refresh stale connection
            bucket = self.get_bucket(refresh_conn=True)
            bucket.remove(query)
        except Exception:
            return False
        else:
            return True

    def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        pass
