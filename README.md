# DBST2VO SS24 Assignment Description

This is the Public Repository for the Assignment of the DBST2VO  2024 Class.

### TL;DR:

To pass the assignment, you need the following:

1. A working solution that **passes all the public tests** and **passes all your personal tests**

    >> NOTE: Failing to pass all the public and personal tests will result in a strong penalty (50/100) even if your solution passes **some** tests and implements the right functionalities.

2. A succinct description of your solution containing a **motivation** for each major design decision. Examples include but are not limited to:
    - *Where did you use NoSQL/SQL and why?*
    - *What is the schema of your Relational DB? How did you obtain it?*
    - *How did you approach the solution?*
    - *How did you approach validating your solution?*

    >> NOTE: The summary description is **NOT** a list of detailed comments on your code. If you start writing down an explanation of what each single line does, you are not moving in the right direction.

3. Your "personal tests" should cover all the Python methods that must be implemented. There's a penalty for each method that is **not** covered by your tests, so use `pycov` (and set up the GitHub actions) to check this aspect. Additionally, your tests must include at least one `assert` statement to be considered valid.

    >> Note: the more you test, the less likely the "grading (private) tests" will fail. And you cannot use public tests as private tests, nor consider public tests in your coverage report!
    
## Repo Structure

This (public) repository has the following structure:

```
.
├── README.md
├── requirements.txt
├── tests
│   ├── __init__.py
│   └── test_public_tests.py
└── traits
    ├── __init__.py
    └── interface.py

```

- `README.md`: this file
- `requirements.txt`: the file containing all and only the libraries you need to complete the task
- `tests`: contains the public tests
- `traits`: contain the abstract class to implement


> **NOTE** The content of this repository may change as a result of in-class discussion or the definition of new public test cases. For instance, new files inside the `tests` folder might be added, or their content might change anytime.
**It is your responsibility to ensure you always check out the latest version of this repository from GitHub.**

## Task Description

You must develop the backend system of a ticket reservation system called TRAITS, which stands for TRAIn Ticketing Service.
TRAITS allows its users to see train schedules, train connections, train status, buy train tickets, and reserve sits. Additionally, new users can be registered, new trains added to their schedule, existing schedules can be updated, and more (see below).

The backend system is the combination of two sub-systems that must interoperate via some Python code:

- A relational database (RDBMS) for transactional operations  to be implemented using `mariadb`

- A graph database (NoSQL) for other operations implemented using `neo4j`

It is your job to decide what information to store in which database, how to keep them synchronized, and how to orchestrate their operations.

For portability reasons, those components and the Python logic that coordinates them must be run in docker containers. Make sure you deploy each component into a separate docker container.

### Prerequisites
The following list defines the prerequisites for completing the assignment

- Docker
- Python 3.10
- MariaDB 10.6
- Neo4j 5.9.0

Additional Python libraries (to be installed with `pip`) are listed in the `requirements.txt` file.


## Main Features

TRAITS must implement three features used by guest users, registered users, and admin users. 

### Basic Features

All users can access the following basic features:

#### Search Train Connections (between two stations)
Return the connections from starting and ending stations, possibly including changes at interchanging stations. 

The search must be parametrized `travel time`, a `sorting criteria`, and the result can be `limited to a predefined number of connections`.

Travel time is a day of the year (use `day`, `month`, and `year`) and a time (use `hour` and `minute`) in 24h format.
Travel time can be either a departure or arrival time. Specifying a departure time ensures that the trip cannot start before the given time, whereas specifying an arrival time ensures that the trip cannot end after the given time.
By default, i.e., when not explicitly specified, travel time is `departure` and `now`.

