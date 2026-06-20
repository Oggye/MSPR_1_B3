def build_target(row):
    """
    1 = ligne potentiellement substituable
    0 = non substituable
    """

    distance = row["distance_km"]
    duration = row["duration_min"]
    is_night = row["is_night"]

    if (
        distance <= 1200
        and duration <= 480
    ):
        return 1

    if (
        is_night == 1
        and distance <= 1500
        and duration <= 720
    ):
        return 1

    return 0