import pytest
from pytest_mysql import factories
from contextlib import contextmanager
from neo4j import GraphDatabase
from pytest_mysql.executor_noop import NoopMySQLExecutor
from traits.implementation import TraitsUtility

# Default configurations
from public.traits.interface import BASE_USER_NAME, BASE_USER_PASS, ADMIN_USER_NAME, ADMIN_USER_PASS

################################################################################
# MariaDB fixtures
################################################################################

@pytest.fixture(scope="session")
def mariadb_host(request):
    """
    Return the HOST parameter to connect to a MariaDB. By default returns localhost's IP
    """
    return request.config.getoption("--mysql-host") if request.config.getoption("--mysql-host") is not None else "127.0.0.1"

@pytest.fixture(scope="session")
def mariadb_port(request):
    """
    Return the PORT parameter to connect to a MariaDB. By default returns 3306
    """
    return request.config.getoption("--mysql-port") if request.config.getoption("--mysql-port") is not None else 3306


@pytest.fixture(scope="session")
def root_mariadb_in_docker(mariadb_host, mariadb_port):
    """
    Return a Dummy executor needed to spin off the database using pytest_mysql import factories
    """
    mysql_executor = NoopMySQLExecutor(
            user="root",
            host=mariadb_host,
            port=int(mariadb_port),
        )

    with mysql_executor:
            yield mysql_executor

# This creates also a db named test... If I am not mistaked, this is deleted after each test execution
root_connection = factories.mysql("root_mariadb_in_docker", passwd="root-pass")

@pytest.fixture
def mariadb_database():
    """
    Return the name of the test database
    """
    return "test"


@pytest.fixture
def mariadb(root_connection):
    """
    This fixture creates a Maria DB called "test" and initializes it with the YOUR code inside the
    TraitsUtility.generate_sql_initialization_code. This code should create the tables and the users (traits and admin)
    with the right permissions
    """

    cur = root_connection.cursor()
    cur.execute("BEGIN;")
    for sql_statement in TraitsUtility.generate_sql_initialization_code():
        cur.execute(sql_statement)
    cur.execute("COMMIT;")

    yield root_connection


@pytest.fixture
def connection_factory(mariadb, mariadb_host, mariadb_port, mariadb_database):
    """ 
    This code retuns an object that can create connections to a database given user and password
    """
    @contextmanager
    def _gen_connection(user, password):
        """ Generate a connection to the database """
        import mysql.connector
        from mysql.connector import Error

        assert user != "root", "Do not create connections to the db using Root!"

        # Try to create the connection, if succeeded eventually close it
        connection = mysql.connector.connect(host=mariadb_host,
                                             database=mariadb_database,
                                             user=user,
                                             port=mariadb_port,
                                             password=password)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                # print("Connected to MariaDB Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                # print("You're connected to database: ", record)

                yield connection

        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    yield _gen_connection


@pytest.fixture
def rdbms_connection(connection_factory):
    with connection_factory(BASE_USER_NAME, BASE_USER_PASS) as connection:
       yield connection

@pytest.fixture
def rdbms_admin_connection(connection_factory):
    with connection_factory(ADMIN_USER_NAME, ADMIN_USER_PASS) as connection:
       yield connection
       
################################################################################
# Neo4J fixtures
################################################################################
def pytest_addoption(parser):
    """ 
    Register the additional options to make Neo4j Fixtures work also on GitHub Actions
    """
    try:
        parser.addoption(
            '--neo4j-web-port', action='store', default="", help='Web Port to connect to Neo4j'
        )
        parser.addoption(
            '--neo4j-bolt-port', action='store', default="", help='Bolt Port to connect to Neo4j'
        )
        parser.addoption(
            '--neo4j-host', action='store', default="localhost", help='Bolt Port to connect to Neo4j'
        )
    except Exception:
        pass



@pytest.fixture
def neo4j_db_port(request):
    return request.config.getoption("--neo4j-bolt-port")


@pytest.fixture
def neo4j_db_host(request):
	return request.config.getoption("--neo4j-host")


@pytest.fixture
def neo4j_db(neo4j_db_host, neo4j_db_port):
    """
    This fixture connects to a running neo4j database
    :param neo4j_db_host:
    :param neo4j_db_port:
    :return:
    """
    URI = f"neo4j://{neo4j_db_host}:{neo4j_db_port}"

    # Create/Connect to a Database
    with GraphDatabase.driver(URI) as driver:
        driver.verify_connectivity()

        # The community version of Neo4j supports only one database, so we need to remove
        # all the nodes/links before and after each test
        records, summary, keys = driver.execute_query("MATCH (a) DETACH DELETE a")

        yield driver

        records, summary, keys = driver.execute_query("MATCH (a) DETACH DELETE a")
