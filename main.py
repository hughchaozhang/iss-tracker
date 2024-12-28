import requests
from datetime import datetime
import os
import pytz
from time import sleep
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Default LA coordinates
DEFAULT_CITY = "Los Angeles"
DEFAULT_COORDS = {
    "latitude": 34.052235,
    "longitude": -118.243683
}


# N2YO API configuration
N2YO_API_KEY = os.getenv("N2YO_API_KEY")  # You'll need to get this from n2yo.com
SATELLITE_ID = 25544  # ISS NORAD ID


def get_user_location():
    """Get location input from user"""
    print("\nEnter location details (press Enter for Los Angeles):")
    city = input("City: ").strip()
    if not city:
        return None

    state = input("State (optional, press Enter to skip): ").strip()
    country = input("Country (optional, press Enter for USA): ").strip() or "USA"

    # Construct location string
    location = city
    if state:
        location += f", {state}"
    if country:
        location += f", {country}"

    return location


def get_city_coordinates(location=None):
    """Get coordinates for a given location string, default to LA if None or error"""
    if not location:
        print(f"\nUsing default location: {DEFAULT_CITY}")
        return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY

    try:
        geolocator = Nominatim(user_agent="iss_tracker")
        location_data = geolocator.geocode(location)

        if location_data:
            print(f"\nFound location: {location_data.address}")
            return location_data.latitude, location_data.longitude, location_data.address
        else:
            print(f"\nCould not find coordinates for {location}, using Los Angeles as default")
            return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"\nError getting coordinates: {e}. Using Los Angeles as default")
        return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY


def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates"""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    return timezone_str or 'America/Los_Angeles'  # Default to LA if lookup fails


def get_iss_position():
    """Get current ISS position using N2YO API with rate limiting"""
    sleep(1)  # Basic rate limiting
    """Get current ISS position using N2YO API"""
    try:
        url = f"https://api.n2yo.com/rest/v1/satellite/positions/{SATELLITE_ID}/0/0/0/1/?apiKey={N2YO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for bad status codes
        data = response.json()

        # Add debug logging
        print(f"API Response: {data}")  # Temporary debug line

        # Check if required keys exist
        if 'error' in data:
            print(f"API Error: {data['error']}")
            return None, None, None

        if 'positions' not in data:
            print("Unexpected API response format - 'positions' key not found")
            return None, None, None

        if not data['positions']:
            print("No position data returned")
            return None, None, None

        positions = data['positions'][0]
        return float(positions['satlatitude']), float(positions['satlongitude']), float(positions['sataltitude'])

    except requests.exceptions.RequestException as e:
        print(f"Error getting ISS position: {e}")
        return None, None, None
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response: {e}")
        return None, None, None
    except ValueError as e:
        print(f"Error converting position values: {e}")
        return None, None, None


def get_next_passes(lat, lng, alt=0, days=10):
    """Get next visible passes using N2YO API"""
    try:
        url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{SATELLITE_ID}/{lat}/{lng}/{alt}/{days}/300/&apiKey={N2YO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['passes']
    except requests.exceptions.RequestException as e:
        print(f"Error getting pass predictions: {e}")
        return None


def format_pass_info(pass_data, timezone_str):
    """Format pass information for display in local timezone"""
    try:
        local_timezone = pytz.timezone(timezone_str)
        start_time = datetime.fromtimestamp(pass_data['startUTC'], tz=pytz.UTC).astimezone(local_timezone)
        end_time = datetime.fromtimestamp(pass_data['endUTC'], tz=pytz.UTC).astimezone(local_timezone)

        return (f"Start: {start_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n"
                f"Starting direction: {pass_data['startAz']}° ({get_cardinal_direction(pass_data['startAz'])})\n"
                f"Maximum Elevation: {pass_data['maxEl']}°\n"
                f"Ending direction: {pass_data['endAz']}° ({get_cardinal_direction(pass_data['endAz'])})\n"
                f"End: {end_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n"
                f"Duration: {pass_data['duration']} seconds\n"
                f"Viewing guide: Look {get_cardinal_direction(pass_data['startAz'])} at {start_time.strftime('%I:%M %p')}, "
                f"the ISS will rise to {pass_data['maxEl']}° above horizon "
                f"and set {get_cardinal_direction(pass_data['endAz'])}")
    except pytz.exceptions.PytzError as e:
        print(f"Timezone error: {e}. Falling back to UTC")
        # Fallback to UTC if there's any timezone error
        start_time = datetime.fromtimestamp(pass_data['startUTC'], tz=pytz.UTC)
        end_time = datetime.fromtimestamp(pass_data['endUTC'], tz=pytz.UTC)
        return (f"Start: {start_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n"
                f"End: {end_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n")


def get_cardinal_direction(azimuth):
    """
    Convert azimuth angle to cardinal direction.
    
    Args:
        azimuth (float): Angle in degrees (0-360)
        
    Returns:
        str: Cardinal direction (e.g., 'N', 'NNE', 'NE', etc.)
        
    Example:
        >>> get_cardinal_direction(45)
        'NE'
    """
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(azimuth / 22.5) % 16
    return directions[index]


def main():
    # Get location input from user
    location = get_user_location()

    # Get coordinates for the location
    latitude, longitude, address = get_city_coordinates(location)
    timezone_str = get_timezone_from_coordinates(latitude, longitude)

    print(f"\nLocation: {address}")
    print(f"Coordinates: {latitude:.4f}, {longitude:.4f}")
    print(f"Timezone: {timezone_str}")

    # Get current position
    print("\nFetching ISS position...")
    lat, lng, alt = get_iss_position()
    if all(v is not None for v in (lat, lng, alt)):
        print(f"\nCurrent ISS Position:")
        print(f"Latitude: {lat:.4f}°")
        print(f"Longitude: {lng:.4f}°")
        print(f"Altitude: {alt:.2f} km")
    else:
        print("Unable to fetch current ISS position")

    # Get next passes
    print("\nFetching upcoming passes...")
    passes = get_next_passes(latitude, longitude)
    if passes:
        print("\nUpcoming visible passes:")
        for i, pass_data in enumerate(passes, 1):
            print(f"\nPass {i}:")
            print(format_pass_info(pass_data, timezone_str))
    else:
        print("No upcoming visible passes found or error fetching pass data")


if __name__ == "__main__":
    if not N2YO_API_KEY:
        print("Error: N2YO API key not found. Please set the N2YO_API_KEY environment variable.")
    else:
        main()