import sys
import os
import shutil #to find executable files and store their file paths
import subprocess #to execute executable files

def commandType(userCommand):
    validTypeArr = ["echo","exit","pwd","cd","type"]
    userCommandArr = userCommand.strip().split()
    if len(userCommandArr) < 2:
        return(f"{userCommandArr[1:]}: not found")
    else:
        if userCommandArr[1] in validTypeArr:
            return(f"{userCommandArr[1]} is a shell builtin")
        elif shutil.which(userCommandArr[1]):
            filePath = shutil.which(userCommandArr[1])
            return(f"{userCommandArr[1]} is {filePath}")
        else:
            return(f"{userCommandArr[1:]}: not found")
        
def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        commandArray = command.strip().split() #convert user input into an array of words
        commandArrayLength = len(commandArray)
        #right now, we're treating all inputs as invalid
        
        if command == "exit":
            break
        
        elif commandArray[0] == "echo":
            commandString = " ".join(commandArray[1:]) #echo back the entire user input minus the echo keyword
            print(commandString)
        
        elif commandArray[0] == "type":
            print(commandType(command))
        
        elif commandArray[0] == "pwd":
            currentPath = os.getcwd()
            print(currentPath)
        
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
