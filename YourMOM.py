import os
import sys
import termios
import tty
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
        if p.startswith(query):
            pathli.append(p)
    others = [x for x in paths if x not in pathli and query in x]
    pathli.extend(others)
    return pathli

def clear_current_line():
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def display_pathlist(query, paths, currpath):
    clear_current_line()
    size = os.get_terminal_size()
    query = currpath + '/' + query if query else currpath
    query_curr = query.split('/')
    par, chi = query_curr[-2], query_curr[-1]
    parchilen = len(par) + len(chi) + 7
    if paths:
        suggestions_str = ' | '.join(paths)
        sys.stdout.write(f"{par}/{chi} [{suggestions_str[:size.columns-parchilen]+'...' if len(suggestions_str) > size.columns-parchilen else suggestions_str}]")
    else:
        sys.stdout.write(f"{par}/{chi}")
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

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def run_script_in_new_terminal(command):
    try:
        script = f'''
    tell application "Terminal"
        set newTab to do script
        set theWindow to first window of (every window whose tabs contains newTab)

        do script "{command}" in newTab
        repeat
            delay 0.05
            if not busy of newTab then exit repeat
        end repeat

        repeat with i from 1 to the count of theWindow's tabs
            if item i of theWindow's tabs is newTab then close theWindow
        end repeat
    end tell'''
        subprocess.run(['osascript', '-e', script], check=True)
    except Exception as e:
        print(f"Error running command in new terminal: {e}")

def get_input(pathlist, currpath):
    fd = sys.stdin.fileno()
    original_settings = termios.tcgetattr(fd)
    input_chars = []
    paths = []
    query = ''
    global text_editors
    try:
        hide_cursor()
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)

            if char == '\n' or char == '\r':
                os.system("clear")
                if query == '..':
                    currpath = os.path.dirname(currpath)
                    pathlist = update_path(currpath)
                    input_chars = []
                    paths = []
                if paths:
                    currpath = os.path.join(currpath, paths[0])
                    if os.path.isfile(currpath):
                        try:
                            out = subprocess.check_output(
                                f"open {currpath}",
                                text=True,
                                shell=True
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
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
                        try:
                            out = subprocess.check_output(
                                f"{com_.split(' ')[0]} {currpath}",
                                text=True,
                                shell=True,
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Error opening file: {e}")
                    elif (com_.startswith("ls") or
                        com_.startswith("cd") or
                        com_.startswith("mkdir") or
                        com_.startswith("rm") or
                        com_.startswith("cat") or
                        com_.startswith("grep") or
                        com_.startswith("head") or
                        com_.startswith("tail") or
                        com_.startswith("sort") or
                        com_.startswith("uniq") or
                        com_.startswith("find") or
                        com_.startswith("chmod") or
                        com_.startswith("chown") or
                        com_.startswith("touch") or
                        com_.startswith("awk") or
                        com_.startswith("sed")):
                        try:
                            out = subprocess.check_output(
                                f"{com_}",
                                text=True,
                                shell=True,
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Error running command: {e}")
                    elif (com_.startswith("cp") or
                            com_.startswith("mv")):
                        com_2 = com_.split(" ")
                        source = com_2[-1]
                        dest = com_2[-2]
                        com_0_li = com_2[:-2]
                        com_0 = ' '.join(com_0_li)
                        try:
                            out = subprocess.check_output(
                                f"{com_0} {source} {dest}",
                                text=True,
                                shell=True,
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Error running command: {e}")
                    elif (com_.startswith("pwd") or
                          com_.startswith("clear") or
                            com_.startswith("wc") or
                            com_.startswith("df") or
                            com_.startswith("du")):
                        com_0 = com_.split(" ")[0]
                        try:
                            out = subprocess.check_output(
                                f"{com_0}",
                                text=True,
                                shell=True,
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Error running command: {e}")
                    elif com_.startswith("-- "):
                        com_x = com_.split(" ")
                        com_0 = com_x[1:-1]
                        com_0x = ' '.join(com_0)
                        try:
                            out = subprocess.check_output(
                                f"{com_0x}",
                                text=True,
                                shell=True,
                            )
                            sys.stdout.write(''.join([a if a != '\n' else '\n\r' for a in out])+'\n')
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Error running command: {e}")
                    else:
                        try:
                            run_script_in_new_terminal(com_)
                        except Exception as e:
                            print(f"Error running command: {e}")
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
                if paths:
                    input_chars = list(paths[0])

            elif char == '\x1b':
                break

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
    pathlist = getdirs(os.path.expanduser("~"))
    sys.stdout.write(os.path.expanduser("~"))
    sys.stdout.flush()
    get_input(pathlist, (os.path.expanduser("~")))

if __name__ == '__main__':
    main()
