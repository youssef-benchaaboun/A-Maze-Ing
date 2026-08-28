import sys
from MazeConfig import ConfigLoader
from MazeApplication import MazeApplication


def main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        print(f"Usage: {arguments[0]} config.txt", file=sys.stderr)
        return 1

    config, error = ConfigLoader.load_config(arguments[1])
    if error or config is None:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    application = MazeApplication(config)
    return application.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
