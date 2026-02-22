import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        commandArray = command.strip().split()
        #right now, we're treating all inputs as invalid
        if command == "exit":
            break
        elif commandArray[0] == "echo":
            commandString = " ".join(commandArray[1:])
            print(commandString)
        else:
            print(f"{command}: command not found")
        pass


if __name__ == "__main__":
    main()
