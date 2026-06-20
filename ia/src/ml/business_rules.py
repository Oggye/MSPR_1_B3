# ia\src\ml\business_rules.py

DAY_MAX_DISTANCE = 1200
DAY_MAX_DURATION = 480

NIGHT_MAX_DISTANCE = 1500
NIGHT_MAX_DURATION = 720


def build_target(row):

    distance = row["distance_km"]
    duration = row["duration_min"]

    if (
        distance <= DAY_MAX_DISTANCE
        and duration <= DAY_MAX_DURATION
    ):
        return 1

    if (
        row["is_night"]
        and distance <= NIGHT_MAX_DISTANCE
        and duration <= NIGHT_MAX_DURATION
    ):
        return 1

    return 0