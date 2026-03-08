import sys
import os
import shlex #shell lexicon library for word and char manipulation
import shutil #to find executable files and store their file paths
import subprocess #to execute executable files
import glob #to see all files in a directory, mainly used for tab completion functionality 
import readline #mainly for tab completion functionality 

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

def _completer(text, state):
    """
    readline completer function.

    - first word: complete builtins + executables
    - after `echo` or `cd`: complete filesystem paths (files/directories)
    - returns the `state`-th candidate or None
    """
    # get buffer and current word bounds
    buf = readline.get_line_buffer()
    try:
        begidx = readline.get_begidx()
        endidx = readline.get_endidx()
    except Exception:
        # Fallback if these aren't available: approximate using buffer and text
        begidx = buf.rfind(text)
        endidx = begidx + len(text)

    # Words typed before the current token (use only up to begidx)
    prefix = buf[:begidx]
    try:
        words = shlex.split(prefix)
    except Exception:
        # fallback to whitespace split if quoting is incomplete
        words = prefix.split()

    # Determine candidates
    if not words:
        # completing first word (command name)
        candidates = [c for c in (_BUILTINS + _EXECUTABLES) if c.startswith(text)]
    else:
        first = words[0]
        if first in ("echo", "cd"):
            # filename/path completion for the argument being typed
            # glob on the text fragment to find matching files/dirs, adding a trailing * to match anything starting with the text
            if text == "":
                pattern = "*"
            else:
                pattern = text + "*"
            matches = glob.glob(pattern)
            # append trailing slash for directories to indicate they are directories
            candidates = [m + ("/" if os.path.isdir(m) else "") for m in matches]
        else:
            # don't complete other commands' arguments by default
            candidates = []

    # readline asks for the Nth candidate via state
    try:
        candidate = _last_matches[state]
    except IndexError:
        return None
#below code is for adding a space after tab autocomplete on a command
    if len(_last_matches) == 1:
        if candidate.endswith("/"):#If exactly one match and it's not a directory (doesn't end with '/'), append a space
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
        commandArray = shlex.split(command.strip()) #convert user input into an array of words
        commandArrayLength = len(commandArray)
        
        if command == "exit":
            break
        
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
