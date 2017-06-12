# Flightradar24
Script for automated flights data download by given Airport ID
The script collects all flights numbers according to the Arrivals/Departures pages (all dates are saved),
Then iterate over all flights (by opening the flight) and download all CSVs according to the saved dates.
* For a business account downloads are limited to 1000, and only flights of the last two days are presented

Hard Coded: (needed)
-----------
- Airport ID
- Username (required for being able to download CSVs)
- Password
