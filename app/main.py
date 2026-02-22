import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        #right now, we're treating all inputs as invalid
        if command == "exit":
            break
        else:
            print(f"{command}: command not found")
        pass


if __name__ == "__main__":
    main()
