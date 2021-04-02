import random
from gpx import *

INPUT_FILE=f'path_to_input_file'
OUTPUT_FILE=f'path_to_output_file'


def main():
    gpx = GPX(INPUT_FILE, lat_p=6, lon_p=6, ele_p=1, ms=False)
    set_by_speed(
        gpx,
        11,
        datetime.datetime(2021, 3, 1, 0, 0, 0),
        datetime.datetime(2021, 3, 1, 0, 0, 0)
    )
    gpx.write(OUTPUT_FILE)


if __name__ == '__main__':
    main()
