import sys


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
                if commandArray[1]in typeArr:
                    print(f"{commandArray[1]} is a shell builtin")
                else: #right now, the only valid words after type are echo,exit, and type
                    commandString = " ".join(commandArray[1:])
                    print(f"{commandString}: not found")

            else:
                commandString = " ".join(commandArray[1:])
                print(f"{commandString}: not found")
        else:
            print(f"{command}: command not found")
        pass


if __name__ == "__main__":
    main()
