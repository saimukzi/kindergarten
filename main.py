import os
import sys

PROJECT_PATH = os.path.dirname(__file__)
SRC_PATH = os.path.join(PROJECT_PATH,'src')
sys.path.append(SRC_PATH)

import argparse
import kindergarten.playground.runtime as runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    args = parser.parse_args()

    runtime.run(args)


if __name__=="__main__":
    main()
