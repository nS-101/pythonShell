import sys
import os
import shlex #shell lexicon library for word and char manipulation
import shutil #to find executable files and store their file paths
import subprocess #to execute executable files

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


def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        commandArray = shlex.split(command.strip()) #convert user input into an array of words
        commandArrayLength = len(commandArray)
        
        if command == "exit":
            break
        
        elif ">" in command or "1>" in command: #redirect stdout command
            cORt, fileN = command.split(">", 1) #split based on the > sign and split into two elements: the command/text and the file name
            
            commandOrText = shlex.split(cORt.strip())
            fileName = fileN.strip()

            try:
                with open(fileName, "w") as f:
                    subprocess.run(commandOrText, stdout=f) #run command and store output to file
            except Exception as e: #in case of error, print the error
                print(f"Shell error: {e}")



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
            if directorySwitch(command):
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
