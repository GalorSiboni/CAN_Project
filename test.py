import time
import unittest

import can

from main import length_validation, data_validation, rate_validation, invalid_reason_checker, id_dlc_dict, id_data_dict


class TestLength(unittest.TestCase):
    def test_rate(self):
        """
        Test that it can valid the rate
        """
        time.time()
        time.sleep(10 / 100)
        result = rate_validation()
        time.time()
        time.sleep(5 / 100)
        result2 = rate_validation()
        self.assertEqual(result, 0)
        self.assertEqual(result2, 1)

    def test_frame_length(self):
        """
        Test that it can valid the length of a data field
        """
        data = [2, 2, 3, 4, 5, 6, 7, 27]
        id_dlc_dict[0x100] = 7
        id_dlc_dict[0x200] = 8
        msg1 = can.Message(arbitration_id=0x100, data=data, dlc=len(data))
        msg2 = can.Message(arbitration_id=0x200, data=data, dlc=len(data))
        result = length_validation(msg1)
        result2 = length_validation(msg2)
        self.assertEqual(result, 0)
        self.assertEqual(result2, 1)

    def test_frame_data_field(self):
        """
        Test that it can Valid the data field
        """
        data = [2, 2, 3, 4, 5, 6, 7, 27]
        data2 = [13, 12, 13, 14, 15, 16, 17, 127]
        data3 = [13, 12, 13, 14, 15, 16, 7, 127]

        id_data_dict[0x100] = data
        id_data_dict[0x200] = data

        msg1 = can.Message(arbitration_id=0x100, data=data2)
        msg2 = can.Message(arbitration_id=0x200, data=data3)

        result = data_validation(msg1)
        result2 = data_validation(msg2)

        self.assertEqual(result, 0)
        self.assertEqual(result2, 1)

    def test_invalid_reason_checker(self):
        """
        Test that it can return the right reason for invalidation
        """

        result = invalid_reason_checker(invalid_array=[1, 0, 0])  # Rate
        result2 = invalid_reason_checker(invalid_array=[0, 1, 0])  # Length
        result3 = invalid_reason_checker(invalid_array=[0, 0, 1])   # Data
        result4 = invalid_reason_checker(invalid_array=[1, 1, 0])   # Rate and Length
        result5 = invalid_reason_checker(invalid_array=[1, 0, 1])   # Rate and Data
        result6 = invalid_reason_checker(invalid_array=[0, 1, 1])   # Length and Data
        result7 = invalid_reason_checker(invalid_array=[1, 1, 1])   # Rate, Length and Data

        self.assertEqual(result, "Rate")
        self.assertEqual(result2, "Length")
        self.assertEqual(result3, "Data")
        self.assertEqual(result4, "Rate and Length")
        self.assertEqual(result5, "Rate and Data")
        self.assertEqual(result6, "Length and Data")
        self.assertEqual(result7, "Rate, Length and Data")


if __name__ == '__main__':
    unittest.main()
