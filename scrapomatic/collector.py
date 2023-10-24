import abc


class Collector(metaclass=abc.ABCMeta):
    """
    This class is an interface for all the data collectors in scrape-o-matic.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'scrape') and
                callable(subclass.scrape) or NotImplemented
        )

    @abc.abstractmethod
    def collect(self, username: str) -> dict:
        """
        Base method for all platform collectors. This method will return a dictionary of all
        the data available from the given social media platform.
        :param username: The username for the account that you want information about.
        :return:  A dict of all the data returned.
        """
        raise NotImplementedError
