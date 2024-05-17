# DBST2VO SS24 Assignment Description

This the Public Repository for the Assignment of the DBST2VO  2024 Class.

### TL;DR:

In order to pass the assignment you need:

1. A working solution that **passes all the public tests** and **passes all your personal tests**

    >> NOTE: Failing to pass all the public and personal tests will result in a strong penalty (-50/100) even if your solution pass **some** tests and implements the right functionalities.

2. A succinct description of your solution containing a **motivation** for each of your major design decisions. Examples include but are not limited to:
    - *Where did you use NoSQL/SQL and why?*
    - *What is the schema of your Relational DB? How did you obtain it?*
    - *How did you approach the solution?*
    - *How did you approach validating your solution?*

    >> NOTE: The summary description is **NOT** a list of detailed comments of your code. If you start writing down an explanation of what each single line does, your are not moving in the right direction.

3. Your personal tests should cover all the python methods that must be implemented. There's a penalty for each method that is **not** covered by your tests, so use `pycov` (and setup the GitHub actions) to check this aspect. Additionally, your tests must include at least one `assert` statement to be considered valid.

    >> Note: the more you test the less likely the "grading (private) tests" will fail. And you cannot use public tests as private tests, nor consider public tests in your coverage report!
    
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


> **NOTE** the content of this repository may change as the result of in-class discussion or the definition of new public test cases. For instance, new files inside the `tests` folder might be added or their content might change at any time.
**It is your responsibility to ensure you always check out the latest version of this repository from GitHub.**

## Task Description

You must develop the backend system of an ticket reservation system called TRAITS, which stands for TRAIn Ticketing Service.
TRAITS allows its users to see train schedules, train connections, train status, buy train tickets, and reserve sits. Additionally, new users can be registered, new trains added with their schedule, existing schedules can be updated, and more (see below).

The backend system is the combination of two sub-systems, that must interoperate via some python code:

- A relational database (RDBMS) for transactional operations  to be implemented using `mariadb`

- A graph database (NoSQL) for other operations implemented using `neo4j`

It is your job to decide what information to store in which database, how to keep them synchronized, and how to orchestrate their operations.

For portability reasons, those components as well as the python logic that coordinate them must be run in docker containers. Make sure you deploy each component into a separate docker container.

### Prerequisites
The following list defines the prerequisites for completing the assignment

- Docker
- Python 3.10
- MariaDB 10.6
- Neo4j 5.9.0

Additional python libraries (to be installed with `pip`) are listed in the `requirements.txt` file


## Main Features

TRAITS must implement three types of features, that can used by guests users, registered users, admin users. 

### Basic Features

All users can access the following basic features:

#### Search Train Connections (between two stations)
Return the connections from a starting and ending stations, possibly including changes at interchanging stations. 

The search must be parametrized `travel time`, a `sorting criteria`, and the result can be `limited to a predefined number of connections`.

Travel time is a day of the year (use `day`, `month`, and `year`) and a time (use `hour` and `minute`) in 24h format.
Travel time can be either a departure or arrival time. Specifying a departure time ensures that the trip cannot start before the given time, whereas specifying an arrival time ensures that the trip cannot end after the given time.
By default, i.e., when not explicitly specified, travel time is `departure` and `now`.

A sorting criteria can be one (and only one) of the following:`overall travel time (ott)`, `number of train changes (nc)`, `waiting time (wt)`, and `estimated price (ep)`. 

The overall travel time is the time from the beginning of the trip and its very end.

The number of train changes is the count of how many time the user must change train during the trip

The waiting time is the time the user spent in waiting for a train including the time spent waiting for the first train.

Estimated price is the overall (fixed) cost of the travel, which depends on the type of train used in each connections, and the (variable) cost for seat reservation, which depends on what are the actual seats reserved.

Sorting can be `ascending` or `descending`.
By default, i.e., when not explicitly specified, the sorting criteria is `overall travel time ascending` (so, the system must report the fastest connections first).

In case starting or ending stations do not exist, or no connection between them is possible, the system must return an empty result.

In case the starting or ending stations are the same, the system must return a `ValueError`

#### Check the status of a train
The user should be able to check the status of a train/connection: is the train operational? is delayed? etc.

### Advanced Features

Registered and only registered users can access the following advanced features:

#### Book Tickets and Reserve Seats
Given a train connection instance (e.g., on a given date/time), registered users can book tickets and optionally reserve seats. When the user decides to reserve seats, the system will try to reserve all the available seats automatically.

We make the following assumptions: 

- there is always a place on the trains, so tickets can be always bought
- the train seats are not numbered, so the system must handle only the number of passengers booked on a train and not each single seat.
- The system grants only those seats that are effectively available at the moment of request; thus, overbooking on reserved seats is **not** possible.
- Seats reservation can be done also after booking a ticket.
- A user can only reserve one seat in each train at the given time.
 
#### Access Purchase History

Registered users can list the history of their past purchases, including the starting and ending stations, the day/time, total price, and **for each connection**, the price and whether they reserved a seat.

The purchase history is always represented in descending starting time (at the top the most recent trips)

### Admin Features:

Admin and only admin users can access the following special features:

#### Add/update/remove users
Admin can add/delete users. 

Users are identified by their (unique) email address and might have other attributes.

- Invalid addresses are not allowed (must raise a `ValueError`)
    >> NOTE: Check the validity of the email in the Database not in Python !

- Duplicated addresses are not allowed (must raise a `ValueError`)

To follow GDPR regulation, all the data about deleted users must be deleted as well, including all the seats reservations (seats might become free). If the user does not exist, no exception is raised!

#### Add/update/remove trains
Admin can add, update, or delete trains. Updating a train can change their size (how many seats are available) and their status, i.e., operational vs non operational.
Deleting a train should ensure consistency!
Reservations are cancelled, schedules/trips are cancelled, etc.

#### Add/update/remove schedules
Admin users can also add, update, delete train schedules. A train schedule associates a train with stations (stops) and their estimated time. 

A train might be delayed or cancelled, therefore affecting its schedule.

## Additional methods

Additional or utility methods can be implemented to check seat availability (e.g.,.on a train, along a given connection), view train's schedule on a day, check train statuses (some trains might be delayed or cancelled), and more. 

The implementation of those methods must follow the general guidelines of the assignment: limit the use of python as much as possible and rely on the functionalities provided by the databases as much as you can.


## Hints

1. The methods to implement are listed in the given code; however, some of their parameters may be underspecified (i.e., using `**kwargs`) to allow some flexibility in the implementation. 

    >> Note: In case of problems, write a message on Teams and open an issue on the *public* repository so anyone can contribute and track it.

2. To complete this assignment, you can use any of the following concepts:

    - non-root users definition with specific permissions granted;
    - simple and nested transactions for reading, creating, updating and deleting elements from the database;
    - queries that makes use of grouping and sorting; 
    - transactions with the right isolation level(s);
    - consistency checks and references (cascade, etc.)
    - views;
    - database triggers;

    >> NOTE: Performance is **not** a quality we are looking for; correctness is! So do not waste precious time trying to optimize your queries to minimize execution time.


