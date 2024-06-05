# Import your implementation in the public tests
from traits.implementation import Traits
from public.traits.interface import TraitsKey

import pytest

@pytest.mark.skip(reason="This test was only illustrative")
def test_smoke_test():
    """ Simply check that the test can be run from the root of the project with pytest public """
    pass

# Empty DB, finds no connections
def test_search_connections():
     """
     Search Train Connections (between two stations).
     Sorting criteria can be one of the following:overall travel time (ott), number of train changes (nc), waiting time (wt), and estimated price (ep)
     Return the connections from a starting and ending stations, possibly including changes at interchanging stations.
     Returns an empty list if no connections are possible
     Raise a ValueError in case of errors and if the starting or ending stations are the same
     """
     
     # TODO How to instantiate this one? Should this be provided via a Fixture?
     t = Traits()
     starting_station_key = TraitsKey("1")
     ending_station_key = TraitsKey("2") 
     no_connections = t.search_connections(starting_station_key, ending_station_key,
                           travel_time_day=None, travel_time_month=None, travel_time_year=None, is_departure_time=True,
                           sort_by="ott", is_ascending=True,
                           limit=5)
     
     assert len(no_connections) == 0, "Wrong number of connections returned"

def test_get_train_current_status():
    """
    Check the status of a train
    The user should be able to check the status of a train/connection: is the train operational? is delayed? etc.

    """
    t = Traits()
    train_key = TraitsKey("1")

    train_status = t.get_train_current_status(train_key)

    assert train_status is None, ""

########################################################################
# Advanced Features
########################################################################

def test_buy_ticket():
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

    t = Traits()
    
    user_email = "user@email.org"
    connection = None # TODO What's here?
    also_reserve_seats = True

    t.buy_ticket(user_email, connection, also_reserve_seats)

    # TODO How to assert? using history?


def test_get_purchase_history():
     """
     Access Purchase History
     Registered users can list the history of their past purchases, including the starting and ending stations, the day/time, total price, and for each connection, the price and whether they reserved a seat
     The purchase history is always represented in descending starting time (at the top the most recent trips).
     
     If the user is not registered, the list is empty
     """
     t = Traits()
     user_email = "user@email.org"
     empty_history = t.get_purchase_history(user_email)

     assert len(empty_history) == 0, "Wrong history returned for non registered user"


########################################################################
# Admin Features:
########################################################################

def test_do_not_add_user_with_invalid_email():
    """
    Add a new user to the system with given email and details.
    Email format: <Recipient name>@<Domain name><top-level domain>
    See: https://knowledge.validity.com/s/articles/What-are-the-rules-for-email-address-syntax?language=en_US

    Raise a ValueError if the email has invalid format.
    Raise a ValueError if the user already exists
    """
    t = Traits()
    invalid_user_email = "this is not a valid email address"
    user_details = None
    with pytest.raises(ValueError) as exc_info:
        t.add_user(invalid_user_email, user_details)


def test_do_not_add_duplicated_user():
    """
    Add a new user to the system with given email and details.
    Email format: <Recipient name>@<Domain name><top-level domain>
    See: https://knowledge.validity.com/s/articles/What-are-the-rules-for-email-address-syntax?language=en_US

    Raise a ValueError if the email has invalid format.
    Raise a ValueError if the user already exists
    """
    t = Traits()
    user_email = "user@email.org"
    user_details = None
    t.add_user(user_email, user_details)
    with pytest.raises(ValueError) as exc_info:
        t.add_user(user_email, user_details)


def test_delete_user():
    """
    Delete the user from the db if the user exists.
    The method should also delete any data related to the user (past/future tickets and seat reservations)
    """
    t = Traits()
    user_email = "user@email.org"
    user_details = None
    t.add_user(user_email, user_details)
    # Make the user buy something
    # Check the user history not empty
    # TODO Probably we should add a get_user method?
    t.get_purchase_history(user_email)
    t.delete_user(user_email)
    empty_history = t.get_purchase_history(user_email)
    assert len(empty_history) == 0

