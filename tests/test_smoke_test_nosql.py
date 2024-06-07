# This module contains exemplary test cases to connect to the local neo4j database, insert new nodes, etc.

def test_neo4j_is_empty(neo4j_db):
    records, summary, keys = neo4j_db.execute_query(
        "MATCH (x) RETURN x"
    )
    assert len(records) == 0


def test_neo4j(neo4j_db):
    records, summary, keys = neo4j_db.execute_query(
        "MATCH (x) RETURN x"
    )
    assert len(records) == 0
    # Insert Some Nodes and Connections
    neo4j_db.execute_query(
        "CREATE (u:User {username: $username})",
        username = "Alice",
    )
    neo4j_db.execute_query(
        "CREATE (u:User { username: $username})",
        username="Bob",
    )
    records, summary, keys = neo4j_db.execute_query(
        "MATCH (x) RETURN x"
    )
    assert len(records) == 2
