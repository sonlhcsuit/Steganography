import numpy as np
import cv2
from textwrap import wrap
starts = "@@@@@"
terminals = "$$$$$"

container = 'original_image.jpeg'
to_be_hidden_image = 'to_be_hidden_image.jpeg'
encoded_image = 'encoded_image.png'

to_be_decoded_image = 'to_be_decoded_image.png'
hidden_image = 'hidden_image.png'
lena='lena.jpg'

MESSAGE = 'MESSAGE'
IMAGE = 'IMAGE'


def is_encodable(type,container,to_be_encoded_data):
    """
    :param type:
    :param container: an image (2d matrix of pixel)
    :param to_be_encoded_data: if type is MESSAGE, it should be a text. If not, it should be an image ( 2d matrix of pixel)
    :return: bool
    """
    to_be_encoded_data_length=None
    if type == MESSAGE:
        to_be_encoded_data_length = (len(to_be_encoded_data) + 10)*8 #bits
    elif type == IMAGE:
        h,w,_ = to_be_encoded_data.shape
        to_be_encoded_data_length = (h*w*3 + 10)*8 #bits
    height,width,_ = container.shape
    container_length = height*width*3*8 +32#width and length
    return to_be_encoded_data_length*4 < container_length

def letter_2_bits_string(str_message):
    if type(str_message) == str:
        return ''.join([format(ord(char),'08b') for char in str_message])
    elif type(str_message)==int or type(str_message) == np.uint8:
        return ''.join([format(int(str_message),'08b')])
    else:
        return None

def image_2_bits_string(image):
    try:
        # for line in container:
        #     for pixel in line:
        #         container_as_bits += ''.join(list(map(to_bits_string,pixel)))
        # the same purpose with line 52 but line 52 is faster
        return ''.join([ ''.join([''.join(list(map(letter_2_bits_string, pixel))) for pixel in line]) for line in image])
    except Exception:
        raise Exception("Input is Not Image")

def bits_string_2_image(bits_string,size=None):
    """
    :param bits_tring: bit_string left to right and top to down
    :param size: width, height channel default is 3
    :return: 3d array -> image
    """
    if len(bits_string) % 24 == 0:
        pass
    else:
        raise Exception("Cannot Decoding!")
    print("Convert bits-string to an image...")
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

def hide_data_to_img(data,type=MESSAGE,image=None,image_path=None):
    """
    using 2 bits of each channel(3 channels) to hide data -> 6 bits of n-bits-message per pixel.
    1 pixel is 3-bytes(24 bits) so the max size of message lenght stored is:
    w * h * 24*0.25 - 10*8
    starts and terminals( @@@@@ and $$$$$ )symbols is required.
    Example: If we have an 512x512 image, we can hide an 196598-letters-string into it.
    (512x512x8x3x0.25 - 10*8)/8
    """
    container = None
    if image is None and image_path is None:
        raise Exception("image or image path is required")
    elif image is not None:
        if(image.shape[2]==3):
            container = image
        else:
            raise Exception("Image must be an 2d array of pixels")
    elif image_path is not None:
        container =  cv2.imread(image_path)
    print("Checking comapatible...")
    if is_encodable(type=type,container=container,to_be_encoded_data=data):
        data_as_bits = ''
        if type == MESSAGE:
            formatted_message = '{starts}{content}{terminals}'.format(starts=starts, content=data,                                                             terminals=terminals)
            data_as_bits = letter_2_bits_string(formatted_message)
        if type == IMAGE:
            imgbit = letter_2_bits_string(starts)
            for line in data:
                for pixel in line:
                    a = list(map(letter_2_bits_string, pixel))
                    imgbit = imgbit+ ''.join(a)
            imgbit = imgbit + format(data.shape[0],'016b') +format(data.shape[1],'016b')
            data_as_bits = imgbit + letter_2_bits_string(terminals)
        container_as_bits = image_2_bits_string(container)
        container_length = len(container_as_bits)
        data_length = len(data_as_bits)
        print("Comapatible!")
        print("Start hidding data...")
        index = 0
        encoded_bits=''
        for a in range(0,container_length,8):
            channel8bits = container_as_bits[a:a+8]
            data2bit = data_as_bits[index:index+2]
            index = index + 2
            encoded_data = channel8bits[0:6] + data2bit
            encoded_bits = encoded_bits + encoded_data
            if index == data_length:
                encoded_bits = encoded_bits + container_as_bits[a+8:]
                break
                #out of data
        decoded_img = bits_string_2_image(encoded_bits,(1333,1000))
        print("Hide Successful!")
        return decoded_img
    else:
        raise Exception("Cannot hide data. Using smaller image or less letters")

