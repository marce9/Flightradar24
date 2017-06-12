from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import datetime
from calendar import month_abbr


def parse_date(text):
    record_date = text[1:8]

    return record_date[4:] + ' ' + record_date[1:3]


def record_date_to_datetime(text):
    record_date = text

    day = record_date[4:]

    month = record_date[:3]

    for k, v in enumerate(month_abbr):

        if v == month:
            month = k

            break

    new_date = datetime.date(2017, month, int(day))

    return new_date


def get_minimum_date(dates_list):
    minimum_date = record_date_to_datetime(dates_list[0])

    for dte in dates_list[1:]:

        tmp_date = record_date_to_datetime(dte)

        if tmp_date < minimum_date:
            minimum_date = tmp_date

    return minimum_date


def get_max_y_value(y_values_list):
    maximum_y_value = y_values_list[0]

    for tmp_y_value in y_values_list[1:]:

        if maximum_y_value < tmp_y_value:
            maximum_y_value = tmp_y_value

    return maximum_y_value


chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile': {
        'password_manager_enabled': False
    }
})

flights_numbers = []

dates = []

driver = webdriver.Chrome(os.getcwd() + '\chromedriver.exe', chrome_options=chrome_options)

# First sign-in

driver.get('https://www.flightradar24.com')

element = driver.find_element_by_css_selector(".premium-menu-title.premium-menu-title-login")

element.click()

username = driver.find_element_by_id("fr24_SignInEmail")
username.send_keys("") # enter username

password = driver.find_element_by_id("fr24_SignInPassword")
password.send_keys("") # enter password

element = driver.find_element_by_css_selector(".btn.btn-blue")

element.click()

time.sleep(3)

driver.switch_to.window(driver.window_handles[-1])

# for Ben-Gurion airport, choose 'tlv' in the urls of arrivals & departures

airport_id = '' # need to be written

urls = ['https://www.flightradar24.com/data/airports/tlv/arrivals',
        'https://www.flightradar24.com/data/airports/tlv/departures']

for url in urls:

    driver.get(url)

    time.sleep(3)

    # first click on the "Load earlier flights" button until all records are loaded

    element = driver.find_element_by_css_selector(".btn.btn-table-action.btn-flights-load")

    load_button_still_clickable = True

    while load_button_still_clickable is not None:
        try:
            element.click()
        except:
            load_button_still_clickable = None

    # then save the dates of the flights (suppose to be only 2 days)

    elements = driver.find_elements_by_css_selector(".row-date-separator.hidden-xs.hidden-sm")

    for index, date in enumerate(elements):
        # parse dates to remove the name of the day, then save to dates
        date_text = date.text
        dates.append(date_text[date_text.index(',') + 2:])  # plus 2 to past the ',' and space (' ')

    # now save all flight numbers

    elements = driver.find_elements_by_css_selector(".p-l-s.cell-flight-number")

    for flight_num in elements:
        flights_numbers.append(flight_num.text)

    driver.switch_to.window(driver.window_handles[-1])  # instead of: driver.quit()

# same flight number can appear both in arrivals and in departures,
# by making a set out of the flight_numbers we remove the duplicates
# same for the dates

flights_numbers = set(flights_numbers)

print 'Number of Flights: {0} , Flights_Numbers: {1}'.format(len(flights_numbers), flights_numbers)

dates = set(dates)

print 'Dates: {0}'.format(dates)

min_date = get_minimum_date(list(dates))

# now after we have the flights numbers, we need to download their CSV's,
# we will do that by opening the flight page, iterate over all records, and match each record with our dates,
# if the record's date matches to one of the dates we found before, we download its CSV

for flight_num in flights_numbers:

    try:
        # driver = webdriver.Chrome(os.getcwd() + '\chromedriver.exe')

        driver.get('https://www.flightradar24.com/data/flights/' + flight_num)

        # time.sleep(3)
        driver.implicitly_wait(5)

        # first loop is to determine the gap in y axis between the first record and its csv button,
        # (calculating the substraction: button.location['y'] - record.location['y'] )

        button_y = 0

        gap = 0

        csv_buttons = driver.find_elements_by_css_selector(
            ".btn.btn-sm.btn-white.btn-table-action.fs-10.csvButton.notranslate.downloadCsv")

        for button in csv_buttons:

            if button.text == 'CSV' and button.location['y'] != 0:
                button_y = button.location['y']

                break

        elements = driver.find_elements_by_css_selector(".ng-scope")

        for record in elements:

            if abs(record.location['y'] - button_y) <= 10:
                gap = abs(record.location['y'] - button_y)

                break

        records_y_locations = []

        # store only the right records (their date appear in dates)

        elements = driver.find_elements_by_css_selector(".ng-scope")

        for record in elements:

            condition = 'Tel Aviv (TLV)' in record.text and len(record.text) < 200

            if condition and parse_date(record.text) in dates:
                records_y_locations.append(record.location['y'])

            if condition:

                if record_date_to_datetime(parse_date(record.text)) < min_date:
                    break

        max_y_value = 0 if len(records_y_locations) == 0 else get_max_y_value(records_y_locations)

        # iterate over CSV's, for each check if the parent's (the record containing the CSV) id appear in record_ids

        flights_counter = 0

        if max_y_value != 0:

            for button in csv_buttons:

                if button.text == 'CSV' and button.location['y'] - gap in records_y_locations:

                    button.click()

                    flights_counter += 1

                    if max_y_value < button.location['y']:
                        break

                    time.sleep(2)

                    # time.sleep(3)  # give the browser time to start the download

        print 'Flight: {0} , Number of Flights: {1}\n'.format(flight_num, flights_counter)

        driver.switch_to.window(driver.window_handles[-1])  # instead of: driver.quit()

    except Exception, e:
        print "failed parsing flight: {0}, error is: {1}\n".format(flight_num, str(e))
        continue

driver.quit()
