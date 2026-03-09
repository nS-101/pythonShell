import sys #mainly for redirecting input/output to specific locations
import os #for directory and file manipulation, mainly used for cd command and tab completion functionality
import shlex #shell lexicon library for word and char manipulation
import shutil #to find executable files and store their file paths
import subprocess #to execute executable files
import glob #to see all files in a directory, mainly used for tab completion functionality 
import readline #mainly for tab completion functionality 
import time #mainly used here for double tab functionality, to see how much time has passed between the first and second tab

def commandType(userCommand): #commands for when user types "type [statement]"
    validTypeArr = ["echo","exit","pwd","cd","type"]
    userCommandArr = shlex.split(userCommand.strip()) #shlex.split is better for terminal commands than just .split()
    if len(userCommandArr) < 2:
        return(f"{userCommandArr[1:]}: not found")
    else:
        if userCommandArr[1] in validTypeArr:
            return(f"{userCommandArr[1]} is a shell builtin")
        elif shutil.which(userCommandArr[1]):
            filePath = shutil.which(userCommandArr[1])
            return(f"{userCommandArr[1]} is {filePath}")
        else:
            return(f"{"".join(userCommandArr[1:])}: not found")

def directorySwitch(commandArray): # we use the list as a parameter to prevent having to split again
    path = "~"
    if len(commandArray) > 1:
        path = commandArray[1] 

    try:
        os.chdir(os.path.expanduser(path))
        return True
    except (FileNotFoundError, PermissionError):
        return False


def execute_pipeline(full_command):
    segments = [s.strip() for s in full_command.split("|")]
    prev_stdout = None
    processes = []

    for i, segment in enumerate(segments):
        args = shlex.split(segment)
        is_last = (i == len(segments) - 1)

        # 1. Handle Redirection(only if it's the last segment)
        if is_last and ">" in segment:
            cmd_part, file_part = segment.split(">", 1)
            args = shlex.split(cmd_part.strip())
            filename = file_part.strip()
            try:
                with open(filename, "w") as f:
                    subprocess.run(args, stdin=prev_stdout, stdout=f)
                return # We are done!
            except Exception:
                return

        # 2. Handle Builtins(inside the loop)
        if args[0] in _BUILTINS:
            builtin_output = ""
            if args[0] == "pwd":
                builtin_output = os.getcwd() + "\n"
            elif args[0] == "echo":
                builtin_output = " ".join(args[1:]) + "\n"
            
            if is_last:
                sys.stdout.write(builtin_output)
                sys.stdout.flush()
            else:
                # Create the "bridge" for the next command
                proc = subprocess.Popen(["echo", "-n", builtin_output], 
                                        stdout=subprocess.PIPE, text=True)
                prev_stdout = proc.stdout
                processes.append(proc)
        
        # 3. Handle External Commands(inside the loop)
        else:
            proc = subprocess.Popen(
                args,
                stdin=prev_stdout,
                stdout=subprocess.PIPE if not is_last else None,
                text=True
            )
            prev_stdout = proc.stdout
            processes.append(proc)

    # 4. Wait for everyone to finish(outside the loop)
    for p in processes:
        p.wait()

# builtins and a cached list of executables for completion
_BUILTINS = ["echo", "exit", "pwd", "cd", "type"]

def _list_executables(): #returns sorted listed of executable names found on PATH, used for tab completion functionality
    
    cmds = set()
    for p in os.environ.get("PATH", "").split(os.pathsep):
        if not p:
            continue
        try:
            for name in os.listdir(p):
                full = os.path.join(p, name)
                if os.path.isfile(full) and os.access(full, os.X_OK):
                    cmds.add(name)
        except Exception:
            # ignore unreadable PATH entries
            continue
    return sorted(cmds)

_EXECUTABLES = _list_executables()


def _longest_common_prefix(strs): #returns longest common prefix for a list of strings, used for tab completion functionality
    
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        # shorten prefix until s startswith prefix
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix

# module-level cache variables (define near the top where your completer lives)
_last_matches = []
_last_prefix = None

# tab state for double-Tab listing behavior
_TAB_TIMEOUT = 1.0  # seconds to wait between first and second Tab
_tab_prefix = None
_tab_count = 0
_tab_time = 0.0

