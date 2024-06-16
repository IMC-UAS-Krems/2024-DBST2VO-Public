from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from enum import Enum

# Global Constants

# The name of the base user of traits database
BASE_USER_NAME = "traits"
BASE_USER_PASS = "traits-pass"
# The name of the admin user of traits database
ADMIN_USER_NAME = "traits-admin"
ADMIN_USER_PASS = "traits-admin-pass"


class TraitsKey():
    """
    Encapsulate an int or str value and leaves the freedom to use them as keys/IDs
    """

    def __init__(self, value: str|int) -> None:
        self.id = value

    def to_string(self) -> str:
        return str(self.id)
    
    def to_int(self) -> int:
        return int(self.id)


class TrainStatus(Enum):
    OPERATIONAL = 0
    DELAYED = 1
    BROKEN = 2


class SortingCriteria(Enum):
    OVERALL_TRAVEL_TIME = 0
    NUMBER_OF_TRAIN_CHANGES = 1
    OVERALL_WAITING_TIME = 2
    ESTIMATED_PRICE = 3

class TraitsUtilityInterface(ABC):
    """
    This is the reference (abstract) class defining utility methods like CRUD operations on basic entities, 
    and database initialization. NOTE: You can define more methods in your implementation to support your own
    tests
    """

    @abstractmethod
    def __init__(self, rdbms_connection, rdbms_admin_connection, neo4j_driver) -> None:
        pass

    @abstractmethod
    def generate_sql_initialization_code() -> List[str]:
        """
        Returns a list of string each one containing a SQL statment to setup the database. 
        This list resembles the SQL instructions that you can get when dumping a database.
        For instance, it will contains table definitions (CREATE TABLE), setup of the users
        BASE_USER_NAME and ADMIN_USER_NAME

        These instructions will be used to setup the MariaDB database before each and every test
        """
        pass

    @abstractmethod
    def get_all_users(self) -> List:
        """
        Return all the users stored in the database
        """
        pass


    @abstractmethod
    def get_all_schedules(self) -> List:
        """
        Return all the schedules stored in the database
        """
        pass


class TraitsInterface(ABC):
    """
    This is the reference (abstract) class that defines the main admin features.
    """

    @abstractmethod
    def __init__(self, rdbms_connection, rdbms_admin_connection, neo4j_driver) -> None:
        pass

    ########################################################################
    # Basic Features
    ########################################################################

    @abstractmethod
    def search_connections(self, starting_station_key: TraitsKey, ending_station_key: TraitsKey,
                           travel_time_day: int = None, travel_time_month : int = None, travel_time_year : int = None,
                           is_departure_time=True,
                           sort_by : SortingCriteria = SortingCriteria.OVERALL_TRAVEL_TIME, is_ascending : bool =True,
                           limit : int = 5) -> List:
        """
        Search Train Connections (between two stations).
        Sorting criteria can be one of the following:overall travel time, number of train changes, waiting time, and estimated price

        Return the connections from a starting and ending stations, possibly including changes at interchanging stations.
        Returns an empty list if no connections are possible
        Raise a ValueError in case of errors and if the starting or ending stations are the same
        """
        pass

    @abstractmethod
    def get_train_current_status(self, train_key: TraitsKey) -> Optional[TrainStatus]:
        """
        Check the status of a train. If the train does not exist returns None
        """
        pass

    ########################################################################
    # Advanced Features
    ########################################################################

    @abstractmethod
    def buy_ticket(self, user_email: str, connection, also_reserve_seats=True):
        """
        Given a train connection instance (e.g., on a given date/time), registered users can book tickets and optionally reserve seats. When the user decides to reserve seats, the system will try to reserve all the available seats automatically.
        We make the following assumptions:
            - There is always a place on the trains, so tickets can be always bought
            - The train seats are not numbered, so the system must handle only the number of passengers booked on a train and not each single seat.
            - The system grants only those seats that are effectively available at the moment of request; thus, overbooking on reserved seats is not possible.
            - Seats reservation cannot be done after booking a ticket.
            - A user can only reserve one seat in each train at the given time.

        If the user does not exist, the method must raise a ValueError
        """

    @abstractmethod
    def get_purchase_history(self, user_email: str) -> List:
        """
        Access Purchase History

        Registered users can list the history of their past purchases, including the starting and ending stations, the day/time, total price, and for each connection, the price and whether they reserved a seat.
        The purchase history is always represented in descending starting time (at the top the most recent trips).

        If the user is not registered, the list is empty
        """

        pass

    ########################################################################
    # Admin Features:
    ########################################################################

    # Add and remove users
    @abstractmethod
    def add_user(self, user_email: str, user_details) -> None:
        """
        Add a new user to the system with given email and details.
        Email format: <Recipient name>@<Domain name><top-level domain>
        See: https://knowledge.validity.com/s/articles/What-are-the-rules-for-email-address-syntax?language=en_US

        Raise a ValueError if the email has invalid format.
        Raise a ValueError if the user already exists
        """
        pass

    @abstractmethod
    def delete_user(self, user_email: str) -> None:
        """
        Delete the user from the db if the user exists.
        The method should also delete any data related to the user (past/future tickets and seat reservations)
        """
        pass

    # Deleting a train should ensure consistency! Reservations are cancelled, schedules/trips are cancelled, etc.

    @abstractmethod
    def add_train(self, train_key: TraitsKey, train_capacity: int, train_status: TrainStatus) -> None:
        """
        Add new trains to the system with given code.

        Raise a ValueError if the train already exists
        """
        pass

    @abstractmethod
    def update_train_details(self, train_key: TraitsKey, train_capacity: Optional[int] = None, train_status: Optional[TrainStatus] = None) -> None:
        """
        Update the details of existing train if specified (i.e., not None), otherwise do nothing.
        """
        pass

    @abstractmethod
    def delete_train(self, train_key: TraitsKey) -> None:
        """
        Drop the train from the system. Note that all its schedules, reservations, etc. must be also dropped.
        """
        pass

    @abstractmethod
    def add_train_station(self, train_station_key: TraitsKey, train_station_details) -> None:
        """
        Add a train station
        Duplicated are not allowed, raise ValueError
        """
        pass
    
    @abstractmethod
    def connect_train_stations(self, starting_train_station_key: TraitsKey, ending_train_station_key: TraitsKey, travel_time_in_minutes: int)  -> None:
        """
        Connect to train station so trains can travel on them
        Raise ValueError if any of the stations does not exist
        Raise ValueError for invalid travel_times
        """
        pass

    @abstractmethod
    def add_schedule(self, train_key: TraitsKey,
                     starting_hours_24_h: int, starting_minutes: int,
                     stops: List[Tuple[TraitsKey, int]], # [station_key, waiting_time]
                     valid_from_day: int, valid_from_month: int, valid_from_year: int,
                     valid_until_day: int, valid_until_month: int, valid_until_year: int) -> None:
        """
        Create a schedule for a give train.
        The schedule must have at least two stops, cannot connect the same station directly but can create "rings"
        Stops must correspond to existing stations
        Consecutive stops must be connected stations.
        starting hours and minutes defines when this schedule is active
        Validity dates must ensure that valid_from is in the past w.r.t. valid_until
        In case of error, raise ValueError
        """
        pass
