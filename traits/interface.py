from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
class TraitsInterface(ABC):
    """
    This is the reference (abstract) class that defines the main admin features.
    """

    ########################################################################
    # Basic Features
    ########################################################################

    @abstractmethod
    def search_connections(starting_station_key, ending_station_key,
                           travel_time_day=None, travel_time_month=None, travel_time_year=None, is_departure_time=True,
                           sort_by="ott", is_ascending=True,
                           limit=5) -> List:
        """
        Search Train Connections (between two stations).
        Sorting criteria can be one of the following:overall travel time (ott), number of train changes (nc), waiting time (wt), and estimated price (ep)

        Return the connections from a starting and ending stations, possibly including changes at interchanging stations.
        Returns an empty list if no connections are possible
        Raise a ValueError in case of errors and if the starting or ending stations are the same
        """
        pass

    @abstractmethod
    def get_train_current_status(train_key) -> Optional[str]:
        """
        Check the status of a train
        The user should be able to check the status of a train/connection: is the train operational? is delayed? etc.
        """
        pass

    ########################################################################
    # Advanced Features
    ########################################################################

    @abstractmethod
    def buy_ticket(user_email, connection, also_reserve_seats=True):
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
    def get_purchase_hystory(user_email):
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
    def add_user(user_email, user_details):
        """
        Add a new user to the system with given email and details.
        Email format: <Recipient name>@<Domain name><top-level domain>
        See: https://knowledge.validity.com/s/articles/What-are-the-rules-for-email-address-syntax?language=en_US

        Raise a ValueError if the email has invalid format.
        Raise a ValueError if the user already exists
        """
        pass

    @abstractmethod
    def delete_user(user_email):
        """
        Delete the user from the db if the user exists.
        The method should also delete any data related to the user (past/future tickets and seat reservations)
        """
        pass

    # Deleting a train should ensure consistency! Reservations are cancelled, schedules/trips are cancelled, etc.

    @abstractmethod
    def add_train(train_key, train_capacity, is_operational):
        """
        Add new trains to the system with given code.

        Raise a ValueError if the train already exists
        """
        pass

    @abstractmethod
    def update_train_details(train_key, train_capacity=None, is_operational=None):
        """
        Update the details of existing trains, otherwise do nothing
        """
        pass

    @abstractmethod
    def delete_train(train_key):
        """
        Drop the train from the system. Note that all its schedules, reservations, etc. must be also dropped.
        """
        pass

    @abstractmethod
    def add_train_station(train_station_key):
        """
        Add a train station
        Duplicated are not allowed, raise ValueError
        """
        pass

    def connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time):
        """
        Connect to train station so trains can travel on them
        Raise ValueError if any of the stations does not exist
        Raise ValueError for invalid travel_times
        """
        pass

    @abstractmethod
    def add_schedule(train_key,
                     stops: List[Tuple], # [station_key, waiting_time]
                     valid_from_day, valid_from_month, valid_from_year,
                     valid_until_day, valid_until_month, valid_until_year):
        """
        Create a schedule for a give train.
        The schedule must have at least two stops, cannot connect the same station directly but can create "rings"
        Stops must correspond to existing stations
        Consecutive stops must be connected.
        Validity dates must ensure that valid_from is in the past w.r.t. valid_until
        In case of error, raise ValueError
        """

        pass







