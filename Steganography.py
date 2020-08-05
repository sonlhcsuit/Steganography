# import cv2
import numpy as np
import types
import matplotlib.pyplot as plt

# Hide Data
def mess2Bin(message):
    if type(message) == str:
        return ''.join([format(ord(i), "08b") for i in message])
    elif type(message) == bytes or type(message) == np.ndarray:
        return [format(i,"08b") for i in message]
    elif type(message) == int or type(message) == np.uint8:
        return format(message,"08b")
    else:
        raise TypeError("Input không hợp lệ")

def hideData(image, message):
    """Tính số lượng byte cần encode"""
    n_bytes = image.shape[0] * image.shape[1]*3//8
    print ("Số lượng byte cần encode:",n_bytes)

    """Không thể nén message vào ảnh vì không đủ kích thước"""
    if len(message) > n_bytes:
        raise ValueError("Thông tin text quá lớn không thể lưu vào ảnh, cần ảnh lớn hơn hoặc giảm bớt thông tin lại!!!")

    message += "#####" # Có thể dùng tùy ý kí tự tách chuỗi
    data_index = 0

#     Convert mess 2 bin:
    bin_mess = mess2Bin(message)

    # Tìm độ dài chuỗi bit để encode
    data_len = len(bin_mess)
    for values in image:
        for pixel in values:
            """Convert RGB 2 Bin"""
            r,g,b = mess2Bin(pixel)
            """Bắt đầu chuyển dần bit phải nhất nếu vẫn ảnh vần còn lưu được"""
            if data_index < data_len:
                """Giấu ảnh vào red pixel với hệ nhị phân (2)"""
                pixel[0] = int(r[:-1] + bin_mess[data_index], 2)
                data_index += 1
            if data_index < data_len:
                """Giấu ảnh vào green pixel với hệ nhị phân (2)"""
                pixel[1] = int(g[:-1] + bin_mess[data_index], 2)
                data_index += 1
            if data_index < data_len:
                """Giấu ảnh vào blue pixel với hệ nhị phân (2)"""
                pixel[2] = int(b[:-1] + bin_mess[data_index], 2)
                data_index += 1
            # Khi hết data để encode
            if data_index >= data_len:
                break
    return image


def hideImage(img, img_hide):
    """Thay đổi size của ảnh giấu về cùng chiều với ảnh chứa """
    d = img.shape[0]
    h = img.shape[1]
    img_hide = cv2.resize(img_hide, (h,d))

    for i in range(d-1):
        for j in range(h-1):
            """Convert 2 ảnh RGB 2 Bin"""
            r1,g1,b1 = mess2Bin(img[i][j])
            r2,g2,b2 = mess2Bin(img_hide[i][j])
            """Giấu 4 bit phải nhất của ảnh giấu sang 4 bit trái nhất ảnh chứa"""
            img[i][j][0] = int(r1[:4] +r2[:4],2)
            img[i][j][1] = int(g1[:4] +g2[:4],2)
            img[i][j][2] = int(b1[:4] +b2[:4],2)
    return img


##################################################################
# Show Data
def showData(image):
    bin_data = ""
    for values in image:
        for pixel in values:
            r,g,b = mess2Bin(pixel)
            bin_data += r[-1]
            bin_data += g[-1]
            bin_data += b[-1]

    """Tách mỗi 8 bit"""
    all_bytes = [bin_data[i:i+8] for i in range(0, len(bin_data), 8)]
    """Convert 8bit to characters"""
    decode_data = ""
    for byte in all_bytes:
        decode_data += chr(int(byte,2))
        if decode_data[-5:] == "#####": # Check nếu đến đoạn cắt
            break
    return decode_data[:-5]

def showImage(img):
    """Create new RGB image to storage output"""
#     new_img = cv2.CreateImage((img.shape[0],img.shape[1]),8,3)
    new_img = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            """Convert 2 ảnh RGB 2 Bin"""
            r1,g1,b1 = mess2Bin(img[i][j])
            new_img[i][j][0] = int(r1[4:] + "0000",2)
            new_img[i][j][1] = int(g1[4:] + "0000",2)
            new_img[i][j][2] = int(b1[4:] + "0000",2)
    return new_img

########################################################
# encode
def encode_text():
    img_name = input("Nhập tên file ảnh name(bao gồm đuôi): ")
    img = cv2.imread(img_name)

    # Info image
    print('Shape image: ',img.shape)
    print('Ảnh gốc: ')
    resized_img = cv2.resize(img, (500,500))

    cv2.imshow('Ảnh gốc',resized_img)
    cv2.waitKey()

    data = input('Nhập message cần giấu trong ảnh này:')
    if (len(data) == 0):
        raise ValueError("Message trống")

    file_name = input('Đặt tên file encode ảnh (bao gồm đuôi .png):')
    encode_img = hideData(img, data)
    cv2.imwrite(file_name,encode_img)

def encode_img():
    img_name = input("Nhập tên file ảnh name(bao gồm đuôi): ")
    img = cv2.imread(img_name)

    # Info image
    print('Shape image: ',img.shape)
    print('Ảnh gốc: ')
    resized_img = cv2.resize(img, (500,500))
    cv2.imshow('Ảnh gốc',resized_img)
    cv2.waitKey()

    img_name_hide = input("Nhập tên file ảnh name(bao gồm đuôi) cần giấu: ")
    img_hide = cv2.imread(img_name_hide)

    file_name = input('Đặt tên file encode ảnh (bao gồm đuôi):')
    encode_img = hideImage(img,img_hide)
    cv2.imwrite(file_name, encode_img)


##############################################################
# Decode
def decode_text():
    img_name = input('Nhập tên file đã giấu thông tin trong ảnh(đuôi .png):')
    img = cv2.imread(img_name)

    print('Ảnh đã giấu nó như thế này:')
    resized_img = cv2.resize(img,(500,500))
    cv2.imshow('Ảnh đã giấu thông tin',resized_img)
    cv2.waitKey()

    text = showData(img)
    return text

def decode_img():
    img_name = input('Nhập tên file đã giấu thông tin trong ảnh(đuôi png):')
    img = cv2.imread(img_name)
    print('Ảnh đã giấu nó như thế này:')
    resized_img = cv2.resize(img,(500,500))
    resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
    plt.imshow(resized_img)
    image_hide = showImage(img)
    return image_hide

def Steganography():
    a = input('Image Steganography with Least Significant Bit \n 1. Encode message \n 2. Decode message\n 3. Encode Image\n 4. Decode Image\n')

    userinput = int(a)
    if (userinput==1):
        print("\nEncoding mess...")
        encode_text()
    elif (userinput==2):
        print("\nDecoding mess...")
        print("Decoded message: "+ decode_text())
    elif (userinput==3):
        print("\nEncoding image...")
        encode_img()
    elif (userinput==4):
        print("\nDecoding image...")
        output = decode_img()
        resized_img = cv2.resize(output,(500,500))
        cv2.imshow('Ảnh Decode',resized_img)
        cv2.waitKey()
    else:
        raise Exception("Nhập sai input rồi")
a = mess2Bin("this is fucking test")
print(a)
# Steganography()
