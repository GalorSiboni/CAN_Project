import can
from random import randint
import time
last_arival = time.time()
last_dlc_per_id_array = [-1, -1, -1]
frame_counter = 0
def generator_unit(frame_counter):
    id_option_array = [0x100, 0x200, 0x300]
    random_bytearray = []
    bytearray_size = randint(0, 8)
    for i in range(bytearray_size):
        random_bytearray.append(1)
    can_msg = can.Message(arbitration_id=id_option_array[randint(0, 2)], data=random_bytearray, is_extended_id='False')
    try:
        print("Frame {}: Message id: {},Data: {} , DLC:{} , TimeStamp:{}".format(frame_counter, can_msg.arbitration_id, can_msg.data, can_msg.dlc, can_msg.timestamp))
    except can.CanError:
        print("cannot print the Message")
    return can_msg

def detection_unit(msg):
    invalid_array = [0, 0, 0]
    global last_arival, last_dlc_per_id_array

    # Rate Validation
    rate = time.time() - last_arival
    if rate > 0.1:
        invalid_array[0] = 1
    last_arival = time.time()

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
    if invalid_array[0] == 0:
        print("Rate is Valid!")
    else:
        print("Rate Invalid - rate: {}".format(rate))

    if invalid_array[1] == 0:
        print("Length is Valid!")
    else:
        print("Length Invalid - length is equal to the previous frame carrying the same ID")

    time.sleep(randint(5, 10)/100)

while True:
    detection_unit(generator_unit(frame_counter))
    frame_counter += 1
