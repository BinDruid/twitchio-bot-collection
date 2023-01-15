import sys
from src.utils.exec_command import ExeCommandLine


def main():
    command = ExeCommandLine(sys.argv)
    bot = command.create_bot()
    bot.run()


if __name__ == "__main__":
    main()
