from argparse import ArgumentParser,ArgumentError



def main(arg):
    print(arg)
    pass


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
        parser.error("When encode action was chose, message must be provided")
    if args
        # raise ArgumentError("When encode action was chose, message must be provided")
    return vars(args)


if __name__ == '__main__':

    args = parserArgs()
    main(args)