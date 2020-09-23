"""
IS590 PR - Assignment 3
Group: Team 05
Author: Yi Hsuan Liao (yhliao4) 661311697
        Cheng Chen Yang (ccy3) 657920840
We discussed the steps and worked together through each questions via zoom.
"""
# Import Library
from geographiclib.geodesic import Geodesic
geod = Geodesic.WGS84

# Functions


def execute_data(file_name, result):
    """
    This is the main function to process storm data and the function will call other functions.
    :param file_name: name of the text file
    :param result: empty dictionary for putting results
    """
    # open the file
    with open(file_name, 'r') as f:
        # initiate the dictionary for each of the storm
        hurdat_dic = new_hurdat_dic()
        how_many_line = 0
        for line in f:
            if line[0].isalpha():  # check if it is a storm name
                hurdat_dic["Storm_Id"] = line[0:8]  # make id column
                hurdat_dic["Storm_Name"] = line[19:28].replace(" ", "")
                how_many_line = int(line[33:36])
                continue

            # count the lines
            how_many_line -= 1
            # latitude and longitude
            latitude = get_latitude(line)
            longitude = get_longitude(line)
            # wind degree
            hurdat_dic["degree"] = cal_degree(hurdat_dic, latitude, longitude)
            # find if the result of adding offset degree falls into the quadrant of the strongest wind
            true_or_false(hurdat_dic, line)
            # total distance
            distance = cal_distance(hurdat_dic, latitude, longitude)
            hurdat_dic["Distance"].append(distance)
            # current latitude
            hurdat_dic["latitude"] = latitude
            hurdat_dic["longitude"] = longitude
            # current year
            year_date = line[0:8]
            # current time
            time_now = line[10:14]
            # start date of the storm
            if hurdat_dic["First_Date"] is None:
                hurdat_dic["First_Date"] = year_date[4:8]

            # hour
            hour = cal_time(hurdat_dic, year_date, time_now)
            hurdat_dic["New_Time_List"].append(hour)
            # speed (and round it)
            speed = round(cal_speed(distance, hour), 2)
            hurdat_dic["Speed"].append(speed)
            # current date and time
            hurdat_dic["year_date"] = year_date
            hurdat_dic["time_now"] = time_now

            # new start after each storm ends
            if how_many_line == 0:
                # set the key for result_dic
                new_storm_id = hurdat_dic["Storm_Id"] + hurdat_dic["First_Date"] + hurdat_dic["Storm_Name"]
                # calculate average speed
                if len(hurdat_dic["New_Time_List"]) > 1:
                    avg_speed = round((sum(hurdat_dic["Distance"]) / sum(hurdat_dic["New_Time_List"])), 2)
                else:
                    avg_speed = 0.0
                # add information to result_dic
                if new_storm_id not in result:
                    result[new_storm_id] = [
                        hurdat_dic["Storm_Id"],
                        hurdat_dic["Storm_Name"],
                        round(sum(hurdat_dic["Distance"]), 2),
                        round(max(hurdat_dic["Speed"]), 2),
                        avg_speed,
                    ]
                # initialize hurdat_dic to record the next storm
                hurdat_dic = new_hurdat_dic()


def cal_distance(h_dic, latitude, longitude):
    """
    Calculate the distance from last row to current row.
    :param h_dic: dictionary for putting the storm data
    :param latitude: latitude of current row
    :param longitude: longitude of current row
    :return: distance: the result
    """
    last_latitude = h_dic["latitude"]
    last_longitude = h_dic["longitude"]

    if (last_latitude or last_longitude) == 0:
        return 0.0
    distance = round(geod.Inverse(last_latitude, last_longitude, latitude, longitude)['s12'] / 1852.0, 2)
    return distance


def get_latitude(line):
    """
    Get the latitude and convert string to float.
    :param line: latitude data of the storm
    :return: latitude
    """
    # if the latitude has "N" mark as positive, "S" mark as negative
    if line[27: 28] == "N":
        north = 1
    elif line[27: 28] == "S":
        north = -1
    else:
        return 0.0
    latitude = float(line[23:27]) * north
    return latitude


def get_longitude(line):
    """
    Get the longitude and convert string to float.
    :param line: longitude data of the storms
    :return: longitude
    """
    # if the longitude has "E" mark as positive, "W" mark as negative
    if line[35: 36] == "E":
        east = 1
    elif line[35: 36] == "W":
        east = -1
    else:
        return 0.0
    longitude = float(line[30:35]) * east
    return longitude


def cal_time(h_dic, year_date, time_now):
    """
    Calculate time between each row.
    :param h_dic: dictionary for putting the storm data
    :param year_date: date
    :param time_now: time
    :return: hour
    """
    last_date = h_dic["year_date"]
    last_time = h_dic["time_now"]
    if int(last_date) == 0:
        return 0
    this_hour = int(time_now[0:2])
    this_min = int(time_now[2:4])
    last_hour = int(last_time[0:2])
    last_min = int(last_time[2:4])
    # then calculate the time
    hour = (this_hour - last_hour) + (this_min - last_min) / 60

    if year_date != last_date:
        hour += 24
    return hour


