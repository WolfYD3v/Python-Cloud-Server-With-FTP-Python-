import ftputil
import ftplib
import json
import sys
import os
import time

class FTP_Client():
    ftp_host = None

    adress = "192.168.1.12"
    user = "anonymous"
    password = "anonymous@"
    port = 2221
    session_factory = None

    host_current_dir = ""
    host_current_dir_files = []

    mode = "Download"
    local = "/home/wolfyd3v/Documents/"

    def load_profile(self, profile_name: str) -> None:
        with open(f"profiles/profile_{profile_name}.json", "r") as profile_file:
            profile_data = json.loads(profile_file.read())
            self.adress = profile_data["adress"]
            self.user = profile_data["user"]
            self.password = profile_data["password"]
            self.port = profile_data["port"]
            print(f"Profile '{profile_name}' Data: {profile_data}")

    def init_session_factory(self) -> None:
        self.session_factory = ftplib.FTP
        self.session_factory.port = self.port
    
    def count_files_at(self, folder: str) -> int:
        file_count = len(self.ftp_host.listdir(folder))
        return file_count

    def list_items(self) -> None:
        self.host_current_dir = self.ftp_host.curdir
        self.host_current_dir_files = self.ftp_host.listdir(self.host_current_dir)
        self.host_current_dir_files.append("..")

        print(f"Current location: {self.ftp_host.getcwd()}")
        idx = 1
        for elem in self.host_current_dir_files:
            console_output = f"| {idx} | {elem} "
            if not self.ftp_host.path.isfile(elem): console_output += f"[{self.count_files_at(elem)} element(s)]"

            print(console_output)
            idx += 1
    
    def download_file(self, file: str) -> None:
        local_path = f"{self.local}{file}"
        local_path = local_path.replace('"', '').replace("'", "")
        self.ftp_host.download(file, local_path)
        print(f"File '{file}' Downloaded Succesfully!")
    
    '''
    def download_folder(self, folder: str) -> None:
        print(folder)
        if not os.path.exists(f"{self.local}/{folder}"): os.mkdir(f"{self.local}/{folder}")

        for file in self.ftp_host.listdir(folder):
            if self.ftp_host.path.isfile(file): self.download_file(f"{folder}/{file}")
            else:
                if not os.path.exists(f"{self.local}/{folder}/{file}"): 
                    self.download_folder(f"{folder}/{file}")
                    #os.mkdir(f"{self.local}/{folder}/{file}")
    '''
    
    def download_folder(self, folder: str) -> None:
        # Walk through the remote directory tree
        for root, dirs, files in self.ftp_host.walk(folder):
            # Calculate the relative path to recreate the structure locally
            rel_path = os.path.relpath(root, folder)
            local_root = os.path.join(folder, rel_path)

            # Ensure the local directory exists
            if not os.path.exists(local_root):
                os.makedirs(local_root)

            for file in files:
                remote_path = self.ftp_host.path.join(root, file)
                local_path = os.path.join(local_root, file)
                print(local_path)
                    
                # download_if_newer handles binary/text mode automatically
                self.ftp_host.download_if_newer(remote_path, self.local + local_path)
                print(f"Synced: {file}")
    
    
    def explore_files(self) -> None:
        self.list_items()

        item_idx = int(input("Type the corresponding idx: "))
        print("")
        if item_idx > 0 and item_idx <= len(self.host_current_dir_files):
            item_idx -= 1
            item_selected = self.host_current_dir_files[item_idx]

            if self.ftp_host.path.isfile(item_selected): self.manage_file(item_selected)
            else: self.manage_folder(item_selected)
                

    def manage_file(self, file: str) -> None:
        self.download_file(file)

        if self.check_for_stoping_processus(): self.stop()
        else: self.explore_files()
    
    def manage_folder(self, folder: str) -> None:
        folder_action = ""
        if folder != "..":
            folder_action = input(f"Download Folder [type 1] | Explore Files In '{folder}' [type somathing else] ")
            print("")
        if not folder_action == "1":
            self.ftp_host.chdir(folder)
            self.explore_files()
        else:
            self.download_folder(folder)
                
            if self.check_for_stoping_processus(): self.stop()
            else: self.explore_files()



    def upload(self) -> None:
        file_to_upload_path = input("Drag and drop a file/type file path here: ").strip()
        file_to_upload_path = file_to_upload_path.replace('"', '').replace("'", "")

        if os.path.isfile(file_to_upload_path): self.upload_file(file_to_upload_path)
        else: self.upload_folder(file_to_upload_path)

        if self.check_for_stoping_processus(): self.stop()
        else: self.upload()

    
    def upload_file(self, file_path: str) -> None:
        file = os.path.basename(file_path)

        with open(file_path, "rb") as source:
            with self.ftp_host.open(f"{self.ftp_host.curdir}/{file}", "wb") as target:
                self.ftp_host.copyfileobj(source, target)
        print(f"File '{file}' Upload Succesfully!")
    
    def upload_folder(self, file_to_upload_path: str) -> None:
        print(f"Uploading folder: {file_to_upload_path}")
        folder_name = os.path.basename(file_to_upload_path)
        if not self.ftp_host.path.exists(folder_name): self.ftp_host.mkdir(folder_name)
        self.ftp_host.chdir(folder_name)

        for file in os.listdir(file_to_upload_path):
            full_path = os.path.join(file_to_upload_path, file)
            if os.path.isdir(full_path): self.upload_folder(full_path)
            else:
                self.upload_file(full_path)
                time.sleep(0.1)
        
        self.ftp_host.chdir("..")
    
    def start(self) -> None:
        self.init_session_factory()
        self.ftp_host = ftputil.FTPHost(
            self.adress,
            self.user,
            self.password,
            session_factory = self.session_factory
        )


        match self.mode:
            case "Download": self.explore_files()
            case "Upload": self.upload()
            case _: self.stop(f"{self.mode} Mode Does Not Exist")
        
    def check_for_stoping_processus(self) -> bool:
        stop_process = input("Stop Process? (type something to stop the process) ")
        return stop_process != ""
    
    def stop(self, reason: str = "Processus Stoped") -> None:
        if not self.ftp_host: return

        print(reason)
        self.ftp_host.close()
        quit()


if __name__ == "__main__":
    ftp_client = FTP_Client()

    print(sys.argv)
    if len(sys.argv) > 0: ftp_client.mode = sys.argv[1]
    if len(sys.argv) > 1: ftp_client.load_profile(sys.argv[2])

    ftp_client.start()
