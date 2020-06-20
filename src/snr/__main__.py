#!/usr/bin/env python3

# :::::::::::::::[]::::::::::::: #
# :::: /_> |U_U| || /_> /_> :::: #
# :::: <=/ |T-T| || <=/ <=/ :::: #
# ::::::::SHISS DOTFILES:::::::: #
# https://github.com/gzygmanski: #
# gzygmanski@hotmail.com:::::::: #

import os
import argparse
import snr.reader.state_reader as State
from snr.snr import snr

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-r', '--dark_mode', help='enable dark mode', action='store_true')
    arg_parser.add_argument('-s', '--speed_mode', help='enable speed reading mode', \
        action='store_true')
    arg_parser.add_argument('-v', '--highlight', help='enable speech highlight', \
        action='store_true')
    arg_parser.add_argument('-d', '--double_page', help='enable double page mode', action='store_true')
    arg_parser.add_argument('-f', '--justify_full', help='enable justify full mode', action='store_true')
    arg_parser.add_argument('-e', '--hyphenation', help='enable hyphenation, requires dictionary', action='store_true')
    arg_parser.add_argument('--lang', help='specify dictionary language e.g. en_US, pl_PL', type=str)
    arg_parser.add_argument('--dict_download', help='allow to download dictionary', action='store_true')
    arg_parser.add_argument('--verbose', help='show output', action='store_true')
    arg_parser.add_argument('FILE', help='path/to/epub/file', nargs='?', default=None)

    args = arg_parser.parse_args()

    state = State.StateReader(args.verbose)
    default = False

    if args.FILE is not None:
        fileinput = os.path.abspath(args.FILE)
    else:
        try:
            fileinput = state.get_path()
            default = True
        except KeyError:
            print(Msg.HEADER)
            print(Msg.ERR_NO_PATH)
            exit()

    snr(state, fileinput, args, default)

if __name__ == '__main__':
    main()