Sorting criteria can be one (and only one) of the following:`overall travel time (ott)`, number of train changes (nc)`, `waiting time (wt)`, and `estimated price (ep)`. 

The overall travel time is the time from the beginning of the trip to its very end.

The number of train changes is the count of how many times the user must change the train during the trip.

The waiting time is the time the user spends waiting for a train, including the time spent waiting for the first train.

The estimated price is the overall (fixed) cost of the travel, which depends on the travel distance/time (`travel_price = travel time / 2`), and the (variable) cost for seat reservation, which depends on how many seats should be reserved (`reservation_price=number of trains * 2`).

For example, if the user travels with Train 1 from A to B to C and then boards Train 2 to reach D, the estimated price for the ticket plus reservations is:
- ```travel_price = [ tt(A,B) + tt(B,C) + tt(C,D) ] / 2```, where tt is the travel time from two stations (without counting the waiting time at each station or any delay)
- ```reservation_price = 2 * 2```

> Note: the actual price might be different if some seats cannot be reserved due to high demand

Sorting can be `ascending` or `descending`.
By default, i.e., when not explicitly specified, the sorting criteria is `overall travel time ascending` (so, the system must report the fastest connections first).

If starting or ending stations do not exist, or no connection between them is possible, the system must return an empty result.

In case the starting or ending stations are the same, the system must return a `ValueError.`

#### Check the status of a train
The user should be able to check the status of a train/connection: is the train operational? Is delayed? Etc.

### Advanced Features

Registered and only registered users can access the following advanced features:

#### Book Tickets and Reserve Seats
Given a train connection instance (e.g., on a given date/time), registered users can book tickets and optionally reserve seats. When the user decides to reserve seats, the system will try to reserve all the available seats automatically.

We make the following assumptions: 

- there is always a place on the trains so that tickets can always be bought
- the train seats are not numbered, so the system must handle only the number of passengers booked on a train and not each single seat
- The system grants only those seats that are effectively available at the moment of request; thus, overbooking on reserved seats is **not** possible
- Seats reservation **cannot** be done after booking a ticket
- A user can only reserve one seat on each train at the given time
- You do not have to implement a method to cancel reservations or provide a refund
 
#### Access Purchase History

Registered users can list the history of their past purchases, including the starting and ending stations, the day/time, total price, and **for each connection**, the price, and whether they reserved a seat.

The purchase history is always represented in descending starting time (at the top, the most recent trips).

### Admin Features:

Admin and only admin users can access the following special features:

#### TRAITS User Management
Admin can add/delete users. 

Users are identified by their (unique) email address and might have other attributes.

- Invalid addresses are not allowed (must raise a `ValueError`)
    >> NOTE: Check the validity of the email in the Database, not in Python!

- Duplicated addresses are not allowed (must raise a `ValueError`)

To follow GDPR, all the data about deleted users must also be deleted, including all the seat reservations (seats might become free). If the user does not exist, no exception is raised!

#### Train station management
Admin users can add and connect train stations and specify how long trains will travel between them.

Train stations cannot be duplicated (raise ValueError).
Any train station can be connected with any other train station except itself (so travel time cannot be zero!).
The same two train stations cannot be directly connected more than once.

As long as train stations are connected, trains can travel between them in any direction.  

Travel times must be at least one minute and cannot be more than one hour (raise ValueError otherwise).

We assume that 
- between connected stations, there are as many tracks as needed, so trains can travel freely (no need to check if at a given time the tracks are occupied by another train)
- any station has as many platforms as necessary (size does not matter)

#### Add/update/remove trains
Admin can add, update, or delete trains.

Updating a train can change their size (how many seats are available) and their status. The modification of the train has an immediate effect, but we assume that a train capacity cannot be reduced.

Admin can only toggle train status, i.e., trains can only be operational or nonoperational. When a train changes its status, its schedule(s) are affected.

Deleting a train should ensure consistency!
(Future) reservations are canceled, schedules/trips are canceled, etc. However, deleting a train must not change the purchase history of users.

#### Train Scheduling
Admin users can also add train schedules. A train schedule associates a train with a list of stations (stops) and their estimated waiting time (the train must stop at that station for the given time).

We assume that a train is never delayed, but it can be non-operational for some time (max three hours in a day). If a train is non-operational, its current and future schedules (on the same day) must be updated by adding a delay.

The delay is computed as the difference between when the train became non-operational and "now". The delay is rounded to the (next) minute.

We assume that:

- schedules are daily (all the weekdays are the same)
- schedules have validity (from a starting day to an ending day)
- at the end of each day, any problem is (automatically) resolved; thus, no delay affects the schedules of the next days

Scheduling trains must be physically feasible and follow these ground rules:

- A train cannot be in two places at the same time!
- A train cannot teleport:
    - trains cannot travel faster than the tracks/link allow/s
    - trains can travel only by passing by directly connected stations
    - trains always stop at all stations, i.e., they cannot pass through a station without stopping
    - A train stopping in one station cannot restart from another one

- A train must stop at the end station(s) for at least 10 minutes before resuming operations (e.g., waiting time cannot be less than 10 minutes there)
- To allow night operations, the train's last stop in a day must be at least six hours before the first start of the train the next day. Consequently, a schedule must always end on the same day it is started

> NOTE: schedules are affected by train availability: if a train is deleted, the schedule is impossible. 

## Utility methods

Utility methods must be implemented in the `TraitsUtils` class under the `implementation` module.
This class must extend the given interface class; however, you can implement in that class also any additional or utility method that you need for testing. For instance, methods that check seat availability (e.g., on a train, along a given connection), view trains' schedule on a day, check train statuses (some trains might be delayed or canceled), CRUD operations on the various entities (users, trains, stations) and more. 



The implementation of those methods must follow the general guidelines of the assignment: limit the use of Python as much as possible and rely on the functionalities provided by the databases as much as you can.

## Testing

We use `pytest` to test the solution. Test methods must be placed inside the `tests` folder in your project. Additional tests are located inside the `public/tests` folder. All the tests depend on MariaDB and Neo4J, since connections to those databases are required to instantiate both `Traits` and `UtilityTraits`.

The following setup is viable (but not the only one!):

Start MariaDB in docker. Be sure you set the root password as shown and open the network port:

```bash 
docker run --name mariadbtest -e MYSQL_ROOT_PASSWORD=root-pass -p 3306:3306 -d mariadb:10.6
```

Start Neo4J in docker. Be sure you set the network ports as shown and disable authentication:

```bash 
docker run -d --publish=7474:7474 --publish=7687:7687 --env NEO4J_AUTH=none neo4j:5.9.0
```

Wait a few seconds so the databases complete the startup.

Execute the tests by running the following command from the root of your project:

```python
pytest
```

Initially, all the tests will not pass; that's fine. Implement step by step your solution and keep testing.


## Hints

1. The methods to implement are listed in the given code; however, some of their parameters may be underspecified (i.e., using `**kwargs`) to allow some flexibility in the implementation. 

    >> Note: In case of problems, write a message on Teams and open an issue on the *public* repository so anyone can contribute and track it.

2. To complete this assignment, you can use any of the following concepts:

    - non-root users definition with specific permissions granted;
    - simple and nested transactions for reading, creating, updating, and deleting elements from the database;
    - queries that make use of grouping and sorting; 
    - transactions with the right isolation level(s);
    - consistency checks and references (cascade, etc.)
    - views;
    - database triggers;

    >> NOTE: Performance is **not** a quality we are looking for; correctness is! So, do not waste precious time trying to optimize your queries to minimize execution time.

3. The expected project structure is:

    ```
