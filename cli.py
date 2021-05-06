from argparse import ArgumentParser, ArgumentError
import os
from core import Steganography, IMAGE, MESSAGE


def main(parser, arg):
    try:
        print(arg)
        current_path = os.getcwd();
        cont_image_path = os.path.join(current_path, arg['container'])
        steg = Steganography(cont_image_path)
        if arg['action'] == 'encode':
            if not steg.is_encodable(arg['message'], IMAGE if arg['image'] else MESSAGE):
                parser.error(f"Cannot encode, data to be encoded must lower than one quarter of container size")
            encoded = steg.encode(arg.get('message'), IMAGE if arg['image'] else MESSAGE)
            Steganography.save(encoded, IMAGE, os.path.join(os.getcwd(), 'ecd'))
        elif arg['action'] == 'decode':
            decoded = steg.decode(type=IMAGE if arg['image'] else MESSAGE)
            Steganography.save(decoded, IMAGE, os.path.join(os.getcwd(), 'dcd'))

        # print(encoded)
    except Exception as e:
        parser.error(e)


def parserArgs():
    parser = ArgumentParser(
        description="CLI to encode an image or message into another image using 2 least significant bits.")
    parser.add_argument('action', help="Action to be perform, decode or encode")
    parser.add_argument('container', help="Container image, which carry messages")
    parser.add_argument('--message', '-m', help="Message to be encoded. If image, must use flag -i", type=str)
    parser.add_argument('--image', '-i', help="Must be specified if image are selected", action='store_true',
                        default=False)
    parser.add_argument('--delimiter', '-d', help="Custom delimiter, default is \'@@@@@\'")
    parser.add_argument('--output-name', '-o',
                        help="Output filepath/filename, if not specified, postfix \"encoded\" or \"decoded\" will be add")

    args = parser.parse_args()
    if args.action == "encode" and not args.message:
        parser.error("When encode action was chose, \'message\' must be provided")
    return parser, vars(args)


if __name__ == '__main__':
    parser, args = parserArgs()
    main(parser, args)
