from abc import ABC, abstractmethod

class TraitsInterface(ABC):
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