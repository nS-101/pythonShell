import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    sys.stdout.write("$ ")
    command = input("")
    #right now, we're treating all inputs as invalid
    if command:
        print(f"{command}: command not found")
    else:
        print(f"{command}: command not found")
    pass


if __name__ == "__main__":
    main()
