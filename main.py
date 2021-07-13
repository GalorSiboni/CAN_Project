import can
from random import randint
import time
last_arival = time.time()
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
    global last_arival
    rate = time.time() - last_arival
    if rate <= 0.1:
        invalid_array[0] = 1
    last_arival = time.time()
    if invalid_array[0] == 1:
        print("Valid!")
    else:
        print("Invalid - rate: {}".format(rate))
    time.sleep(randint(5, 10)/100)

while True:
    detection_unit(generator_unit(frame_counter))
 #   generator_unit(frame_counter)
    frame_counter += 1
