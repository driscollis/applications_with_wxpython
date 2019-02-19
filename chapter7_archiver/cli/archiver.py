# archiver.py

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
                        required=True, action='store',
                        dest='input_path')
    parser.add_argument('-o', '--output',
                        help='Output path', 
                        action='store', 
                        dest='output')
    return parser.parse_args()


def main():
    args = get_args()
    if args.output:
        output = pathlib.Path(args.output)
        input_path = pathlib.Path(args.input_path)
    else:
        temp = pathlib.Path(args.input_path)
        output = pathlib.Path(f'{temp}.tar')
        input_path = pathlib.Path(args.input_path)
    controller.create_tar(output, archive_objects=[input_path])
    print(f'Created tarball from {input_path} to {output}')
    
if __name__ == '__main__':
    main()