import datetime
from unittest.mock import patch

from lambdaCode.models.guest import Guest


@patch("lambdaCode.models.guest.datetime")
def test_guest(mock_datetime):
    exp_datetime = datetime.datetime(2022, 3, 30)
    mock_datetime.now.return_value = exp_datetime
    exp_first_name = "first"
    exp_last_name = "last"
    exp_phone_number = "12345678910"
    exp_email_address = "email@address.com"
    exp_total_number_of_guests_attending = "123"
    exp_not_attending = True
    guest = Guest(
        exp_first_name,
        exp_last_name,
        exp_phone_number,
        exp_email_address,
        exp_total_number_of_guests_attending,
        exp_not_attending,
    )

    assert guest.first_name == exp_first_name
    assert guest.last_name == exp_last_name
    assert guest.phone_number == exp_phone_number
    assert guest.email_address == exp_email_address
    assert (
        guest.total_number_of_guests_attending == exp_total_number_of_guests_attending
    )
    assert guest.not_attending == exp_not_attending
    assert guest.first_name_lower == exp_first_name.lower()
    assert guest.last_name_lower == exp_last_name.lower()
    assert guest.last_updated == exp_datetime