def cal_speed(distance, hour):
    """
    Calculate the speed. (distance/hour)
    :param distance: distance we get previously
    :param hour: time we calculated previously
    :return: speed
    """
    if hour == 0:  # the division cannot be 0
        return 0
    speed = distance / hour
    return speed


def new_hurdat_dic():
    """
    Reset the storm dictionary.
    :return: huradat_dic
    """
    h_dic = {
        "Storm_Id": None,  # set a default
        "Storm_Name": "UNNAMED",
        "Wind_Speed": 0,
        "First_Date": None,
        "latitude": 0,
        "longitude": 0,
        "Distance": [],
        "year_date": 0,
        "time_now": 0,
        "New_Time_List": [],
        "Speed": [],
    }
    return h_dic


def cal_degree(h_dic, latitude, longitude):
    """
    Calculate degree difference from last row to current row.
    :param h_dic: dictionary for putting the storm data
    :param latitude: latitude (current row)
    :param longitude: longitude (current row)
    :return: degree
    """
    last_latitude = h_dic["latitude"]
    last_longitude = h_dic["longitude"]
    degree = geod.Inverse(last_latitude, last_longitude, latitude, longitude)['azi2']
    if degree < 0:
        degree += 360  # make all the negative degrees into positive value
    return degree


def true_or_false(h_dic, line):
    """
    Get the strongest wind of the four quadrant and check which quadrant the strongest wind lands.
    :param h_dic: dictionary for putting the storm data
    :param line: storm data
    """
    wind_list = []
    if int(line[0:4]) > 2003:  # select data from 2004
        ne = int(line[49:53])  # 1
        se = int(line[55:59])  # 2
        sw = int(line[61:65])  # 3
        nw = int(line[67:71])  # 4
        if ((ne and se and sw and nw) != 0) and ((ne and se and sw and nw) != -999):
            wind_list.append(ne)
            wind_list.append(se)
            wind_list.append(sw)
            wind_list.append(nw)
            wind_max = 0
            # find the largest wind of the four quadrant
            for w in wind_list:
                if w > wind_max:
                    wind_max = w
            for d in range(360):  # check all the degrees
                check_degree = h_dic["degree"] + d  # check which quadrant the strongest wind lands
                if check_degree >= 360:
                    check_degree -= 360
                if 0 <= check_degree < 90:
                    check = 1  # if lands in first quadrant
                elif 90 <= check_degree < 180:
                    check = 2
                elif 180 <= check_degree < 270:
                    check = 3
                else:
                    check = 4

                if wind_list[check - 1] == wind_max:
                    cnt_tf[d][1] += 1  # if True, add 1 to [1]
                else:
                    cnt_tf[d][0] += 1  # if False, add 1 to [0]
    return


def output_result(result):
    """
    Output the result into text file.
    :param result: result dictionary
    """
    file1 = open("Assignment3_Result_Team05.txt", "w")
    print('Assignment_3 \n Author: Cheng Chen Yang (ccy3); Yi Hsuan Liao (yhliao4)\n', file=file1)
    print("Question1", file=file1)
    print("  Storm ID      Name  Distance", file=file1)
    for storm in result:
        print(
            "{0:>10s}{1:>10s}{2:10.2f}".format(result[storm][0], result[storm][1],
                                               result[storm][2]), file=file1)
    print("\nQuestion2", file=file1)
    print("  Storm ID      Name Max Speed Avg Speed", file=file1)
    for storm in result:
        print("{0:>10s}{1:>10s}{2:10.2f}{3:10.2f}".format(result[storm][0], result[storm][1],
                                                          result[storm][3], result[storm][4]), file=file1)
    print("\nQuestion3", file=file1)
    print("Degree Offset", "% Segments Supporting Hypothesis", file=file1)
    for key in cnt_tf:
        if cnt_tf[key][0] == 0:
            print("0", file=file1)
        else:
            print("{0:^13d}{1:^32.2f}".format(key, (cnt_tf[key][1] / (cnt_tf[key][1] + cnt_tf[key][0])) * 100),
                  file=file1)
    file1.close()


# Execute program


if __name__ == '__main__':
    result_dic = {}
    cnt_tf = {}
    # set values to zero
    for i in range(360):
        cnt_tf[i] = [0, 0]
    # run the storm data
    execute_data("hurdat2-1851-2019-052520.txt", result_dic)
    execute_data("hurdat2-nepac-1949-2019-042320.txt", result_dic)

    # output answers for question 1, 2, and 3
    output_result(result_dic)
