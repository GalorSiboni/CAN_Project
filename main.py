import can
from random import randint
import time
import datetime
import logging

logging.basicConfig(filename='CanLog.log', level=logging.INFO)

# const id options array
CONST_ID_OPTIONS_ARRAY = [0x100, 0x200, 0x300]

# store the last CAN message frame arrival time
last_arrival = time.time()

# Store the last CAN message DLC for each arbitration id
id_dlc_dict = {}

# Current CAN frame indicator
frame_counter = 0

# Store the last CAN message data for each arbitration id
id_data_dict = {}


def rate_validation():
    global last_arrival
    rate = time.time() - last_arrival
    last_arrival = time.time()
    if rate > 0.1:
        return 1
    return 0


def length_validation(msg):
    global id_dlc_dict
    if id_dlc_dict.get(msg.arbitration_id) is not None:
        if id_dlc_dict.get(msg.arbitration_id) == msg.dlc:
            return 1

    else:
        id_dlc_dict[msg.arbitration_id] = msg.dlc
    return 0


def data_validation(msg):
    global id_data_dict
    int_values = [x for x in msg.data]

    if id_data_dict.get(msg.arbitration_id) is not None:
        for i in range(msg.dlc):
            if int_values[i] == id_data_dict.get(msg.arbitration_id)[i]:
                id_data_dict[msg.arbitration_id] = int_values
                return 1

    else:
        id_data_dict[msg.arbitration_id] = int_values
    return 0


def invalid_reason_checker(invalid_array):
    invalidReason = ""
    if invalid_array[0] == 1 and invalid_array[1] == 0 and invalid_array[2] == 0:
        return invalidReason + "Rate"
    elif invalid_array[0] == 1 and invalid_array[1] == 1 and invalid_array[2] == 0:
        return invalidReason + "Rate and Length"
    elif invalid_array[0] == 1 and invalid_array[1] == 0 and invalid_array[2] == 1:
        return invalidReason + "Rate and Data"
    elif invalid_array[0] == 1 and invalid_array[1] == 1 and invalid_array[2] == 1:
        return invalidReason + "Rate, Length and Data"
    elif invalid_array[0] == 0 and invalid_array[1] == 1 and invalid_array[2] == 0:
        return invalidReason + "Length"
    elif invalid_array[0] == 0 and invalid_array[1] == 1 and invalid_array[2] == 1:
        return invalidReason + "length and Data"
    else:
        return invalidReason + "Data"


def generator_unit():
    global frame_counter, CONST_ID_OPTIONS_ARRAY

    random_bytearray = []

    # Initialize the data array length between 0-8 bytes to a random number between 0 - ((2^8) -1)  => Byte size
    # and fill all the other data field to be constant "1"
    bytearray_size = randint(0, 8)
    for i in range(bytearray_size):
        random_bytearray.append(randint(0, 255))  # 255 = 2^8 - 1

    # fill all the other data field to be constant "1"
    if bytearray_size != 8:
        for j in range(bytearray_size, 8):
            random_bytearray.append(1)

    # Create the CAN message
    can_msg = can.Message(arbitration_id=CONST_ID_OPTIONS_ARRAY[randint(0, 2)], dlc=bytearray_size,
                          data=random_bytearray, is_extended_id='False')
    print("Frame {}: Message id: {},Data: {} , DLC:{}".format(frame_counter, can_msg.arbitration_id,
                                                              [x for x in can_msg.data], can_msg.dlc))
    return can_msg


def detection_unit(msg):
    invalid_array = [0, 0, 0]

    # Set frame arrival timestamp
    msg.timestamp = datetime.datetime.now()

    # Rate Validation
    invalid_array[0] = rate_validation()

    # Length Validation
    invalid_array[1] = length_validation(msg)

    # Data Validation
    invalid_array[2] = data_validation(msg)

    return [msg, invalid_array]


def reporting_unit(results):  # results[0] contain the CAN message & results[1] contain the invalidation array
    global frame_counter

    can_msg = results[0]

    # Convert the CAN.data byte array to hexadecimal presentation
    hexData = can_msg.data.hex()

    if 1 in results[1]:
        invalidReason = invalid_reason_checker(results[1])
        logging.error('Frame %s,%s,%s,%s,%s', frame_counter, str(can_msg.timestamp), str(hexData), "Invalid", invalidReason)
    else:
        logging.info('%s,%s,%s', str(can_msg.timestamp), str(hexData), "Valid")

    # Sleep for random period time of 50mSec to 100 mSec.
    time.sleep(randint(5, 10) / 100)


while True:
    reporting_unit(detection_unit(generator_unit()))
    frame_counter += 1