def _completer(text, state):
    global _last_matches, _last_prefix, _tab_prefix, _tab_count, _tab_time

    buf = readline.get_line_buffer()
    try:
        begidx = readline.get_begidx()
        endidx = readline.get_endidx()
    except Exception:
        begidx = buf.rfind(text)
        endidx = begidx + len(text)

    prefix = buf[:begidx]
    try:
        words = shlex.split(prefix)
    except Exception:
        words = prefix.split()

    # On first call (state==0), compute and cache matches
    if state == 0:
        _last_matches = []
        _last_prefix = text

        if not words:
            # first-word completion: combine builtins + executables then dedupe preserving order
            candidates = [c for c in (_BUILTINS + _EXECUTABLES) if c.startswith(text)]
            candidates = list(dict.fromkeys(candidates))  # remove duplicates while preserving order

            # candidates is a deduped list of matches
            if candidates:
                # try to extend to the longest common prefix (LCP)
                lcp = _longest_common_prefix(candidates)
                if len(lcp) > len(text):
                    new_matches = [c for c in candidates if c.startswith(lcp)]
                    # if LCP narrows to a single match, complete and append space
                    if len(new_matches) == 1:
                        candidate = new_matches[0]
                        if candidate.endswith("/"):
                            _last_matches = new_matches
                            return candidate
                        else:
                            _last_matches = new_matches
                            return candidate + " "
                    else:
                        # multiple matches still remain after LCP expansion; insert the LCP
                        _last_matches = new_matches
                        return lcp

            # If LCP did not extend the current text, fall back to bell/listing behavior
            if len(candidates) > 1:
                now = time.time()
                # consider this a "second Tab" only if same prefix and within the timeout
                if _tab_prefix == text and _tab_count == 1 and (now - _tab_time) <= _TAB_TIMEOUT:
                    # Second tab: print matches, reprint prompt and original buffer
                    matches_sorted = sorted(candidates)
                    sys.stdout.write("\n")
                    sys.stdout.write("  ".join(matches_sorted) + "\n")
                    # Reprint prompt and the original buffer content
                    prompt = "$ "
                    sys.stdout.write(prompt + readline.get_line_buffer())
                    sys.stdout.flush()
                    try:
                        readline.redisplay()
                    except Exception:
                        pass
                    # reset tab-tracking state
                    _tab_prefix = None
                    _tab_count = 0
                    _tab_time = 0.0
                else:
                    # First tab: ring bell and record state
                    sys.stdout.write("\x07")
                    sys.stdout.flush()
                    _tab_prefix = text
                    _tab_count = 1
                    _tab_time = now

                # cache matches for potential later requests; return None so no completion is inserted
                _last_matches = candidates
                return None

            # If exactly one command matches, treat as unique and complete normally
            _last_matches = candidates
        else:
            first = words[0]
            if first in ("echo", "cd"):
                # filesystem completion for the token being typed
                pattern = text + "*" if text != "" else "*"
                matches = glob.glob(pattern)
                # append slash marker for directories to signal they are directories
                _last_matches = [m + ("/" if os.path.isdir(m) and not m.endswith("/") else "") for m in matches]
            else:
                _last_matches = []

    # Return the state-th match, adding a trailing space if unique and appropriate
    try:
        candidate = _last_matches[state]
    except IndexError:
        return None

    # If exactly one match and it's not a directory (doesn't end with '/'), append a space
    if len(_last_matches) == 1:
        if candidate.endswith("/"):
            return candidate  # keep the slash so further completion is possible
        else:
            return candidate + " "
    else:
        return candidate





# register completer and enable Tab
readline.set_completer(_completer)
# handle macOS (libedit) vs GNU readline binding names
try:
    readline.parse_and_bind("tab: complete")
except Exception:
    try:
        readline.parse_and_bind("bind ^I rl_complete")
    except Exception:
        # if this fails, completion will be unavailable but program still runs
        pass



