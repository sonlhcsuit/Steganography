import numpy as np
import cv2
import sys
import os
from more_itertools import grouper
from ultis import char_to_8_bit_string, int_to_8_bit_string, int_to_16_bit_string, change_lsb, get_lsb

MESSAGE = 'MESSAGE'
IMAGE = 'IMAGE'


class Steganography:
    def __init__(self, container_path, delimiter='!@!@!'):
        if container_path is None:
            raise Exception("Must provide the container image path!")
        self.container = container_path
        self.delimiter = delimiter

    def is_encodable(self, data: str, type: str = MESSAGE) -> bool:
        container_len: int = os.path.getsize(self.container)
        if type == MESSAGE:
            # Check whether a text can be encoded into a image
            delimiter_len = sys.getsizeof(self.delimiter)
            data_len = delimiter_len * 4 + sys.getsizeof(data)

        elif type == IMAGE:
            # Check whether an image can be encoded into a image
            delimiter_len = sys.getsizeof(self.delimiter)
            data_len = delimiter_len * 4 + os.path.getsize(data)
        else:
            raise Exception(f"File type \"{type}\" isn't supported!")
        return container_len >= 4 * data_len

    def encode(self, data: str, type: str) -> np.ndarray:
        """
        :param data: data to be encoded into the container str. If type is MESSAGE, data is the message. If type is IMAGE,
        data is the image path as string
        :param type: type of data. IMAGE or MESSAGE
        :return: an encoded container image as numpy 3d-array

        using 2 bits of each channel(3 channels) to hide data -> 6 bits of n-bits-message per pixel.
        1 pixel is 3-bytes(24 bits) so the max size of message length stored is:
        w * h * 24*0.25 - size(delimiter)*2
        delimiter ( default is '@@@@@') symbols is required.
        Example: If we have an 512x512 image, we can hide an 196598-letters-string into it.
        (512x512x8x3x0.25 - 10*8)/8
        """
        print("Checking compatible...")
        if not self.is_encodable(data=data, type=type):
            raise Exception("Cannot encoding data into container, size of message exceed limit")
        print("Starting encode data...")
        container_image: np.ndarray = cv2.imread(self.container)
        container_image_flatten = container_image.reshape(-1)
        bits_data = []
        if type == IMAGE:
            # read image & container, process shape, flat
            image_path = os.path.join(os.getcwd(), data)
            image: np.ndarray = cv2.imread(image_path)
            image_flatten = image.reshape(-1)
            image_shape = image.shape

            # encode delimiter for determine which bits-sequence to chose
            delimiter = np.array(list(map(char_to_8_bit_string, self.delimiter)))
            delimiter = np.array(np.vectorize(lambda x: int(x, base=2))(delimiter))
            # also encode shape to reconstruct
            shape = np.array(image_shape)
            shape = np.vectorize(int_to_16_bit_string)(shape)

            # concatenate into a long bits_sequence included: delimiter,shape,IMAGE,delimiter
            bits_data: np.ndarray = np.concatenate((
                np.vectorize(int_to_8_bit_string)(delimiter),
                shape,
                np.vectorize(int_to_8_bit_string)(image_flatten),
                np.vectorize(int_to_8_bit_string)(delimiter)))

            # Start chunking into array of 2bit
        elif type == MESSAGE:
            # delimiter
            delimiter = np.array(list(map(char_to_8_bit_string, self.delimiter)))
            delimiter = np.array(np.vectorize(lambda x: int(x, base=2))(delimiter))

            # data-len (image shape)
            shape = np.array([len(data)])
            # the message as string
            bits_data = np.array(list(map(char_to_8_bit_string, data)))
            bits_data = np.array(np.vectorize(lambda x: int(x, base=2))(bits_data))

            bits_data: np.ndarray = np.concatenate((
                np.vectorize(int_to_8_bit_string)(delimiter),
                np.vectorize(int_to_16_bit_string)(shape),
                np.vectorize(int_to_8_bit_string)(bits_data),
                np.vectorize(int_to_8_bit_string)(delimiter)))

        else:
            raise Exception(f"Expected IMAGE or MESSAGE but got{type}")

        chunks = list(''.join(bits_data.tolist()))
        chunks: list = list(grouper(chunks, 2, '0'))
        chunks: list = list(map(lambda chunk: int(''.join(chunk), base=2), chunks))
        chunks: np.ndarray = np.array(chunks)

        # right shift 2 bits, then left shift 2 bits (remove data), then plus => change 2 lsb
        # replace 2 lsb by 2bit of message to be encoded
        vf = np.vectorize(change_lsb)
        encoded_chunks: np.ndarray = container_image_flatten[:len(chunks)]
        encoded_chunks = vf(encoded_chunks, chunks)
        container_image_flatten[:len(chunks)] = encoded_chunks

        return container_image.copy()

    def decode(self, type=MESSAGE) -> np.ndarray:
        """
        :param type: type of hidden data. If type is MESSAGE, decoded data is message as string. If tyoe is IMAGE, data is image as 3d numpy array
        :return: encoded data
        """
        print("Preprocessing image...")
        encoded_image: np.ndarray = cv2.imread(self.container)
        encoded_image_flatten = encoded_image.reshape(-1)

        print("Starting decode data...")
        # check maybe first is our delimiter

        delimiter_len = len(self.delimiter)
        print('Checking delimiter')
        delimiter: np.ndarray = encoded_image_flatten[:(8 * delimiter_len) // 2]
        delimiter = np.vectorize(get_lsb)(delimiter)
        delimiter: list = delimiter.tolist()
        delimiter: list = list(map(lambda x: format(x, '02b'), delimiter))
        delimiter: str = ''.join(delimiter)
        delimiter: str = ''.join(self.bits_sequence_to_string(delimiter))
        if not delimiter == self.delimiter:
            raise Exception("Cannot decode by invalid encoding format")
        print('Delimiter is correct!\nExtracting data...')
        if type == IMAGE:
            # next 6 byte is about the shape
            # width, height, 3channel => 2 bytes => 6 bytes
            shape_len = 6
            shape: np.ndarray = encoded_image_flatten[(8 * delimiter_len) // 2: (8 * delimiter_len + shape_len * 8) // 2]
            shape = np.vectorize(get_lsb)(shape)
            # divide by 2 as we use 2 lsb
            shape: list = shape.tolist()
            shape: list = list(map(lambda x: format(x, '02b'), shape))
            shape: str = ''.join(shape)
            shape_tup: tuple = (int(shape[0:16], base=2), int(shape[16:32], base=2), int(shape[32:48], base=2))

            # extract data bits_sequence
            data_len = shape_tup[0] * shape_tup[1] * shape_tup[2]

            data: np.ndarray = encoded_image_flatten[(8 * delimiter_len + shape_len * 8) // 2:
                                             (8 * delimiter_len + shape_len * 8 + data_len * 8) // 2]
            data = np.vectorize(get_lsb)(data)
            data: list = data.tolist()
            data: list = list(map(lambda x: format(x, '02b'), data))
            data: str = ''.join(data)
            data: list = list(grouper(data, 8, 0))
            data: list = list(map(lambda x: int(''.join(x), base=2), data))
            data: np.ndarray = np.array(data)
            data = data.reshape(shape_tup[0], shape_tup[1], shape_tup[2])
            return data.copy()
        elif type == MESSAGE:
            shape_len = 2
            shape = encoded_image_flatten[(8 * delimiter_len) // 2: (8 * delimiter_len + shape_len * 8) // 2]
            shape = np.vectorize(get_lsb)(shape)
            shape: list = shape.tolist()
            shape: list = list(map(lambda x: format(x, '02b'), shape))
            shape: str = ''.join(shape)
            data_len: int = int(shape, base=2)
            data = encoded_image_flatten[(8 * delimiter_len + shape_len * 8) // 2:
                                         (8 * delimiter_len + shape_len * 8 + data_len * 8) // 2]
            data = np.vectorize(get_lsb)(data)
            data: list = data.tolist()
            data: list = list(map(lambda x: format(x, '02b'), data))
            data: str = ''.join(data)
            data: str = ''.join(self.bits_sequence_to_string(data))

            return data

        else:
            raise Exception(f'Cannot decoding due to some stupid reason =]]]]')

    @staticmethod
    def bits_sequence_to_string(bit_sequence: str):
        """
        Convert a bit_sequence to string.
        example: '01100011_01110110_00110010_01000000' -> 'cv2@'  (no underscore)
        :param bit_sequence: bit_sequence to be converted
        :return: The message decoded ('cv2@')
        """
        # Chunking
        chunks = list(grouper(bit_sequence, 8, '0'))
        chunks = list(map(lambda chunk: chr(int(''.join(chunk), base=2)), chunks))
        message = ''.join(chunks)
        return message

    @staticmethod
    def string_to_bits_sequence(string):
        """
        Convert a string to bit_sequence.
        example: 'cv2@' -> '01100011_01110110_00110010_01000000'  (no underscore)
        :param string: the string message
        :return: bit_sequence converted
        """
        if type(string) == str:
            chunks = list(map(char_to_8_bit_string, string))
            return ''.join(chunks)
        raise Exception('Cannot convert string to bit')

    @staticmethod
    def save(data, option_type, path):
        if option_type == MESSAGE:
            f = open('{}.txt'.format(path), "w")
            f.write(data)
        elif option_type == IMAGE:
            cv2.imwrite("{}.png".format(path), data)
        print("Saving successful!")
