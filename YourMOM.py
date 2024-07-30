import os
import sys
import termios
import tty
import subprocess

def check_dirs(query, paths):
    pathli = []
    for p in paths:
        if p.startswith(query):
            pathli.append(p)
    return pathli

def clear_current_line():
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def display_pathlist(query, paths, currpath):
    clear_current_line()
    query = currpath + '/' + query if query else currpath
    if paths:
        suggestions_str = ' | '.join(paths)
        sys.stdout.write(f"{query} [{suggestions_str}]")
    else:
        sys.stdout.write(f"{query}")
    sys.stdout.flush()

def getdirs(root):
    pathlist = []
    try:
        paths = os.listdir(root)
        for path in paths:
            full_path = os.path.join(root, path)
            if os.path.isdir(full_path):
                pathlist.append(path)
            if os.path.isfile(full_path):
                pathlist.append(path)
    except OSError as e:
        sys.stderr.write(f"Error accessing directory: {e}\n")
    return pathlist

def update_path(currpath):
    pathlist = getdirs(currpath)
    sys.stdout.write(currpath)
    sys.stdout.flush()
    return pathlist

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def get_input(pathlist, currpath):
    fd = sys.stdin.fileno()
    original_settings = termios.tcgetattr(fd)
    input_chars = []
    paths = []
    query = ''
    try:
        hide_cursor()
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)

            if char == '\n' or char == '\r':
                clear_current_line()
                if query == '..':
                    clear_current_line()
                    currpath = os.path.dirname(currpath)
                    pathlist = update_path(currpath)
                    input_chars = []
                    paths = []
                if paths:
                    currpath = os.path.join(currpath, paths[0])
                    if os.path.isfile(currpath):
                        try:
                            subprocess.run(['open', currpath], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error opening file: {e}")
                        clear_current_line()
                        currpath = os.path.dirname(currpath)
                        pathlist = update_path(currpath)
                        input_chars = []
                        paths = []
                    else:
                        pathlist = update_path(currpath)
                    input_chars = []
                elif '::' in query:
                    cmd = query.split('::')
                    cmdlist = cmd[1].split()
                    command = []
                    command.extend(cmdlist)
                    command.append(os.path.join(currpath, cmd[0].strip()))
                    try:
                        subprocess.run(command, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error opening file: {e}")
                    input_chars = []
                    paths = []
                    pathlist = getdirs(currpath)
                else:
                    pass

            elif char == '\x7f' or char == '\b':
                if input_chars:
                    input_chars.pop()
            
            elif char == '\t':
                input_chars = []
                input_chars = list(paths[0])

            elif char == '\x1b':
                break

            elif query == '..':
                clear_current_line()
                currpath = os.path.dirname(currpath)
                pathlist = update_path(currpath)
                input_chars = []

            else:
                input_chars.append(char)
            
            query = ''.join(input_chars)
            if query.strip() == '':
                paths = []
            else:
                paths = check_dirs(query, pathlist)
            display_pathlist(query, paths, currpath)

    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_settings)

def main():
    os.system('clear')
    pathlist = getdirs(os.getcwd())
    sys.stdout.write(os.getcwd())
    sys.stdout.flush()
    get_input(pathlist, os.getcwd())

if __name__ == '__main__':
    main()