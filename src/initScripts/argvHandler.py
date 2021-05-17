import argparse
import pathlib


class ArgvHandler:
    """Class to handle input arguments if existant. Provides support for the word integration which calls this program
    using arguments"""
    def __init__(self):
        # 1. Use argparse to read all arguments. All set to optional to allow launching the script without them
        parser = argparse.ArgumentParser(
            description="Script to extract acronyms from Word documents. Don't arguments to access the user interface")
        parser.add_argument("-i", "--input", type=str, default="", help="Path to word document", required=False)
        parser.add_argument("-m", "--mode", type=str, default="", help="Processing mode", required=False)
        parser.add_argument("-fn", "--filename", type=str, default=None, help="Original filename of document", required=False)
        args = parser.parse_args()

        # 2. Perform checks
        aux_path = pathlib.Path(args.input)
        if not aux_path.exists():
            exit(-1) #Fixme: Raise an exception and only exit on the main script

        # 3. Expose arguments
        self.input_path = args.input
        self.mode = args.mode
        self.filename = args.filename
