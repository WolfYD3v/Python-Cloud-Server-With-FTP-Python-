import ftputil
import ftplib
import json
import sys

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

    def list_items(self) -> bool:
        self.host_current_dir = self.ftp_host.curdir
        self.host_current_dir_files = self.ftp_host.listdir(self.host_current_dir)
        self.host_current_dir_files.append("..")
        if len(self.host_current_dir_files) <= 0: return False

        idx = 1
        for elem in self.host_current_dir_files:
            print(f"{idx}| {elem}")
            idx += 1
        
        return True
    
    def select_item(self, mode: str = "Download") -> None:
        if not self.list_items():
            self.ftp_host.chdir("..")
            self.select_item()
            #self.stop("No Items Found!")

        item_idx = int(input("Type the corresponding idx: "))
        if item_idx > 0 and item_idx <= len(self.host_current_dir_files):
            item_idx -= 1
            item_selected = self.host_current_dir_files[item_idx]

            if self.ftp_host.path.isfile(item_selected):
                self.ftp_host.download(item_selected, f"/home/wolfyd3v/Documents/{item_selected}")
                self.stop(f"File '{item_selected}' Downloaded Succesfully!")
            else:
                self.ftp_host.chdir(item_selected)
                self.select_item()
    
    def upload_file(self, file_to_upload: str = "CAR_APP.fig") -> None:
        with open(f"/home/wolfyd3v/Bureau/{file_to_upload}", "rb") as source:
            with self.ftp_host.open(f"{self.ftp_host.curdir}/{file_to_upload}", "wb") as target:
                self.ftp_host.copyfileobj(source, target)
        self.stop(f"File '{file_to_upload}' Upload Succesfully!")
    
    def start(self) -> None:
        self.init_session_factory()
        self.ftp_host = ftputil.FTPHost(
            self.adress,
            self.user,
            self.password,
            session_factory = self.session_factory
        )


        match self.mode:
            case "Download": self.select_item()
            case "Upload": self.upload_file()
            case _: self.stop(f"{self.mode} Mode Does Not Exist")
        
    
    def stop(self, reason: str = "FTP Server Closed") -> None:
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
