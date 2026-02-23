import os
import time
import csv
import pytest
import casbin
from casbin_couchbase_adapter import Adapter
from casbin_couchbase_adapter import CasbinRule


@pytest.fixture
def adapter_fixture():
    # by default 8091 PORT is used
    yield Adapter("couchbase://localhost", "content", "isadmin", "isadmin")


@pytest.fixture
def enforcer_fixture(adapter_fixture):
    with open(
        os.path.split(os.path.realpath(__file__))[0] + "/rbac_policy.csv"
    ) as file:
        csv_reader = csv.reader(file, delimiter=",")
        for line in csv_reader:
            record = CasbinRule(ptype=line[0], values=line[1::])
            cluster = adapter_fixture._cluster
            bucket = adapter_fixture.get_bucket()
            bucket.upsert(record.id, record.__dict__())
    time.sleep(1)

    yield casbin.Enforcer(
        os.path.split(os.path.realpath(__file__))[0] + "/rbac_model.conf",
        adapter_fixture,
    )

    # remove rules
    query = cluster.query(
        'DELETE FROM content WHERE meta().id LIKE "casbin_rule%"'
    )
    query.execute()
    time.sleep(1)


@pytest.mark.parametrize(
    "args,result",
    [
        (("alice", "data1", "read"), True),
        (("alice", "data2", "read"), True),
        (("alice", "data2", "write"), True),
        (("bob", "data2", "write"), True),
        (("bob", "data1", "read"), False),
    ],
)
def test_enforcer_basic(enforcer_fixture, args, result):
    e = enforcer_fixture

    assert e.enforce(*args) is result


def test_add_policy(enforcer_fixture):
    e = enforcer_fixture

    assert e.enforce("eve", "data3", "read") is False
    assert e.add_permission_for_user("eve", "data3", "read")
    assert e.enforce("eve", "data3", "read")


def test_save_policy(enforcer_fixture):
    e = enforcer_fixture
    assert e.enforce("alice", "data4", "read") is False

    model = e.get_model()
    model.clear_policy()

    model.add_policy("p", "p", ["alice", "data4", "read"])

    adapter = e.get_adapter()
    adapter.save_policy(model)
    assert e.enforce("alice", "data4", "read")


def test_remove_policy(enforcer_fixture):
    e = enforcer_fixture
    assert e.enforce("alice", "data5", "read") is False
    e.add_permission_for_user("alice", "data5", "read")
    assert e.enforce("alice", "data5", "read")
    assert e.delete_permission_for_user("alice", "data5", "read")
    assert e.enforce("alice", "data5", "read") is False


def test_str():
    rule = CasbinRule(ptype="p", values=["alice", "data1", "read"])
    assert str(rule) == "p, alice, data1, read"


def test_repr():
    rule = CasbinRule(ptype="p", values=["alice", "data1", "read"])
    assert (
        repr(rule)
        == '<CasbinRule casbin_rule_46ab8754f52a0eb6707cdd15df72b1d409dfdeaa40e7342c1713e7582f3e7dd4: "p, alice, data1, read">'
    )


def test_dict():
    rule = CasbinRule(ptype="p", values=["alice", "data1", "read"])
    assert rule.__dict__() == {"ptype": "p", "values": ["alice", "data1", "read"]}

@pytest.mark.parametrize(
    "owner_name, role",
    [
        ("Alice, LastName", "data2_admin"),
        ("Test\team", "data2_admin"),
        ("Test\deam", "data2_admin"),
        ("Alice<LastName,attribute", "data2_admin"),
        ("12335478.?;,", "data2_admin"),
    ],
    ids=[
        "owner_name with comma",
        "invalid",
        "with slashes",
        "with < and comma",
        "numbers and especial characters",
    ],
)
def test_save_remove_policy_with_commas(enforcer_fixture, owner_name, role):
    e = enforcer_fixture
    assert e.enforce(owner_name, "data4", "read") is False

    # save
    e.add_policy(role, "data4", "read")
    e.add_grouping_policy(owner_name, role)
    adapter = e.get_adapter()
    adapter.save_policy(e.get_model())
    assert e.enforce(owner_name, "data4", "read") is True

    #remove
    assert adapter.remove_policy("g","g",[owner_name, role])
    assert e.delete_permission_for_user(role, "data4", "read")
    adapter.save_policy(e.get_model())
    assert e.enforce(owner_name, "data4", "read") is False
