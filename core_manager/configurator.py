import os.path
import glob

from helpers.yamlio import read_yaml_all, write_yaml_all, CONFIG_FOLDER_PATH
from helpers.config_parser import logger, config


def configure():

    print("Current Configs:")
    print(config)
    print("\n")

    for file in glob.glob(CONFIG_FOLDER_PATH + "/config_request*.yaml"):
        try:
            file_content = read_yaml_all(file)
        except Exception as e:
            logger.error("configure() - read_yaml_all --> " + str(e))
        else:
            print(file)
            print(file_content)
            print("\n")


if __name__ == "__main__":
    configure()