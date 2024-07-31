import os
import sys
import msvcrt
import subprocess

text_editors = [
    # Command-line editors
    "vim",
    "nano",
    "emacs",
    "pico",
    "ed",
    "ne",
    "micro",
    "joe",
    "mcedit",
    
    # External editors
    "notepad",  # Windows
    "gedit",    # GNOME
    "kate",     # KDE
    "subl",     # Sublime Text
    "code",     # Visual Studio Code
    "atom",     # Atom
    "notepad++",
    "textmate", # macOS
    "bbedit",   # macOS
    "xed",      # Linux Mint
    "leafpad",  # Lightweight for various Linux distros
    "mousepad", # Xfce
    "pluma"     # MATE
]

def check_dirs(query, paths):
    pathli = []
    for p in paths:
        if p.lower().startswith(query.lower()):
            pathli.append(p)
    others = [x for x in paths if x not in pathli and query.lower() in x.lower()]
    pathli.extend(others)
    return pathli

def clear_current_line():
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

def display_pathlist(query, paths, currpath):
    clear_current_line()
    size = os.get_terminal_size()
    query = os.path.join(currpath, query) if query else currpath
    query_curr = query.split(os.path.sep)
    par, chi = query_curr[-2], query_curr[-1]
    parchilen = len(par) + len(chi) + 7
    if paths:
        suggestions_str = ' | '.join(paths)
        sys.stdout.write(f"{par}{os.path.sep}{chi} [{suggestions_str[:size.columns-parchilen]+'...' if len(suggestions_str) > size.columns-parchilen else suggestions_str}]")
    else:
        sys.stdout.write(f"{par}{os.path.sep}{chi}")
    sys.stdout.flush()

def getdirs(root):
    pathlist = []
    try:
        paths = os.listdir(root)
        for path in paths:
            full_path = os.path.join(root, path)
            if os.path.isdir(full_path) or os.path.isfile(full_path):
                pathlist.append(path)
    except OSError as e:
        sys.stderr.write(f"Error accessing directory: {e}\n")
    return pathlist

def update_path(currpath):
    pathlist = getdirs(currpath)
    sys.stdout.write(currpath)
    sys.stdout.flush()
    return pathlist

def run_command(command):
    try:
        subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"Error running command: {e}")

def get_input(pathlist, currpath):
    input_chars = []
    paths = []
    query = ''
    global text_editors
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()

            if char in (b'\r', b'\n'):
                os.system("cls")
                if query == '..':
                    currpath = os.path.dirname(currpath)
                    pathlist = update_path(currpath)
                    input_chars = []
                    paths = []
                elif paths:
                    currpath = os.path.join(currpath, paths[0])
                    if os.path.isfile(currpath):
                        try:
                            os.startfile(currpath)
                        except Exception as e:
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
                    com_ = ' '.join([c for c in command])
                    if com_.split(" ")[0] in text_editors:
                        run_command(com_)
                    elif (com_.startswith("dir") or
                          com_.startswith("cd") or
                          com_.startswith("mkdir") or
                          com_.startswith("del") or
                          com_.startswith("type") or
                          com_.startswith("findstr") or
                          com_.startswith("copy") or
                          com_.startswith("move") or
                          com_.startswith("ren") or
                          com_.startswith("attrib")):
                        os.system(com_)
                    else:
                        run_command(f"start cmd /k {com_}")
                    input_chars = []
                    paths = []
                    pathlist = getdirs(currpath)
                else:
                    pass

            elif char == b'\x08':  # Backspace
                if input_chars:
                    input_chars.pop()
            
            elif char == b'\t':  # Tab
                input_chars = []
                if paths:
                    input_chars = list(paths[0])

            elif char == b'\x1b':  # Escape
                break

            else:
                input_chars.append(char.decode('utf-8'))
            
            query = ''.join(input_chars)
            if query.strip() == '':
                paths = []
            else:
                paths = check_dirs(query, pathlist)
            display_pathlist(query, paths, currpath)

def main():
    os.system('cls')
    pathlist = getdirs(os.path.expanduser("~"))
    sys.stdout.write(os.path.expanduser("~"))
    sys.stdout.flush()
    get_input(pathlist, os.path.expanduser("~"))

if __name__ == '__main__':
    main()
