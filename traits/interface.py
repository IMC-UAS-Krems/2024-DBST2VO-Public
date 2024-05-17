from abc import ABC, abstractmethod

class AbstractAdminTraits(ABC):
    """
    This is the reference (abstract) class that defines the main admin features. Admin features cannot be invoked by
    regular (non-admin) database users!
    """

    @abstractmethod
    def add_trains():
        """
        Add new trains to the system.
        """
        pass

    @abstractmethod
    def update_train_details():
        """
        Update the details of existing trains.
        """
        pass

    @abstractmethod
    def cancel_train():
        """
        Cancel train from the system, i.e., the train does not operate
        """
        pass

    @abstractmethod
    def resume_train():
        """
        Resume the train, i.e., the train (re)start operation
        """
        pass

    @abstractmethod
    def delete_train():
        """
        Drop the train from the system
        """
        pass


    @abstractmethod
    def add_trains():
        pass


class AbstractTraits(ABC):
    """
    This is the reference (abstract) class to implement for storing and retrieving the data fromn the TRAITS database.
    """

    #     View Trains Schedule
    # Search Trains
    # Check Seats Availability
    # Train Timings
    # Fare Enquiry
    # Trains Between Stations
    # Booking Seats Online
    # Login and Logout Security
    # Password Changes
    # Payment Gateway
    # Ticket Booking History

    @abstractmethod
    def search_for_connection(starting_station: str, ending_station:str, options: dict) -> list:

        pass