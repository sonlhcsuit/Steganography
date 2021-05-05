from argparse import ArgumentParser,ArgumentError
from core import Steganography


def main(parser,arg):
    try:
        parser.error("Cannot perfrom")
        print(arg)
    except Exception as e:
        Exception().
        parser.error(e)



def parserArgs():
    parser = ArgumentParser(description="CLI to encode an image or message into another image using 3 least significant bits. "
        + "Remember")
    parser.add_argument('action',help="Action to be perform, decode or encode")
    parser.add_argument('container',help="Container image, which carry messages")
    parser.add_argument('--message',help="Message to be encoded. If image, must use flag -i",type=str)
    parser.add_argument('--image','-i',help="Must be specified if image are selected",type=bool)
    parser.add_argument('--delimiter','-d',help="Custom delimiter, default is \'@@@@@\'")
    parser.add_argument('--output-name','-o',help="Output filepath/filename, if not specified, postfix \"encoded\" or \"decoded\" will be add")

    args = parser.parse_args()
    if args.action == "encode" and not args.message :
        parser.error("When encode action was chose, \'message\' must be provided")
    return parser,vars(args)


if __name__ == '__main__':

    parser,args = parserArgs()
    main(parser,args)