# Deleting a train should ensure consistency! Reservations are cancelled, schedules/trips are cancelled, etc.

def test_canont_add_duplicated_train():
    """
    Add new trains to the system with given code.

    Raise a ValueError if the train already exists
    """
    t = Traits()
    train_key = TraitsKey(1)
    train_capacity = 100
    is_operational = True
    t.add_train(train_key, train_capacity, is_operational)
    with pytest.raises(ValueError) as exc_info:
        train_capacity = 10
        is_operational = False
        t.add_train(train_key, train_capacity, is_operational)


def test_update_train_details(train_key, train_capacity=None, is_operational=None):
    """
    Update the details of existing trains, otherwise do nothing
    """
    t = Traits()
    
    train_key = TraitsKey(1)
    train_capacity = 100
    t.add_train(train_key, train_capacity, is_operational=True)
    current_status = t.get_train_current_status()
    
    t.update_train_details(train_key, is_operational=False)
    updated_status = t.get_train_current_status()
    assert updated_status != current_status, f"wrong train updated status {updated_status}"

def test_delete_train():
    """
    Drop the train from the system.
    Note that all its schedules, reservations, etc. must be also dropped.
    """
    t = Traits()
    
    train_key = TraitsKey(1)
    t.delete_train(train_key)
    no_state = t.get_train_current_status(train_key)
    assert no_state is None, "Wrong train status after delete"

def test_do_not_add_duplicated_train_station():
    """
    Add a train station
    Duplicated are not allowed, raise ValueError
    """
    t = Traits()
    train_station_key = TraitsKey(0)
    t.add_train_station(train_station_key)
    with pytest.raises(ValueError) as exc_info:
        t.add_train_station(train_station_key)

def test_do_not_connect_train_stations_that_do_not_exist():
    """
    Connect to train station so trains can travel on them
    Raise ValueError if any of the stations does not exist
    Raise ValueError for invalid travel_times
    """
    t = Traits()
    starting_train_station_key = TraitsKey(0)
    ending_train_station_key = TraitsKey("2") 
    travel_time = 5 # minutes
    with pytest.raises(ValueError) as exc_info:
        t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)

def test_do_not_connect_train_stations_with_wrong_time():
    """
    Connect to train station so trains can travel on them
    Raise ValueError if any of the stations does not exist
    Raise ValueError for invalid travel_times
    """
    t = Traits()
    starting_train_station_key = TraitsKey(0)
    ending_train_station_key = TraitsKey(1)
    travel_time = 0 # Impossible time!
    with pytest.raises(ValueError) as exc_info:
        t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)


def test_add_schedule():
    """
    Create a schedule for a give train.
    The schedule must have at least two stops, cannot connect the same station directly but can create "rings"
    Stops must correspond to existing stations
    Consecutive stops must be connected.
    Validity dates must ensure that valid_from is in the past w.r.t. valid_until
    In case of error, raise ValueError
    """

    t = Traits()
    # Add two stations
    starting_train_station_key = TraitsKey(1)
    ending_train_station_key = TraitsKey("2") # Not a typo !
    travel_time = 10
    # Connect the two stations
    t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)
    # Add a train
    train_key = None
    t.add_train(train_key)
    # Stops
    stops = []
    stops.append( (starting_train_station_key, 5) )
    stops.append( (ending_train_station_key, 10) )
    # Valid from 1 jan to 31 dec 2024
    valid_from_day, valid_from_month, valid_from_year = 1, 1, 2024
    valid_until_day, valid_until_month, valid_until_year = 31, 12, 2024
    starting_hours_24_h = 8
    starting_minutes = 0
    t.add_schedule(
                train_key,
                starting_hours_24_h, starting_minutes,
                stops,
                valid_from_day, valid_from_month, valid_from_year,
                valid_until_day, valid_until_month, valid_until_year)
