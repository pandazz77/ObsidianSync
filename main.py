from sync import Sync
from platform import system
from os import getenv, path, mkdir
from configparser import ConfigParser
from sys import argv, exit

CONFIG_DIR_POSTFIX = "ObsidianSync"
CONFIG_POSTFIX = path.join(CONFIG_DIR_POSTFIX,"config.ini")

DEFAULT_CONFIG="""

"""

def parse_argv(argv:list):
    result = {
        "vault":None,
        "url":None,
        "remote":"origin",
        "branch":"master",
        "cooldown":str(60*5)
    }
    for i in range(len(argv)):
        if argv[i] == "-vault":
            result["vault"] = " ".join(argv[i+1:])
        elif argv[i] == "-url":
            result["url"] = argv[i+1]
        elif argv[i] == "-cooldown":
            result["cooldown"] = argv[i+1]
        elif argv[i] == "-remote":
            result["remote"] = argv[i+1]
        elif argv[i] == "-branch":
            result["branch"] = argv[i+1]

    result_copy = result.copy()

    for k in result.keys():
        if not result[k]:
            result_copy.pop(k)

    return result_copy

if __name__ == "__main__":
    OS = system()
    if(OS=="Windows"):
        configDir = path.abspath(path.join(getenv("APPDATA"), CONFIG_DIR_POSTFIX))
        configPath = path.abspath(path.join(getenv("APPDATA"), CONFIG_POSTFIX))
    elif(OS=="Linux"):
        configDir = path.abspath(path.join(getenv("HOME"), CONFIG_DIR_POSTFIX))
        configPath = path.abspath(path.join(getenv("HOME"),CONFIG_POSTFIX))

    print(configPath)
    if not path.exists(configPath) or len(argv)>1:
        if not(path.exists(configDir)): mkdir(configDir)
        parsed_argv = parse_argv(argv)
        cfg = ConfigParser()
        if path.exists(configPath): cfg.read(configPath)
        else: cfg["SETTINGS"]={}
        for key in parsed_argv.keys():
            cfg["SETTINGS"][key] = parsed_argv[key]
        with open(configPath,"w") as f:
            cfg.write(f)
        print(f"New config | path={configPath} | values={parsed_argv}")

    cfg = ConfigParser()
    cfg.read(configPath)
    if "vault" not in cfg["SETTINGS"]:
        print("Please set vault path")
        exit(1)
    elif "url" not in cfg["SETTINGS"]:
        print("Please set remote url")
        exit(1)
        

    s = Sync(cfg["SETTINGS"]["vault"],cfg["SETTINGS"]["url"],int(cfg["SETTINGS"]["cooldown"]),cfg["SETTINGS"]["remote"],cfg["SETTINGS"]["branch"])
    s.sync()
