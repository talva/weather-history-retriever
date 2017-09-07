# weather
Collect weather data through an API and prepare it for analytics in Tableau

Using https://darksky.net script retrieves historical weather data for single or multiple locations.
The first 1000 API requests every day are free of charge.

Script reads a file with weather data, checks for days with missing data 
and updates the file with data from the missing days.

Register on https://darksky.net/dev to receive a personal access token which need to be added in settings.py file.
In settings user should set locations as follows:

LOCATIONS = {(‘City1’, latitude1,longitude1),(‘City2’,latitude2,longitude2)}
Example:
LOCATIONS = {(‘Zurich’, 47.3769,8.5417),(‘Amsterdam’,52.3702,4.8952), (‘London’,50.5074,-0.1278)}
Or
LOCATIONS = {(‘London’,51.5074,-0.1278)}

