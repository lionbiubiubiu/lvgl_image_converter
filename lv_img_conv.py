# Copyright (c) 2021 W-Mai
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
#
# lvgl_image_converter/lv_img_conv.py
# Created by W-Mai on 2021/2/21.
# repo: https://github.com/W-Mai/lvgl_image_converter
#
##############################################################


import argparse
import time
from pathlib import Path

from lv_img_converter import Converter

name2const = {
    'RGB332': Converter.FLAG.CF_TRUE_COLOR_332,
    'RGB565': Converter.FLAG.CF_TRUE_COLOR_565,
    'RGB565SWAP': Converter.FLAG.CF_TRUE_COLOR_565_SWAP,
    'RGB888': Converter.FLAG.CF_TRUE_COLOR_888,
    'alpha_1': Converter.FLAG.CF_ALPHA_1_BIT,
    'alpha_2': Converter.FLAG.CF_ALPHA_2_BIT,
    'alpha_4': Converter.FLAG.CF_ALPHA_4_BIT,
    'alpha_8': Converter.FLAG.CF_ALPHA_8_BIT,
    'indexed_1': Converter.FLAG.CF_INDEXED_1_BIT,
    'indexed_2': Converter.FLAG.CF_INDEXED_2_BIT,
    'indexed_4': Converter.FLAG.CF_INDEXED_4_BIT,
    'indexed_8': Converter.FLAG.CF_INDEXED_8_BIT,
    'raw': Converter.FLAG.CF_RAW,
    'raw_alpha': Converter.FLAG.CF_RAW_ALPHA,
    'raw_chroma': Converter.FLAG.CF_RAW_CHROMA,
    'true_color': Converter.FLAG.CF_TRUE_COLOR,
    'true_color_alpha': Converter.FLAG.CF_TRUE_COLOR_ALPHA,
    'true_color_chroma': Converter.FLAG.CF_TRUE_COLOR_CHROMA,
}


def check_allowed(filepath: Path):
    suffix: str = filepath.suffix
    return suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tga', '.gif', '.bin']


def conv_one_file(filepath: Path, f, cf, ff: str, dither, out_path=Path()):
    root_path = filepath.parent
    name = filepath.stem
    conv = Converter(filepath.as_posix(), dither, name2const[f])

    c_arr = ''
    if f in ['true_color', 'true_color_alpha', 'true_color_chroma']:
        conv.convert(name2const[cf])
        c_arr = conv.format_to_c_array()
    else:
        conv.convert(name2const[f])

    file_conf = {
        'C': {
            'suffix': 'c',
            'mode': 'w'},
        'BIN': {
            'suffix': '.bin',
            'mode': 'wb'}
    }

    out_path = root_path if out_path == Path() else out_path
    out_path = out_path.joinpath(name).with_suffix(file_conf[ff]['suffix'])

    with open(out_path, file_conf[ff]['mode']) as fi:
        res = conv.get_c_code_file(name2const[f], c_arr) if ff == 'C' else conv.get_bin_file(name2const[f])
        fi.write(res)
    return "SUCCESS"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', type=str, nargs="+",
                        help='images dir paths (or file paths) you wanna convert')
    parser.add_argument('-f', '-format', type=str, default='true_color',
                        choices=['true_color', 'true_color_alpha', 'true_color_chroma',
                                 'indexed_1', 'indexed_2', 'indexed_4', 'indexed_8',
                                 'alpha_1', 'alpha_2', 'alpha_4', 'alpha_8',
                                 'raw', 'raw_alpha', 'raw_chroma'],
                        help='converted file format: \n'
                             'true_color, true_color_alpha, true_color_chroma, '
                             'indexed_1, indexed_2, indexed_4, indexed_8, '
                             'alpha_1, alpha_2, alpha_4, alpha_8, '
                             'raw, raw_alpha, raw_chroma. The default is: true_color')
    parser.add_argument('-cf', '-color-format', type=str, default='RGB888',
                        choices=['RGB332', 'RGB565', 'RGB565SWAP', 'RGB888'],
                        help='converted color format: RGB332, RGB565, RGB565SWAP, RGB888')
    parser.add_argument('-ff', '-file-format', type=str, default='C',
                        choices=['C', 'BIN'],
                        help='converted file format: C(*.c), BIN(*.bin)')
    parser.add_argument('-o', '-output-filepath', type=str, default='',
                        help='output file path. if not set, it will saved in the input dir')
    parser.add_argument('-r', action="store_const", const=True,
                        help='convert files recursively')
    parser.add_argument('-d', action="store_const", const=True,
                        help='need to dith')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    file_count = 0
    failed_pic_paths = []
    for path in args.filepath:
        path = Path(path)
        if Path(path).is_dir():
            path_glob = path.rglob if args.r else path.glob
            for file in path_glob("*.*"):
                file: Path
                if not check_allowed(file):
                    continue
                print(f'{file_count:<5} {file} START', end='')
                t0 = time.time()

                try:
                    conv_rtn = conv_one_file(file, args.f, args.cf, args.ff, args.d, Path(args.o))
                    if conv_rtn == "SUCCESS":
                        file_count += 1
                        print('\b' * 5 + 'FINISHED', end='')
                    elif conv_rtn == "NOT ALLOWED":
                        print('\b' * 5, end='')
                except Exception as e:
                    print('\b' * 5, e, end='')
                    failed_pic_paths.append(file)
                print(f' {(time.time() - t0) * 1000} ms')
    print()
    print(f"Convert Complete. Total convert {file_count} file(s).")
    print()
    if failed_pic_paths:
        print("Failed File List:")
        print(*failed_pic_paths, sep='\n')
