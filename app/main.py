import sys
import os
import shutil #to find executable files and store their file paths
import subprocess #to execute executable files

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
            
            if commandArrayLength == 2:
                #array of exit,echo,type, or other commands(currently invalid) then printf with corresponding text
                typeArr = ["echo", "exit", "type"]
                
                if commandArray[1]in typeArr: #right now, the only valid words after type are echo,exit, and type
                    print(f"{commandArray[1]} is a shell builtin") #since the input is just two words(two elements), we can use the second word which the user wants the type of as arrayIndex[1]
                
                elif(shutil.which(commandArray[1])):
                    filePath = shutil.which(commandArray[1])
                    print(f"{commandArray[1]} is " + filePath)
                
                else: 
                    commandString = " ".join(commandArray[1:]) #
                    print(f"{commandString}: not found")
            else:
                commandString = " ".join(commandArray[1:])
                print(f"{commandString}: not found")
        
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
