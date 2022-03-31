from datetime import datetime


class Guest(object):
    def __init__(
        self,
        first_name,
        last_name,
        phone_number,
        email_address,
        total_number_of_guests_attending,
        not_attending,
    ):
        self.first_name: str or None = first_name
        self.first_name_lower: str or None = first_name.lower()
        self.last_name: str or None = last_name
        self.last_name_lower: str or None = last_name.lower()
        self.phone_number: str or None = phone_number
        self.email_address: str or None = email_address
        self.total_number_of_guests_attending: int = total_number_of_guests_attending
        self.last_updated: datetime = datetime.now()
        self.not_attending: bool = not_attending
