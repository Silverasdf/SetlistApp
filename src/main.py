# Main.py - The driver file for the setlist generator.
# usage: usage: main.py [-d] [-h]
# options:
#   -d, --debug  print debug statements
#   -h, --help   print help
# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active, Not in that order (I don't think)
# Ryan Peruski, 07/29/2023

from gui import *
import sys
import argparse

if __name__ == "__main__":
    #Start arg parsing
    parser = argparse.ArgumentParser(conflict_handler='resolve', description="Setlist Generator")
    # Add debug flag
    parser.add_argument("-d", "--debug", help="print debug statements", action="store_true")
    # Add help flag
    parser.add_argument("-h", "--help", help="print help", action="store_true")
    try: # If unknown argument, print help and exit
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    # End arg parsing
    app = QApplication(sys.argv)
    # If help flag is set, print help and exit
    if args.help:
        parser.print_help()
        sys.exit(0)


    window = SetlistGeneratorWindow(debug=args.debug)
    sys.exit(app.exec_())