...
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_personal.py
├── traits
│   ├── __init__.py
│   └── implementation.py
...
```

4. The content of the `implementation.py` module looks more or less like this:

```python 
# Import all the necessary classes from the public submodule:
from public.traits.interface import TraitsInterface, TraitsUtilityInterface, TraitsKey, TrainStatus, SortingCriteria

# Import all the necessary default configurations
from public.traits.interface import BASE_USER_NAME, BASE_USER_PASS, ADMIN_USER_NAME, ADMIN_USER_PASS

# Implement the utility class. Add any additional method that you need
class TraitsUtility(TraitsUtilityInterface):
    
    def __init__(self, rdbms_connection, rdbms_admin_connection, neo4j_driver) -> None:
        self.rdbms_connection = rdbms_connection
        self.rdbms_admin_connection = rdbms_admin_connection
        self.neo4j_driver = neo4j_driver

    @staticmethod
    def generate_sql_initialization_code() -> List[str]:
        # Note: this code ensures that users are recreated as needed. You need to add the proper permissions. Also add here the statements to setup the database.
        return [
            f"DROP USER IF EXISTS '{ADMIN_USER_NAME}'@'%';"
            f"DROP USER IF EXISTS '{BASE_USER_NAME}'@'%';"
            f"CREATE USER '{ADMIN_USER_NAME}'@'%' IDENTIFIED BY '{ADMIN_USER_PASS}';",
            f"CREATE USER '{BASE_USER_NAME}'@'%' IDENTIFIED BY '{BASE_USER_PASS}';",
        ]

    
# Implement the main class that you need to implement
class Traits(TraitsInterface):

    def __init__(self, rdbms_connection, rdbms_admin_connection, neo4j_driver) -> None:
        self.rdbms_connection = rdbms_connection
        self.rdbms_admin_connection = rdbms_admin_connection
        self.neo4j_driver = neo4j_driver

    ```