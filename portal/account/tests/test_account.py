import pytest

from ..models import User


@pytest.mark.parametrize(
    "email, first_name, last_name, full_name",
    [
        ("John@example.com", "John", "Doe", "John Doe"),
        ("John@example.com", "John", "", "John"),
        ("John@example.com", "", "Doe", "Doe"),
        ("John@example.com", "", "", "John@example.com"),
    ],
)
def test_get_full_name(email, first_name, last_name, full_name):
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    assert user.get_full_name() == full_name