def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        
        #must add pipeline logic here before shlex.split treats the pipeline like a normal character and messes up the logic
        if "|" in command:
            try:
                execute_pipeline(command)
            except Exception as e:
                print(f"Error executing pipeline: {e}")
                pass
            continue #skip rest of the code for this loop since we already handled the logic

        commandArray = shlex.split(command.strip()) #convert user input into an array of words
        commandArrayLength = len(commandArray)
        
        if command == "exit":
            break

        elif not command.strip(): #if the user types nothing, just ignore it(handles edge case of nothing entered) 
            pass
        
        elif " 2>>" in command:
            cORt, fileN = command.split("2>>", 1) #split based on 2>> sign
            
            commandOrText = shlex.split(cORt.strip()) #clean the first element(command)
            fileName = fileN.strip() #clean the second element(file)
            
            try:
                with open(fileName, "a") as f: # "a" instead of "w" since we're appending because of the double >>
                    subprocess.run(commandOrText, stdout=sys.stdout, stderr=f) #run commandOrText where the first element is the command and the rest(elements after the first element are the params), stdout goes to the screen, the error gets written to the file
            except Exception as e:
                print(f"Error: {e}")


        elif " >>" in command or " 1>>" in command: # >> and 1>> are the same, this command appends to a file instead of overwriting it(hence the open command being "a" not "w")
            if " >>" in command:
                cORt, fileN = command.split(">>", 1)#split based on the >> sign
            else:
                cORt, fileN = command.split("1>>", 1)#split based on the 1>> sign
                
            commandOrText = shlex.split(cORt.strip()) #clean the first element(command)
            fileName = fileN.strip() #clean the second element(file)        
                
            try:
                with open(fileName, "a") as f:
                    subprocess.run(commandOrText, stdout=f) #run command and store output to file
            except Exception as e: #in case of error, print the error
                #print(f"Shell error: {e}")
                pass    

#note: this elif block containing functionality for 2> has to be above the block for > and 1> since if it isn't the ">" will trigger and the wrong block gets executed and we get an error
        
        elif " 2>" in command: #redirect erro(redirect stderr)
            cORt, fileN = command.split("2>", 1) #split based on 2> sign
            
            commandOrText = shlex.split(cORt.strip()) #clean the first element(command)
            fileName = fileN.strip() #clean the second element(file)

            try:
                with open(fileName, "w") as f:
                    subprocess.run(commandOrText, stdout=sys.stdout, stderr=f) #run commandOrText where the first element is the command and the rest(elements after the first element are the params), stdout goes to the screen, the error gets written to the file
            except Exception as e:
                print(f"Error: {e}")
        
        elif ">" in command or "1>" in command: #redirect stdout command
            if "1>" in command:
                cORt, fileN = command.split("1>", 1)#split based on the 1> sign
            else:
                cORt, fileN = command.split(">", 1) #split based on the > sign
                
            commandOrText = shlex.split(cORt.strip()) #clean the first element(command)
            fileName = fileN.strip() #clean the second element(file)

            try:
                with open(fileName, "w") as f:
                    subprocess.run(commandOrText, stdout=f) #run command and store output to file
            except Exception as e: #in case of error, print the error
                #print(f"Shell error: {e}")
                pass
        

        elif commandArray[0] == "echo":
            commandString = " ".join(commandArray[1:]) #echo back the entire user input minus the echo keyword
            commandStringShell = shlex.split(command) #using shlex.split instead of the regular .split helps keep the integrity of the quotes
            commandStringShellOutput = " ".join(commandStringShell[1:])
            print(commandStringShellOutput)
        
        elif commandArray[0] == "type":
            print(commandType(command))
        
        elif commandArray[0] == "pwd":
            currentPath = os.getcwd()
            print(currentPath)
        
        elif commandArray[0] == "cd":
            if directorySwitch(commandArray):
                pass #do nothing if the cd worked
            else:
                print(f"{"".join(commandArray[1:])}: No such file or directory") #cd failed
                
        
        else:
            if(shutil.which(commandArray[0])): #argument 0 since the first word is going to be the command and the other stuff is probably arguments
                filePath = shutil.which(commandArray[0])
                #print(f"{commandArray[1]} is " + filePath)

                if(os.access(filePath, os.F_OK) and os.access(filePath, os.X_OK)): #os.F_OK checks for filepath existence and os.F_OK checks for if it is executable(perms)
                    subprocess.run(commandArray, executable=filePath)


            else: 
                commandString = " ".join(commandArray[0:]) #
                print(f"{commandString}: not found")
            

if __name__ == "__main__":
    main()
