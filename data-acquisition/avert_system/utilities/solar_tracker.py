# coding: utf-8
"""
Small module for calculating sunrise/sunset times for a given point in the world.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime, time, timedelta
from math import degrees as deg, radians as rad
from math import cos, sin, acos, asin, tan
from zoneinfo import ZoneInfo


def calculate_solar_timetable(
    longitude: float, latitude: float, dt: datetime, timezone_offset: float
) -> tuple[time, time, time]:
    """
    Calculate the sunrise, solar noon, and sunset times in the local timezone
    for a given location/datetime.

    Parameters
    ----------
    longitude: Geographical coordinate denoting how many degrees E(+) or W(-).
    latitude: Geographical coordinate denoting how many degrees N(+) or S(-).
    dt: The date and time of interest.
    timezone_offset: Difference, in hours, between local and UTC time.

    Returns
    -------
    sunrise, solar_noon, sunset: Times, in local time, for eponymous events.

    """

    equation_of_time, hour_angle = evaluate_orbital_parameters(
        latitude, dt, timezone_offset
    )
    solar_noon = (720 - 4 * longitude - equation_of_time + timezone_offset * 60) / 1440
    sunrise = (solar_noon * 1440 - hour_angle * 4) / 1440
    sunset = (solar_noon * 1440 + hour_angle * 4) / 1440

    return sunrise, solar_noon, sunset


def evaluate_orbital_parameters(
    latitude: float, dt: datetime, timezone_offset: float
) -> tuple[float, float]:
    """
    Calculate the relevant orbital parameters at a given latitude on a given
    day.

    Parameters
    ----------
    latitude: Geographical coordinate denoting how many degrees N(+) or S(-).
    dt: The date and time of interest.
    timezone_offset: Difference, in hours, between local and UTC time.

    Returns
    -------
    equation_of_time: ---
    hour_angle: Number of hours between sunrise/sunset and solar noon, based on
                the angle between the Sun and the horizon at solar zenith.

    """

    date = (dt - datetime(year=1900, month=1, day=1)).days + 2
    fraction_of_day = 0.5
    julian_day = date + 2415018.5 + fraction_of_day - timezone_offset / 24
    julian_century = (julian_day - 2451545) / 36525
    geom_mean_sun_longitude = (
        280.46646 + julian_century * (36000.76983 + julian_century * 0.0003032)
    ) % 360
    geom_mean_sun_anomaly = 357.52911 + julian_century * (
        35999.05029 - 0.0001537 * julian_century
    )
    orbital_eccentricity = 0.016708634 - julian_century * (
        0.000042037 + 0.0000001267 * julian_century
    )
    eq_of_centre_sun = (
        sin(rad(geom_mean_sun_anomaly))
        * (1.914602 - julian_century * (0.004817 + 0.000014 * julian_century))
        + sin(rad(2 * geom_mean_sun_anomaly)) * (0.019993 - 0.000101 * julian_century)
        + sin(rad(3 * geom_mean_sun_anomaly)) * 0.000289
    )
    sun_true_longitude = geom_mean_sun_longitude + eq_of_centre_sun
    mean_oblique_ecliptic = (
        23
        + (
            26
            + (
                (
                    21.448
                    - julian_century
                    * (46.815 + julian_century * (0.00059 - julian_century * 0.001813))
                )
            )
            / 60
        )
        / 60
    )
    sun_apparent_longitude = (
        sun_true_longitude
        - 0.00569
        - 0.00478 * sin(rad(125.04 - 1934.136 * julian_century))
    )
    oblique_correction = mean_oblique_ecliptic + 0.00256 * cos(
        rad(125.04 - 1934.136 * julian_century)
    )
    var_y = tan(rad(oblique_correction / 2)) * tan(rad(oblique_correction / 2))
    sun_declination = deg(
        asin(sin(rad(oblique_correction)) * sin(rad(sun_apparent_longitude)))
    )

    hour_angle = deg(
        acos(
            cos(rad(90.833)) / (cos(rad(latitude)) * cos(rad(sun_declination)))
            - tan(rad(latitude)) * tan(rad(sun_declination))
        )
    )

    equation_of_time = 4 * deg(
        var_y * sin(2 * rad(geom_mean_sun_longitude))
        - 2 * orbital_eccentricity * sin(rad(geom_mean_sun_anomaly))
        + 4
        * orbital_eccentricity
        * var_y
        * (sin(rad(geom_mean_sun_anomaly)) * cos(2 * rad(geom_mean_sun_longitude)))
        - 0.5 * var_y**2 * sin(4 * rad(geom_mean_sun_longitude))
        - 1.25 * orbital_eccentricity**2 * sin(2 * rad(geom_mean_sun_anomaly))
    )

    return equation_of_time, hour_angle


def day_fraction2time(day: float) -> time:
    """
    Convert a fraction of a day to hours and minutes e.g. 0.5 = 12:00:00.

    Parameters
    ----------
    day_fraction: Proportion of day, between 0.0 and 1.0.

    Returns
    -------
    time: Day fraction converted to hours and minutes.

    """

    hours = 24.0 * day
    minutes = (hours - int(hours)) * 60
    seconds = (minutes - int(minutes)) * 60

    return time(hour=int(hours), minute=int(minutes), second=int(seconds))


def timezone_aware_time(
    naive_local_time: datetime, timezone: str
) -> tuple[datetime, datetime]:
    """
    Make a local time timezone aware and calculate the equivalent time in UTC.

    Parameters
    ----------
    naive_local_time: A non-timezone aware representation of the local time.
    timezone: Simple text identifier for the timezone of the location.

    Returns
    -------
    (local_time, utc_time): Timezone aware times in local and UTC time.

    """

    local_time = naive_local_time.replace(tzinfo=ZoneInfo(timezone))
    utc_time = local_time.astimezone(ZoneInfo("UTC"))

    return local_time, utc_time


def is_it_daytime(
    longitude: float, latitude: float, timezone: str, buffer: float
) -> bool:
    """
    Evaluate sunrise/sunset times for a given location and check if it is
    currently day or night. A small buffer can be included to account for
    twilight.

    Parameters
    ----------
    longitude: Geographical coordinate denoting how many degrees E(+) or W(-).
    latitude: Geographical coordinate denoting how many degrees N(+) or S(-).
    timezone: Simple text identifier for the timezone of the location.
    buffer: How many hours of buffer to use at the start/end of the day.

    Returns
    -------
    day_or_night: True if day, False if night.

    """

    naive_utc_dt = datetime.utcnow()
    utc_dt = naive_utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(ZoneInfo(timezone))

    timezone_offset = (
        local_dt.utcoffset().days * 24.0 + local_dt.utcoffset().seconds / 3600
    )

    if utc_dt.hour < abs(timezone_offset):
        date_correction = timedelta(days=1)
    else:
        date_correction = timedelta(days=0)

    sunrise, solar_noon, sunset = calculate_solar_timetable(
        longitude, latitude, naive_utc_dt - date_correction, timezone_offset
    )

    sunrise_local, sunrise_utc = timezone_aware_time(
        datetime.combine(utc_dt.date(), day_fraction2time(sunrise)), timezone
    )
    solar_noon_local, solar_noon_utc = timezone_aware_time(
        datetime.combine(utc_dt.date(), day_fraction2time(solar_noon)), timezone
    )
    sunset_local, sunset_utc = timezone_aware_time(
        datetime.combine(utc_dt.date(), day_fraction2time(sunset)), timezone
    )

    after_sunrise = utc_dt > sunrise_utc - timedelta(hours=buffer)
    before_sunset = utc_dt < sunset_utc + timedelta(hours=buffer)

    return after_sunrise and before_sunset
