import os
import subprocess
from configparser import ConfigParser
from datetime import datetime
from time import sleep

class SyncException(Exception):
    pass


class Sync:
    REMOTE = "origin"
    BRANCH = "master"
    GIT_IGNORE = ".obsidian/workspace.json"
    def __init__(self, vaultPath:str, remoteUrl:str, cooldown:int=60*5,remote:str=REMOTE, branch:str=BRANCH):
        self.cooldown = cooldown
        self.remote = remote
        self.branch = branch
        self.remoteUrl = remoteUrl

        self.vaultPath = vaultPath
        self.vaultGitPath = os.path.abspath(os.path.join(self.vaultPath,".git"))
        self.vaultGitConfigPath = os.path.abspath(os.path.join(self.vaultGitPath,"config"))
        self.vaultGitIgnorePath = os.path.abspath(os.path.join(self.vaultPath,".gitignore"))

        if not os.path.exists(self.vaultPath): raise(SyncException(f"{self.vaultPath} not exists"))
        if not os.path.exists(os.path.abspath(os.path.join(self.vaultPath,".obsidian"))): raise(SyncException(f"{self.vaultPath} is not obsidian vault"))

        if not os.path.exists(self.vaultGitPath):
            self.git("init")

        if not os.path.exists(self.vaultGitIgnorePath):
            with open(self.vaultGitIgnorePath,"w",encoding="UTF-8") as f: f.write(Sync.GIT_IGNORE)
            self.git(f"rm -rf --cached .")
            self.commit_all()

        self.config = ConfigParser()
        self.config.read(self.vaultGitConfigPath)

        self.set_remote(self.remoteUrl)
        self.set_branch()

    def git(self,cmd:str):
        # cmd = ["cmd","/c","git",*cmd.split()]
        # print(cmd)
        process = subprocess.Popen("git "+cmd, stdout=subprocess.PIPE, cwd=self.vaultPath)
        output, unused_err = process.communicate()
        print(output)


    def save_config(self):
        with open(self.vaultGitConfigPath,"w") as f:
            self.config.write(f)

    def set_remote(self, url:str):
        if(f'remote "{self.remote}"' not in self.config.sections()):
            self.config.add_section(f'remote "{self.remote}"')
        self.config[f'remote "{self.remote}"']["url"] = url
        self.config[f'remote "{self.remote}"']["fetch"] = f'+refs/heads/*:refs/remotes/{self.remote}/*'
        self.save_config()
        #os.system(f"git remote add origin {url}")

    def set_branch(self):
        if(f'branch "{self.branch}"' not in self.config.sections()):
            self.config.add_section(f'branch "{self.branch}"')
        self.config[f'branch "{self.branch}"']["remote"] = self.remote
        self.config[f'branch "{self.branch}"']["merge"] = f"refs/heads/{self.branch}"
        self.save_config()
        #os.system(f"git branch -M {self.branch}")

    def commit_all(self):
        self.git("add .")
        self.git(f'commit -m "sync {datetime.now().strftime("%d/%m/%y %H:%M:%S")}"')

    def push(self):
        self.git(f"push -u {self.remote} {self.branch}")

    def pull(self):
        self.git(f"pull origin master --allow-unrelated-histories")

    def sync(self):
        while True:
            self.pull()
            self.commit_all()
            self.push()
            sleep(self.cooldown)