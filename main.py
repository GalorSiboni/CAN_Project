import can
from random import randint
import time
import datetime
import logging

logging.basicConfig(filename='CanLog.log', level=logging.INFO)
last_arrival = time.time()
last_dlc_per_id_array = [-1, -1, -1]
frame_counter = 0

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
    global frame_counter
    id_option_array = [0x100, 0x200, 0x300]
    random_bytearray = []
    bytearray_size = randint(0, 8)
    for i in range(bytearray_size):
        random_bytearray.append(1)
    can_msg = can.Message(arbitration_id=id_option_array[randint(0, 2)], data=random_bytearray, is_extended_id='False')
    print("Frame {}: Message id: {},Data: {} , DLC:{}".format(frame_counter, can_msg.arbitration_id, can_msg.data,
                                                              can_msg.dlc))

    return can_msg


def detection_unit(msg):
    invalid_array = [0, 0, 0]
    global last_arrival, last_dlc_per_id_array

    # Frame's arrival timestamp
    msg.timestamp = datetime.datetime.now()

    # Rate Validation
    rate = time.time() - last_arrival
    if rate > 0.1:
        invalid_array[0] = 1
    last_arrival = time.time()

    # Length Validation
    if msg.arbitration_id == 0x100 and msg.dlc == last_dlc_per_id_array[0]:
        invalid_array[1] = 1
    elif msg.arbitration_id == 0x200 and msg.dlc == last_dlc_per_id_array[1]:
        invalid_array[1] = 1
    elif msg.arbitration_id == 0x300 and msg.dlc == last_dlc_per_id_array[2]:
        invalid_array[1] = 1
    else:
        if msg.arbitration_id == 0x100:
            last_dlc_per_id_array[0] = msg.dlc
        elif msg.arbitration_id == 0x200:
            last_dlc_per_id_array[1] = msg.dlc
        else:
            last_dlc_per_id_array[2] = msg.dlc

    # Data Validation

    # Validation result print
    if invalid_array[0] == 0:
        print("Rate is Valid!")
    else:
        print("Rate Invalid - rate: {}".format(rate))

    if invalid_array[1] == 0:
        print("Length is Valid!")
    else:
        print("Length Invalid - length is equal to the previous frame carrying the same ID")
    return [msg, invalid_array]


def reporting_unit(results):  # results[0] contain the CAN message & results[1] contain the invalidation array
    global frame_counter
    can_msg = results[0]
    hexData = can_msg.data.hex()
    if 1 in results[1]:
        invalidReason = invalid_reason_checker(results[1])
        logging.error('Frame %s: Timestamp: %s, Frame: %s, Frame Validation: %s, %s', str(frame_counter),
                      str(can_msg.timestamp), str(hexData), "Invalid", invalidReason)
    else:
        logging.info('Frame %s: Timestamp: %s, Frame: %s, Frame Validation:%s', str(frame_counter),
                     str(can_msg.timestamp), str(hexData), "Valid")
    time.sleep(randint(5, 10) / 100)

while True:
    reporting_unit(detection_unit(generator_unit()))
    frame_counter += 1
