def char_to_8_bit_string(char):
    if ord(char) > 255:
        raise Exception('Only ASCII-characters supported')
    return format(ord(char), '08b')


def int_to_8_bit_string(number: int):
    if number > 255:
        raise Exception('Only ASCII-characters supported')
    return format(int(number), '08b')


def int_to_16_bit_string(number: int):
    if number > 65535:
        raise Exception('Only Standard-Unicode-characters supported')
    return format(int(number), '016b')


def change_lsb(number: int, bits: int, amount=2):
    """
    :param number: the number which is going to be replaced `amount` lsb
    :param bits: the bits kick in lsb position
    :param amount: number of lsb
    :return:
    """
    if bits > 2 ** amount - 1:
        raise Exception(f'Cannot represent bits_as_int because to few bits ({amount})')
    u = number >> amount
    u = u << amount
    u = u + bits
    return u


def get_lsb(number, amount=2):
    """
    :param number: the number which is going to be extracted
    :param amount: number of lsb
    :return:
    """
    nu = int('1' * amount,base=2)
    return number & nu
