import numpy as np
import cv2,sys,os
from ultis import char_to_8_bit_string

from more_itertools import grouper

origin = 'original_image.jpeg'
to_be_hidden_image = 'to_be_hidden_image.jpeg'
encoded_image = 'encoded_image.png'

to_be_decoded_image = 'to_be_decoded_image.png'
hidden_image = 'hidden_image.png'
lena = 'lena.jpg'

MESSAGE = 'MESSAGE'
IMAGE = 'IMAGE'


class Steganography:

    def __init__(self, container_path, delimiter='@@@@@'):
        if container_path is None:
            raise Exception("Must provide the container image path!")
        self.container = container_path
        self.delimiter = delimiter

    def is_encodable(self, data: str, type: str = MESSAGE) -> bool:
        container_len: int = os.path.getsize(self.container)
        if type == MESSAGE:
            # Check whether a text can be encoded into a image
            delimiter_len = sys.getsizeof(self.delimiter)
            data_len = delimiter_len * 2 + sys.getsizeof(data)

        elif type == IMAGE:
            # Check whether an image can be encoded into a image
            delimiter_len = sys.getsizeof(self.delimiter)
            data_len = delimiter_len * 2 + os.path.getsize(data)
        else:
            raise Exception(f"File type \"{type}\" isn't supported!")
        return container_len >= 4 * data_len

    # def encode(self, data:str, type:str):
    #     """
    #     :param data: data to be encoded into the container str. If type is MESSAGE, data is the message. If type is IMAGE, data is the image path as string
    #     :param type: type of data. Im
    #     :return: an container image encoded as numpy 3d-array
    #
    #     using 2 bits of each channel(3 channels) to hide data -> 6 bits of n-bits-message per pixel.
    #     1 pixel is 3-bytes(24 bits) so the max size of message length stored is:
    #     w * h * 24*0.25 - size(delimiter)*2
    #     delimiter ( default is '@@@@@') symbols is required.
    #     Example: If we have an 512x512 image, we can hide an 196598-letters-string into it.
    #     (512x512x8x3x0.25 - 10*8)/8
    #     """
    #     if type == IMAGE:
    #         data = cv2.imread(data)
    #     elif type == MESSAGE:
    #         pass
    #     else:
    #         raise Exception("Type of encoded data is not supported")
    #     print("Checking compatible...", )
    #     if self.is_encodable(type=type, data=data):
    #         print("Compatible!")
    #         print("Starting convert data...")
    #         data_as_bits_string = ""
    #         if type == MESSAGE:
    #             formatted_message = '{starts}{content}{terminals}'.format(starts=self.starts, content=data,
    #                                                                       terminals=self.terminals)
    #             data_as_bits_string = self.letter_to_bits_string(formatted_message)
    #         if type == IMAGE:
    #             imgbit = self.letter_to_bits_string(self.starts)
    #             for line in data:
    #                 for pixel in line:
    #                     a = list(map(self.letter_to_bits_string, pixel))
    #                     imgbit = imgbit + ''.join(a)
    #             imgbit = imgbit + format(data.shape[0], '016b') + format(data.shape[1], '016b')
    #             data_as_bits_string = imgbit + self.letter_to_bits_string(self.terminals)
    #         container_as_bits = self.image_to_bits_string(self.container)
    #         container_length = len(container_as_bits)
    #         data_length = len(data_as_bits_string)
    #         print("Starting encode...")
    #         index = 0
    #         encoded_bits = ''
    #
    #         for a in range(0, container_length, 8):
    #             channel8bits = container_as_bits[a:a + 8]
    #             data2bit = data_as_bits_string[index:index + 2]
    #             index = index + 2
    #             encoded_data = channel8bits[0:6] + data2bit
    #             encoded_bits = encoded_bits + encoded_data
    #             if index == data_length:
    #                 encoded_bits = encoded_bits + container_as_bits[a + 8:]
    #                 break
    #                 # out of data
    #         decoded_img = self.bits_string_to_image(encoded_bits, (self.container.shape[0], self.container.shape[1]))
    #         print("Encoding Successful!")
    #         return decoded_img
    #     else:
    #         raise Exception("Cannot hide data. Using smaller image or less letters")

    # New Code

    def encode(self, data: str, type: str):
        """
        :param data: data to be encoded into the container str. If type is MESSAGE, data is the message. If type is IMAGE, data is the image path as string
        :param type: type of data. Im
        :return: an container image encoded as numpy 3d-array

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

        print("Compatible!")
        print("Starting convert data...")
        data_as_bits_string = ""
        if type == MESSAGE:
            formatted_message = '{starts}{content}{terminals}'.format(starts=self.starts, content=data,
                                                                      terminals=self.terminals)
            data_as_bits_string = self.letter_to_bits_string(formatted_message)
        if type == IMAGE:
            imgbit = self.letter_to_bits_string(self.starts)
            for line in data:
                for pixel in line:
                    a = list(map(self.letter_to_bits_string, pixel))
                    imgbit = imgbit + ''.join(a)
            imgbit = imgbit + format(data.shape[0], '016b') + format(data.shape[1], '016b')
            data_as_bits_string = imgbit + self.letter_to_bits_string(self.terminals)
        container_as_bits = self.image_to_bits_string(self.container)
        container_length = len(container_as_bits)
        data_length = len(data_as_bits_string)
        print("Starting encode...")
        index = 0
        encoded_bits = ''

        for a in range(0, container_length, 8):
            channel8bits = container_as_bits[a:a + 8]
            data2bit = data_as_bits_string[index:index + 2]
            index = index + 2
            encoded_data = channel8bits[0:6] + data2bit
            encoded_bits = encoded_bits + encoded_data
            if index == data_length:
                encoded_bits = encoded_bits + container_as_bits[a + 8:]
                break
                # out of data
        decoded_img = self.bits_string_to_image(encoded_bits, (self.container.shape[0], self.container.shape[1]))
        print("Encoding Successful!")
        return decoded_img

    def decode(self, type):
        """
        :param type: type of hidden data. If type is MESSAGE, decoded data is message as string. If tyoe is IMAGE, data is image as 3d numpy array
        :return: encoded data
        """
        container_as_bits = self.image_to_bits_string(self.container)
        last2bits_data = ''
        print("Starting convert an image to bits-string...")
        for i in range(0, len(container_as_bits), 8):
            last2bits_data = last2bits_data + container_as_bits[i + 6:i + 8]
        # convert last 2 bits data into ascii message
        message = ''
        for i in range(0, len(last2bits_data), 8):
            block = last2bits_data[i:i + 8]
            message += chr(int(block, base=2))

        index = message.find(self.terminals)  # find terminals
        print("Starting decode...")
        if type == IMAGE:
            size = message[index - 4:index]
            width, height = size[0:2], size[2:]

            width = int(''.join([format(ord(char), "08b") for char in width]), base=2)
            height = int(''.join([format(ord(char), "08b") for char in height]), base=2)
            shape = (width, height, 3)
            content = message[5:index - 4]

            data_as_bits = ''.join([format(ord(letter), "08b") for letter in content])
            hidden_img = self.bits_string_to_image(data_as_bits, size=shape)
            print("Decoding successful!")
            return hidden_img
        elif type == MESSAGE:
            content = message[5:index]
            print("Decoding successful!")
            return content
        else:
            raise Exception("Your container image is not valid!")
        pass

    @staticmethod
    def image_to_bits_string(image):
        try:
            # for line in container:
            #     for pixel in line:
            #         container_as_bits += ''.join(list(map(lambda x:''.join([format(int(x),'08b')]),pixel)))
            # the same purpose with line 150 but line 150 is faster
            return ''.join(
                [''.join([''.join(list(map(lambda x: ''.join([format(int(x), '08b')]), pixel))) for pixel in line]) for
                 line in image])
        except Exception:
            raise Exception("Input is Not Image")

    @staticmethod
    def bits_string_to_image(bits_string, size=None):
        """
        :param bits_tring: bit_string left to right and top to down
        :param size: width, height channel default is 3
        :return: 3d array -> image
        """
        if len(bits_string) % 24 == 0:
            pass
        else:
            raise Exception("Cannot Decoding!")
        index = 0
        temp = []
        for i in range(0, len(bits_string), 24):
            pixel = bits_string[index:index + 24]
            newpixel = []
            for j in range(0, 24, 8):
                channel = pixel[j:j + 8]  # red g or b
                newpixel.append(int(channel, base=2))
            temp.append(newpixel)
            index += 24
        a = np.array(temp, dtype=np.uint8)
        img = np.reshape(a, (size[0], size[1], 3))
        return img

    @staticmethod
    def bits_sequence_to_string(bit_sequence: str):
        """
        :param bit_sequence: Using to decode a bit sequence to strings
        :return: The message decoded
        """
        # Chunk
        chunks = list(grouper(bit_sequence, 8, '0'))
        chunks = list(map(lambda chunk: chr(int(''.join(chunk), base=2)), chunks))
        message = ''.join(chunks)
        return message

    @staticmethod
    def string_to_bits_sequence(string):
        if type(string) == str:
            chunks = list(map(char_to_8_bit_string, string))
            return ''.join(chunks)
        raise Exception('Cannot convert')

    @staticmethod
    def save(data, type, path):
        if type == MESSAGE:
            f = open('{}.txt'.format(path), "w")
            f.write(data)
        elif type == IMAGE:
            cv2.imwrite("{}.png".format(path), data)
        print("Saving successful!")
