def char_to_8_bit_string(char):
    if ord(char) > 255:
        raise Exception('Only ASCII-characters supported')
    return format(ord(char),'08b')