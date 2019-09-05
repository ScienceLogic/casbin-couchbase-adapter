"""Adapter: Casbin Couchbase Adapter
   TODO:
    * Logging
"""
from casbin import persist
from couchbase.cluster import Cluster, PasswordAuthenticator
from couchbase.n1ql import N1QLQuery


class CasbinRule:
    id = 'casbin_rule'
    ptype = ''
    values = []

    def __init__(self, ptype: str, values: list):
        self.id = '%s_%s' % (self.id, '_'.join(values))
        self.ptype = ptype
        self.values = values

    def __str__(self):
        return '%s, %s' % (self.ptype, ', '.join(self.values))

    def __dict__(self):
        return {
            'ptype': self.ptype,
            'values': self.values
        }

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))


class Adapter(persist.Adapter):
    """the interface for Casbin adapters."""

    def __init__(self, host, bucket, user, passwd):
        self._cluster = Cluster(host)
        authenticator = PasswordAuthenticator(
            user,
            passwd
        )
        self._cluster.authenticate(authenticator)
        self._bucket_name = bucket
        self._bucket = self._cluster.open_bucket(bucket)

    def load_policy(self, model):
        """loads all policy rules from the storage."""
        lines = self._cluster.n1ql_query(
            N1QLQuery(
                r'SELECT meta().id, ptype, `values` FROM %s WHERE meta().id LIKE "casbin_rule%%"' % self._bucket_name
            )
        )
        for line in lines:
            rule = CasbinRule(ptype=line['ptype'], values=line['values'])
            persist.load_policy_line(
                str(rule), model
            )

    def _save_policy_line(self, ptype, rule):
        line = CasbinRule(ptype=ptype, values=rule)
        line.values = rule
        # TODO: add try block
        #self._bucket.mutate_in(line.id, subdocument.upsert(line.__dict__()))
        self._bucket.upsert(line.id, line.__dict__())

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
        try:
            self._bucket.remove(
                '%s_%s' % ('casbin_rule', '_'.join(rule))
            )
        except Exception:
            return False
        else:
            return True

    def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        pass

