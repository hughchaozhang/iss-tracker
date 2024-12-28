# ISS Tracker

A Python application that helps you track and view the International Space Station (ISS) from any location on Earth. The program provides precise viewing instructions with local timezone support and compass directions.

## Features

- Get real-time ISS position
- Find upcoming visible passes for any location worldwide
- Automatic city name to coordinates conversion
- Local timezone detection and time conversion
- Detailed viewing instructions with compass directions
- Elevation angles for optimal viewing
- Graceful fallback to default location (Los Angeles)
- Robust error handling for API and geocoding services

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - requests
  - pytz
  - timezonefinder
  - geopy
- N2YO API key (free from n2yo.com)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hughchaozhang/iss-tracker.git
cd iss-tracker
```

2. Install required packages:
```bash
pip install requests pytz timezonefinder geopy
```

3. Set up your N2YO API key:
- Sign up for a free API key at [N2YO.com](https://www.n2yo.com/api/)
- Set your API key as an environment variable:
```bash
export N2YO_API_KEY='your-api-key-here'
```

## Usage

Run the program:
```bash
python iss_pass_my_city.py
```

When prompted:
1. Enter your city name (or press Enter for Los Angeles)
2. Optionally enter your state
3. Optionally enter your country (defaults to USA)

The program will display:
- Confirmed location with full address
- Location coordinates
- Local timezone
- Current ISS position
- Upcoming visible passes with:
  - Start and end times in your local timezone
  - Starting and ending directions in degrees and cardinal points
  - Maximum elevation
  - Duration
  - Easy-to-follow viewing instructions

## Example Output

```
Location: Los Angeles, California, USA
Coordinates: 34.0522, -118.2437
Timezone: America/Los_Angeles

Current ISS Position:
Latitude: 45.6234°
Longitude: -122.3456°
Altitude: 408.23 km

Upcoming visible passes:

Pass 1:
Start: 2024-12-28 08:30:15 PM PST
Starting direction: 315° (NW)
Maximum Elevation: 45°
Ending direction: 135° (SE)
End: 2024-12-28 08:35:45 PM PST
Duration: 330 seconds
Viewing guide: Look NW at 08:30 PM, the ISS will rise to 45° above horizon and set SE
```

## Error Handling

The application includes robust error handling for:
- Invalid API responses
- Geocoding failures
- Timezone conversion issues
- Network connectivity problems
- Missing or invalid API keys

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [N2YO API](https://www.n2yo.com/api/) for satellite tracking data
- [OpenStreetMap Nominatim](https://nominatim.org/) for geocoding services
- Python packages: pytz, timezonefinder, and geopy

## Note

For optimal viewing:
- Choose passes with maximum elevation > 30°
- Look for clear weather conditions
- Find an area with minimal light pollution
- Consider local obstacles that might block your view