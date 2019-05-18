import os
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser
from pathlib import Path

command = "java -jar server.jar -c \"py client/client.py\" -l \"{}\""
gui_command = "java -jar server.jar -c \"py client/client.py\" -l \"{}\" -g"

def scan_dir_for_levels(dir_name, recursive_dir):
    levels = []
    keyword = '**/*.lvl' if recursive_dir else '*.lvl'
    for f_name in Path(dir_name).glob(keyword):
        levels.append(str(f_name.name))
    return levels

def find_level(level_name):
    for f_name in Path('levels').glob('**/*.lvl'):
        if level_name in f_name.name:
            return str(f_name)
    return None

def format_log_name(level_path):
    slash = "/" if "/" in level_path else "\\"
    name = level_path.replace("levels", "", 1).replace(slash, "-").replace(".lvl","")
    return "[{}]log.txt".format(name[1:])

def test_levels(levels, gui, gui_limiter):
    limiter_count = 0
    for lvl in levels:
        lvl_path = find_level(lvl)
        if lvl_path is not None:
            print("Testing: {}".format(lvl_path))

            cmd = command
            if gui and limiter_count < gui_limiter:
                cmd = gui_command
                limiter_count += 1
            p = Popen(cmd.format(lvl_path), stdout=PIPE, stderr=STDOUT)

            log_file = format_log_name(lvl_path)
            print("Creating log file: {}".format(log_file))

            f = open("./logs/{}".format(log_file), 'w', encoding='utf-8')
            for line in p.stdout:
                str_line = line.decode('utf-8').rstrip("\n")
                if "[server][info] Level solved" in str_line:
                    print("{} solved: {}".format(lvl, "Yes" in str_line))
                f.write(str_line)
            f.close()

        else:
            print("NOT FOUND: {}".format(lvl))

def main(args):
    if args.lvls is not None:
        levels = args.lvls.split(',')
        test_levels(levels, args.g, args.madgui)
    elif args.dir is not None:
        levels = scan_dir_for_levels(args.dir, args.recur)
        if len(levels) > 0:
            test_levels(levels, args.g, args.madgui)
    else:
        print("Did not supply level or directory arguments. Use '-h' for help")


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Mass testing utility for Starfish')
    parser.add_argument('-lvls', default=None, help='Provide name of levels separated by comma. Individual levels also supported')
    parser.add_argument('-dir', default=None, help='Test all levels inside given directory. Directory must be inside levels folder')
    parser.add_argument('-recur', default=False, help='Set to true to also test files in sub-directories of given directory')
    parser.add_argument('-g', default=False, help='Set to true to also run the server graphics. Limited to 1 level by default.')
    parser.add_argument('-madgui', default=1, type=int, help='Set the gui limit to whatever and make your machine suffer! Use at your own risk')

    args = parser.parse_args()

    # Run client
    main(args)