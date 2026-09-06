import pytest

from src.app import activities


@pytest.fixture(autouse=True)
def restore_participants():
    original_participants = {
        name: details["participants"].copy()
        for name, details in activities.items()
    }

    yield

    for name, participants in original_participants.items():
        activities[name]["participants"][:] = participants