def get_data_from_img(type=MESSAGE,image=None,image_path=None):
    container = None
    if image is None and image_path is None:
        raise Exception("image or image path is required")
    elif image is not None:
        if (image.shape[2] == 3):
            container = image
        else:
            raise Exception("Image must be an 2d array of pixels")
    elif image_path is not None:
        container = cv2.imread(image_path)
    container_as_bits = image_2_bits_string(container)
    last2bits_data = ''
    print("Starting decode...")
    for i in range(0,len(container_as_bits),8):
        last2bits_data= last2bits_data + container_as_bits[i+6:i+8]
    message = ''
    for i in range(0,len(last2bits_data),8):
        block = last2bits_data[i:i+8]
        message+=chr(int(block,base=2))
    index = message.find('$$$$$') #find terminals
    if type == IMAGE:
        size = message[index-4:index]
        width,height = wrap(size,2)
        width = int(''.join([format(ord(char),"08b") for char in width]),base=2)
        height = int(''.join([format(ord(char),"08b") for char in height]),base=2)
        shape = (width,height,3)
        content = message[5:index-4]
        data_as_bits = ''.join([format(ord(letter),"08b") for letter in content])
        hidden_img = bits_string_2_image(data_as_bits,size=shape)
        print("Decode successful!")
        return hidden_img
    elif type==MESSAGE:
        content = message[5:index]
        print("Decode successful!")
        return content
    else:
        raise Exception("Your Input Is Not Valid!")
def STEGANO():
    is_encode = input("Wanna encode an image or decode an image encoded by us?\n0.Encode\n1.Decode\n")
    # print(is_encode)
    hidden_image_path=''
    if is_encode =="0":
        is_text = input(
            'Wanna hide text message into image or image into image - hidden image size must be smaller 25% of container image size!\n0.MESSAGE\n1.IMAGE\n')
        container_path = input("Enter container image relative path:")
        new_img = None
        if is_text == "0":
            hidden_text = input("Enter text message you wanna hide:")
            new_img = hide_data_to_img(type=MESSAGE,
                                       data=hidden_text,
                                       image_path=container_path)
        else:
            hidden_image_path = input("Enter hidden image relative path:")
            new_img = hide_data_to_img(type=IMAGE,
                                       data=cv2.imread(hidden_image_path),
                                       image_path=container_path)
        encoded_image = input(
            "Enter name of container image after hidden data. It will be at the same folder and has png extension:")

        cv2.imwrite(encoded_image + '.png', new_img)
        print("Save Successful!")
    else:
        is_text = input(
            'Which kind of data did you hide?\n0.MESSAGE\n1.IMAGE\n')
        container_path = input("Enter your image relative path:")
        hidden_data = ''

        if is_text == "0":
            hidden_data=get_data_from_img(type=MESSAGE,image_path=container_path)
            print(hidden_data)
        else:
            hidden_image = input("Enter hidden image name after decoding.It will be at the same folder and has png extension:")
            hidden_data = get_data_from_img(type=IMAGE, image_path=container_path)
            cv2.imwrite(hidden_image + '.png', hidden_data)
            print("Save Successful!")


if __name__ == '__main__':
    STEGANO()

# cvOri = cv2.imread(origin)
# print('{:10}'.format('ORIGIN'),*cvOri[0][:10])
# cvlena = cv2.imread(lena)
# print(*cvlena[0][:3])
# cvEncoded=hide_data_to_img(type=MESSAGE,data='You FUCKING LOSERRRRRRRRR!??',image=cvOri)
# cv2.imwrite(encoded,cvEncoded)
# print('{:10}'.format('DECODED'),*cvEncoded[0][:10])

# cvDecoding = cv2.imread(decoding)
# hidden_data = get_data_from_img(type=MESSAGE,image=cvDecoding)
# print([hidden_data])
# print(*hidden_data[0][:3])
# cv2.imshow("hidden",hidden_data)
# cv2.waitKey()
# cv2.destroyAllWindows()
