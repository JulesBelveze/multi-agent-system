import os
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser
from pathlib import Path

command = "java -jar server.jar -c \"py client/client.py\" -l \"{}\" -t {}"
gui_command = "java -jar server.jar -c \"py client/client.py\" -l \"{}\" -g -t {}"

def scan_dir_for_levels(dir_name, recursive_dir):
    levels = []
    keyword = '**/*.lvl' if recursive_dir else '*.lvl'

    for f in Path(dir_name).glob(keyword):
        levels.append(str(f))
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

def test_levels(levels, is_dir, gui, timeout):
    completed_lvl_count = 0
    for lvl in levels:
        lvl_path = lvl if is_dir else find_level(lvl)
        if lvl_path is not None:
            print("Testing: {}".format(lvl_path))

            cmd = gui_command if gui else command
            p = Popen(cmd.format(lvl_path, timeout), stdout=PIPE, stderr=STDOUT)

            log_file = format_log_name(lvl_path)
            f = open("./logs/{}".format(log_file), 'w', encoding='utf-8')
            print("Created log file: {}".format(log_file))
            for line in p.stdout:
                str_line = line.decode('utf-8').rstrip("\n")

                if "Level solved" in str_line:
                    print("Solved: {}".format("Yes" in str_line))
                    if "Yes" in str_line:
                        completed_lvl_count += 1
                elif "failed to parse" in str_line:
                    print("[OOPS] Server failed to load file")
                elif "timed out" in str_line:
                    print("[OOPS] Client timed out after {} seconds".format(timeout))
                elif "Last action time:" in str_line:
                    print("Time:{}".format(str_line.split(":")[1][:-1]))

                f.write(str_line)
            print("Finished writing to: {}\n".format(log_file))
            f.close()
            p.kill()
        else:
            print("NOT FOUND: {}\n".format(lvl))
    print("Levels completed: {}/{}".format(completed_lvl_count, len(levels)))

def main(args):
    if args.lvls is not None:
        levels = args.lvls.split(',')
        test_levels(levels, False, args.g, args.t)
    elif args.dir is not None:
        levels = scan_dir_for_levels(args.dir, args.recur)
        if len(levels) > 0:
            test_levels(levels, True, args.g, args.t)
        else:
            print("No levels found in directory")
    else:
        print("Did not supply level or directory arguments. Use '-h' for help")

#TODO: Program will not continue if a gui is opened, until it is closed.
if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Mass testing utility for Starfish')
    parser.add_argument('-lvls', default=None, help='Provide name of levels separated by comma. Individual levels also supported')
    parser.add_argument('-dir', default=None, help='Test all levels inside given directory. Directory must be inside levels folder. E.g.: levels, levels/test')
    parser.add_argument('-recur', default=False, help='Set to true to also test files in sub-directories of given directory')
    parser.add_argument('-g', default=False, help='Set to true to also run the server graphics. Opens 1 at a time and must be closed manually')
    parser.add_argument('-t', default=60, type=int, help='Set the timeout for the client in seconds. Default: 60')
    args = parser.parse_args()

    # Run client
    main(args)