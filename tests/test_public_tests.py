# Import your implementation in the public tests
from traits.implementation import Traits, TraitsUtility
from public.traits.interface import TraitsKey, TrainStatus, SortingCriteria
import pytest


def test_cannot_find_a_connections_if_stations_do_not_exist(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    # Those two stations do not exist in the database
    starting_station_key = TraitsKey("1")
    ending_station_key = TraitsKey("2")

    with pytest.raises(ValueError) as exc_info:
        # This call should fail because the stations do not exist in the database
        t.search_connections(starting_station_key, ending_station_key,
                        travel_time_day=None, travel_time_month=None, travel_time_year=None, is_departure_time=True,
                        sort_by=SortingCriteria.OVERALL_TRAVEL_TIME, is_ascending=True,
                        limit=5)


def test_cannot_find_a_connections_if_stations_are_unreacheable(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    # Add the stations to the database but do not connect them, so no connection can be found between them
    starting_station_key = TraitsKey("1")
    train_station_details = None
    t.add_train_station(starting_station_key, train_station_details)

    ending_station_key = TraitsKey("2")
    t.add_train_station(ending_station_key, train_station_details)

    
        # This call should fail because the stations do not exist in the database
    no_connections = t.search_connections(starting_station_key, ending_station_key,
                        travel_time_day=None, travel_time_month=None, travel_time_year=None, is_departure_time=True,
                        sort_by=SortingCriteria.OVERALL_TRAVEL_TIME, is_ascending=True,
                        limit=5)
    
    assert len(no_connections) == 0, "Wrong number of connections returned"


def test_train_status_in_empty_if_no_train_exist(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    # This train is not stored in the db
    train_key = TraitsKey("1")
    
    # Should return nothing
    train_status = t.get_train_current_status(train_key)

    assert train_status is None, ""

########################################################################
# Advanced Features
########################################################################

def test_buy_ticket(rdbms_connection, rdbms_admin_connection, neo4j_db):
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
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    # User does not exist
    user_email = "user@email.org"
    # No connection is specified
    connection = None 
    also_reserve_seats = True

    with pytest.raises(ValueError) as exc_info:
       t.buy_ticket(user_email, connection, also_reserve_seats)


def test_get_empty_purchase_history_if_user_not_registered(rdbms_connection, rdbms_admin_connection, neo4j_db):
     t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
     user_email = "user@email.org"
     empty_history = t.get_purchase_history(user_email)

     assert len(empty_history) == 0, "Wrong history returned for non registered user"


########################################################################
# Admin Features:
########################################################################

def test_do_not_add_user_with_invalid_email(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    invalid_user_email = "this is not a valid email address"
    user_details = None
    with pytest.raises(ValueError) as exc_info:
        t.add_user(invalid_user_email, user_details)


def test_do_not_add_duplicated_user(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    user_email = "user@email.org"
    user_details = None
    t.add_user(user_email, user_details)
    with pytest.raises(ValueError) as exc_info:
        t.add_user(user_email, user_details)


def test_delete_user(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    user_email = "user@email.org"
    user_details = None
    t.add_user(user_email, user_details)
    utils = TraitsUtility(rdbms_connection, rdbms_admin_connection, neo4j_db)
    assert len(utils.get_all_users()) == 1, f"User {user_email} not inserted"
    # Delete the user
    t.delete_user(user_email)
    assert len(utils.get_all_users()) == 0, f"User {user_email} not correctly removed"


def test_canont_add_duplicated_train(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    train_key = TraitsKey(1)
    train_capacity = 100
    is_operational = True
    t.add_train(train_key, train_capacity, is_operational)
    with pytest.raises(ValueError) as exc_info:
        train_capacity = 10
        is_operational = False
        t.add_train(train_key, train_capacity, is_operational)


def test_update_train_details(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    train_key = TraitsKey(1)
    train_capacity = 100
    
    t.add_train(train_key, train_capacity, train_status=TrainStatus.OPERATIONAL)
    current_status = t.get_train_current_status(train_key)
    
    t.update_train_details(train_key, train_status=TrainStatus.DELAYED)
    updated_status = t.get_train_current_status(train_key)

    assert updated_status != current_status, f"wrong train updated status {updated_status}"


def test_delete_a_nonexisting_train_should_not_fail(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    
    train_key = TraitsKey(1)
    t.delete_train(train_key)
    no_state = t.get_train_current_status(train_key)
    assert no_state is None, "Wrong train status after delete"


def test_do_not_add_duplicated_train_station(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    train_station_key = TraitsKey(0)
    train_station_details = None
    t.add_train_station(train_station_key, train_station_details)
    with pytest.raises(ValueError) as exc_info:
        t.add_train_station(train_station_key, train_station_details)


def test_do_not_connect_train_stations_that_do_not_exist(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    starting_train_station_key = TraitsKey(0)
    ending_train_station_key = TraitsKey("2") 
    travel_time = 5 # minutes
    with pytest.raises(ValueError) as exc_info:
        t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)

def test_do_not_connect_train_stations_with_wrong_travel_time(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    starting_train_station_key = TraitsKey(0)
    ending_train_station_key = TraitsKey(1)
    travel_time = 0 # Impossible time!
    with pytest.raises(ValueError) as exc_info:
        t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)


def test_simple_add_schedule(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)

    # Add two stations
    starting_train_station_key = TraitsKey(1)
    train_station_details = None
    t.add_train_station(starting_train_station_key, train_station_details)

    ending_train_station_key = TraitsKey("2") # Not a typo !
    t.add_train_station(ending_train_station_key, train_station_details)

    # Connect the two stations
    travel_time = 20
    t.connect_train_stations(starting_train_station_key, ending_train_station_key, travel_time)
    
    # Add a train
    train_key = None
    t.add_train(train_key, train_capacity=100, train_status=TrainStatus.OPERATIONAL)
    # Stops
    stops = []
    # The train waits 5 minutes at first station
    stops.append( (starting_train_station_key, 5) )
    # The train travels 20 minutes to second station and then wait an additional 10 minutes
    stops.append( (ending_train_station_key, 10) )

    # The schedule starts everyday at 08:00 AM
    starting_hours_24_h, starting_minutes = 8, 0

    # The schedule is valid from 1 jan to 31 dec 2024
    valid_from_day, valid_from_month, valid_from_year = 1, 1, 2024
    valid_until_day, valid_until_month, valid_until_year = 31, 12, 2024
    
    #
    t.add_schedule(
                train_key,
                starting_hours_24_h, starting_minutes,
                stops,
                valid_from_day, valid_from_month, valid_from_year,
                valid_until_day, valid_until_month, valid_until_year)
    
    utils = TraitsUtility(rdbms_connection, rdbms_admin_connection, neo4j_db)

    assert len(utils.get_all_schedules()) == 1, "The schedule was not correctly stored"


def test_do_not_add_schedule_if_stops_are_not_connected(rdbms_connection, rdbms_admin_connection, neo4j_db):
    t = Traits(rdbms_connection, rdbms_admin_connection, neo4j_db)
    # Add two stations
    starting_train_station_key = TraitsKey(1)
    train_station_details = None
    t.add_train_station(starting_train_station_key, train_station_details)

    ending_train_station_key = TraitsKey("2") # Not a typo !
    t.add_train_station(ending_train_station_key, train_station_details)

    # DO NOT CONNECT THE TWO STATIONS. So they cannot be consecutive stops in the schedule
    
    # Add a train
    train_key = None
    t.add_train(train_key, train_capacity=100, train_status=TrainStatus.OPERATIONAL)

    # Stops
    stops = []
    # The train waits 5 minutes at first station
    stops.append( (starting_train_station_key, 5) )
    # This is not possible, since the stations are NOT connected
    stops.append( (ending_train_station_key, 10) )

    # The schedule starts everyday at 08:00 AM
    starting_hours_24_h, starting_minutes = 8, 0

    # The schedule is valid from 1 jan to 31 dec 2024
    valid_from_day, valid_from_month, valid_from_year = 1, 1, 2024
    valid_until_day, valid_until_month, valid_until_year = 31, 12, 2024
    
    with pytest.raises(ValueError) as exc_info:
        # This should fail because stations are not connected
        t.add_schedule(
                train_key,
                starting_hours_24_h, starting_minutes,
                stops,
                valid_from_day, valid_from_month, valid_from_year,
                valid_until_day, valid_until_month, valid_until_year)