import os, shutil
from tkinter import Tk
from tkinter.filedialog import askdirectory

def main():
    input("Make sure Python 3.11.x or higher is installed before using the installer [ENTER]")
    Tk().withdraw()
    print("Select install directory...")
    path = askdirectory()
    print("Installing to " + path)
    os.system("pip install pipreqs && pipreqs --force && pip install -r requirements.txt")
    shutil.copyfile("./bin/driver.py", path + "/driver.py")
    shutil.copyfile("./bin/main.py", path + "/main.py")
    _path = r"C:/ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/"
    with open(_path+"mondia.bat", "w") as f:
        f.write("py " + path + "/main.py")


if __name__ == "__main__":
    main()