#!/usr/bin/env python3
import logging

from core import gui


def main():
    gui.launch_GUI()
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


main()
