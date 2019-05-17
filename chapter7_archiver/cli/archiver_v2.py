# archiver_v2.py

import argparse
import pathlib
import textwrap

import controller


def get_args():
    parser = argparse.ArgumentParser(
        description='Create a tar file',
        epilog=textwrap.dedent(
        '''
        Example Usage:
            archiver.py -t input_path
            archiver.py --tar input_path -o output_path
        ''')
    )
    parser.add_argument('-t', '--tar',
                        help='Create a tar file from the input path',
                        required=True, action='store', nargs='+',
                        dest='input_path')
    parser.add_argument('-o', '--output',
                        help='Output path',
                        action='store',
                        required=True,
                        dest='output')
    return parser.parse_args()


def get_paths(paths):
    path_objs = []
    for path in paths:
        path_objs.append(pathlib.Path(path))
    return path_objs


def main():
    args = get_args()
    if args.output:
        output = pathlib.Path(args.output)
        input_paths = get_paths(args.input_path)
        controller.create_tar(output, archive_objects=input_paths)
        print(f'Created tarball from {args.input_path} to {output}')

if __name__ == '__main__':
    main()