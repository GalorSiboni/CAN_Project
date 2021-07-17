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
last_dlc_per_id_array = [-1] * len(CONST_ID_OPTIONS_ARRAY)

# Current CAN frame indicator
frame_counter = 0


def rate_validation():
    global last_arrival
    rate = time.time() - last_arrival
    last_arrival = time.time()
    if rate > 0.1:
        return 1
    return 0


def length_validation(msg):
    global last_dlc_per_id_array

    # I always save the last message DLC value at a global array call last_dlc_per_id_array that is being initialize
    # at size of arbitration id options(3 in are case- 0x100, 0x200 and 0x300) with -1 (invalid value)
    if (msg.arbitration_id == 0x100 and msg.dlc == last_dlc_per_id_array[0]) or (
            msg.arbitration_id == 0x200 and msg.dlc == last_dlc_per_id_array[1]) or (
            msg.arbitration_id == 0x300 and msg.dlc == last_dlc_per_id_array[2]):
        return 1
    else:
        if msg.arbitration_id == 0x100:
            last_dlc_per_id_array[0] = msg.dlc
        elif msg.arbitration_id == 0x200:
            last_dlc_per_id_array[1] = msg.dlc
        else:
            last_dlc_per_id_array[2] = msg.dlc
    return 0

# TODO
def data_validation():
    return 0


def invalid_reason_checker(invalid_array):
    invalidReason = "Invalid values: "
    if invalid_array[0] == 1 and invalid_array[1] == 0 and invalid_array[2] == 0:
        return invalidReason + "rate"
    elif invalid_array[0] == 1 and invalid_array[1] == 1 and invalid_array[2] == 0:
        return invalidReason + "rate and length"
    elif invalid_array[0] == 1 and invalid_array[1] == 0 and invalid_array[2] == 1:
        return invalidReason + "rate and data"
    elif invalid_array[0] == 1 and invalid_array[1] == 1 and invalid_array[2] == 1:
        return invalidReason + "rate, length and data"
    elif invalid_array[0] == 0 and invalid_array[1] == 1 and invalid_array[2] == 0:
        return invalidReason + "length"
    elif invalid_array[0] == 0 and invalid_array[1] == 1 and invalid_array[2] == 1:
        return invalidReason + "length and data"
    else:
        return invalidReason + "data"


def generator_unit():
    global frame_counter, CONST_ID_OPTIONS_ARRAY

    random_bytearray = []

    # Initialize the data array length between 0-8 bytes and set all values to be equal 1
    bytearray_size = randint(0, 8)
    for i in range(bytearray_size):
        random_bytearray.append(1)

    # Create the CAN message
    can_msg = can.Message(arbitration_id=CONST_ID_OPTIONS_ARRAY[randint(0, 2)], data=random_bytearray,
                          is_extended_id='False')
    print("Frame {}: Message id: {},Data: {} , DLC:{}".format(frame_counter, can_msg.arbitration_id, can_msg.data,
                                                              can_msg.dlc))

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
    invalid_array[2] = data_validation()

    return [msg, invalid_array]


def reporting_unit(results):  # results[0] contain the CAN message & results[1] contain the invalidation array
    global frame_counter

    can_msg = results[0]

    # Convert the CAN.data byte array to hexadecimal presentation
    hexData = can_msg.data.hex()

    if 1 in results[1]:
        invalidReason = invalid_reason_checker(results[1])
        logging.error('Frame %s: Timestamp: %s, Frame: %s, Frame Validation: %s, %s', str(frame_counter),
                      str(can_msg.timestamp), str(hexData), "Invalid", invalidReason)
    else:
        logging.info('Frame %s: Timestamp: %s, Frame: %s, Frame Validation:%s', str(frame_counter),
                     str(can_msg.timestamp), str(hexData), "Valid")

    # Sleep for random period time of 50mSec to 100 mSec.
    time.sleep(randint(5, 10) / 100)


while True:
    reporting_unit(detection_unit(generator_unit()))
    frame_counter += 1
