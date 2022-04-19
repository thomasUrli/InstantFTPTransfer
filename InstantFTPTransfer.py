import ftplib
import getpass
import os
from mutagen.id3 import ID3NoHeaderError, ID3, APIC, TIT2, TPE1, TALB

osuser = getpass.getuser()
musica = "C:\\Users\\"+osuser+"\\Music"
desktop = "C:\\Users\\"+osuser+"\\Desktop"
downloads = "C:\\Users\\"+osuser+"\\Downloads"
errMessage = "Non existing option! Retry: "
imgsize ="512"
downdir = ""
defaultPort = 21

telIP = ""
telPort = 0
telUser = ""
telPW = ""
raspiIP = os.environ["RASPI_IP"]
raspiUser = os.environ["RASPI_USER"]
raspiPW = os.environ["RASPI_PW"]

#Function definition area
def intInput(message, min, max):  # input functions
    var = input(message)

    while var.isalpha() or var == "" or int(var) < min or int(var) > max:
        var = input(errMessage)

    var = int(var)

    return var


def strInput(message, opt1, opt2):
    var = str(input(message))

    if opt1 == 0 and opt2 == 0:
        while var == "" or var.isalpha():
            var = str(input(errMessage))

    else:
        while var == "" or var.lower() != opt1.lower() and var.lower() != opt2.lower():
            var = str(input(errMessage))


    return var


def serverCheck():
    connected = False

    while not connected:       #check if server is reachable
        try:
            print("\nLogging in...")
            ftp.connect(ip, port)
            connected = True

        except (TimeoutError, ConnectionRefusedError):
            ans = strInput("Server not reachable. Retry connecting?(Y/N): ", 'y', 'n')

            if ans == 'N' or ans == 'n':
                quit()


def positionName(n):
    pos = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]

    return pos[n]


def nameCheck(file):
    newfile = file
    pos = -1
    i = 0
    banned_charachters = ['\\', '/', ':', '*', '?', '"', '<', ">", '|']

    try:
        while file.index('?', pos+1):
            pos = file.index('?')
            rep = str(input("Replace the "+positionName(i)+" ? with (invalid charachters: "+"".join(banned_charachters)+"): "))

            while rep == "" or banned_charachters.__contains__(rep):
                if rep == "":
                    rep = str(input("Insert at least one character: "))

                if banned_charachters.__contains__(rep):
                    rep = str(input("Invalid charachter! Insert a valid one: "))

            newfile = file[:pos] + rep + file[pos+1:]
            i += 1

    except ValueError:
        pass

    return newfile


def ddir(var):
    if osuser != "thomas":
        d = desktop

    else:
        d = var

    return d

def ftpDir(s):
    global dir

    if s == 1: #FTP directory assignment
        dir = '/downloads'

    elif s == 2:
        dir = '/Thomas'


def assignValues(s):
    global ip
    global port
    global user
    global pw
    global trunc
    global downdir

    if s == 1:  # per device values
        ip = telIP
        port = telPort
        user = telUser
        pw = telPW
        trunc = 55
        downdir = ddir(musica)

    elif s == 2:
        ip = raspiIP
        port = defaultPort
        user = raspiUser
        pw = raspiPW
        trunc = None

        sdir = intInput("\nSelect the download folder:\n1) Music\n2) Desktop\nFolder: ", 1, 2)

        if sdir == 1:

            downdir = ddir(musica)

        elif sdir == 2:
            downdir = ddir(desktop)

    else:
        ip = strInput("IP Address: ", 0, 0)
        port = intInput("Port(0 for default): ", 0, 65535)
        if port == 0:
            port = defaultPort

        explore = strInput("\nOpen it in explorer(Y/N)?", "Y", "N")

        if explore == "y":
            os.system("explorer.exe ftp://" + ip + ":" + str(port))
            quit()


def getFiles():  # get files in the actual folder
    namelist = ftp.nlst()
    outfilelist = []
    x = 0

    for names in namelist:
        global start
        if names == namelist[0] and names == "total " + str(len(namelist) - 1):
            start = 1
            pass
        else:
            outfilelist.append(str(names[trunc:]))

    x = x + 1
    return outfilelist


def printFiles(filenames):  # download functions
    global y
    y = 1
    for i in filenames:
        print(str(y) + ") " + i)
        y += 1


def isFile(file):
    try:
        current_dir = ftp.pwd()
        ftp.cwd(file)
        ftp.cwd(current_dir)

    except ftplib.error_perm as e:
        e = str(e)
        if e.find("550") == 0:
            return True

    return False


def ismp3(file):
    if os.path.splitext(file)[1] == ".mp3" or os.path.splitext(file)[1] == ".MP3":
        return True

    else:
        return False


def childDir():
    if sel == 1:
        child = ""

    else:
        child = ((ftp.pwd()).replace('/', '\\'))

    return child


def modifyTag(filepath):
    name = os.path.split(filepath)[1]
    name = name.partition(' - ')
    name = list(name)
    del name[1]
    artist = name[0]
    title = os.path.splitext(name[1])[0]

    print("Modifying Tag...")

    try:
        file = ID3(filepath)
        tags=True

    except ID3NoHeaderError:
        file = ID3()
        tags=False

    # try:
    #     if tags:
    #         if str(file["APIC:"].data).__contains__("b"):
    #             pass
    #
    #     else:
    #         raise ValueError
    #
    # except (KeyError, TypeError, ValueError):
    #     print("\nDownloading cover art...")
    #     os.system("sacad "+"\""+str(artist)+"\""+" \""+title+"\""+" \""+imgsize+"\""+" \""+os.path.join(downdir, "cover.jpg")+"\""+" -d")
    #
    #     try:
    #         image = open(os.path.join(downdir, "cover.jpg"), 'rb').read()
    #         print("Applying cover art...")
    #         file.add(APIC(encoding=0, mime="image/jpeg", type=0, desc="", data=image))
    #         os.remove(os.path.join(downdir, "cover.jpg"))
    #
    #     except FileNotFoundError:
    #         pass

    try:
        if file["TIT2"] == title:
            pass

        else:
            file["TIT2"] = TIT2(encoding=3, text=title)

    except KeyError:
        file["TIT2"] = TIT2(encoding=3, text=title)

    try:
        if file["TPE1"] == artist:
            pass

        else:
            file["TPE1"] = TPE1(encoding=3, text=artist)

    except KeyError:
            file["TPE1"] = TPE1(encoding=3, text=artist)

    file["TALB"] = TALB(encoding=3, text="")

    file.save(filepath, v2_version=3)

    print("Done!")

#end of function declaration area

if __name__ == "__main__":
    go = 1
    while go == 1:
        os.system('cls')
    
        sel = intInput("What do you want to connect to?\n1) Phone\n2) Raspberry Pi\n3) Custom\n0) Quit\nAnswer: ", 0, 3)
    
        if sel == 0:
            quit()
    
        assignValues(sel)
    
        ftp = ftplib.FTP()
    
        serverCheck()
    
        ftp.login(user, pw)
    
        ftpDir(sel)
    
        #else:
            #getFolders()
            #dir = input("\nSelect the folder: ")
    
        go = 2
        passed = False
        while go == 2:
            if passed:      #passed == True (if the user has already passed through this point, and wants to download other files, clear the screen)
                os.system('cls')
            else:
                print("\nChanging to "+dir+'\n')
                ftp.cwd(dir)
    
            files_selected = False
    
            print("Files:")
    
            def downloadFiles(sdelete):  # function where files are downloaded
                global files_selected
                global bdelete
    
                filelist = getFiles()
                printFiles(filelist)
    
                if sel == 2 and downdir == desktop and files_selected == False:  # file selection section
                    listfile = []
    
                    numbers = str(
                        input("\nInsert the number of the files you want to download, separated by a comma(0 for all): "))
    
                    while numbers == "":  # file selection check
                        numbers = str(input("No file selected! Select at least one file: "))
    
                    numbers = list(int(z) for z in numbers.split((',')))
    
                    for n in numbers:
                        while n < 0 or n > len(filelist):
                            newnumber = int(input("File " + str(n) + " not existing! Substitute with: "))
                            pos = int(numbers.index(n))
                            numbers[pos] = newnumber
                            n = newnumber
    
                    if numbers[0] == 0:
                        pass
    
                    else:
                        for i in numbers:
                            listfile.append(str(filelist[i - 1]))
    
                        filelist = listfile
    
                    files_selected = True
    
                    sdelete = strInput("\nDelete files after download?(Y/N): ", 'y', 'n')  # ask for file deletion
    
                    if sdelete == 'Y' or sdelete == 'y':
                        bdelete = True
    
                    else:
                        bdelete = False
    
                if downdir == musica:
                    pass
    
                else:
                    try:
                        os.mkdir(downdir + dir.replace('/', '\\'))
    
    
                    except FileExistsError:
                        pass
    
                for files in filelist:  # download section
                    if isFile(files):  # if it's a file, download it
                        name = nameCheck(files)
    
                        if files_selected:
                            pass
    
                        else:
                            sdelete = strInput("\nDelete files after download?(Y/N): ", 'y', 'n')  # ask for file deletion
                            files_selected = True
    
                        if sdelete == 'Y' or sdelete == 'y':
                            bdelete = True
    
                        else:
                            bdelete = False
    
                        if ismp3(files):  # ismp3 == True
    
                            if downdir == musica:
                                findir = downdir
    
                                print("\nDownloading: " + files)
                                file = open(os.path.join(downdir, name), 'wb')
                                ftp.retrbinary('RETR ' + files, file.write)
                                file.close()
    
                                if bdelete:
                                    ftp.delete(files)
    
                            else:
                                global child_directory
    
                                child_directory = childDir()
                                findir = downdir + child_directory
    
                                print("\nDownloading " + files)
                                file = open(os.path.join(findir, name), 'wb')
                                ftp.retrbinary('RETR ' + files, file.write)
                                file.close()
    
                                if bdelete:
                                    ftp.delete(files)
    
                                modifyTag(findir + '\\' + files)
    
                        else:
    
                            child_directory = childDir()
                            findir = downdir + child_directory
    
                            print("\nDownloading "+ files)
                            file = open(os.path.join(findir, name), 'wb')
                            ftp.retrbinary('RETR ' + files, file.write)
                            file.close()
    
                            if bdelete:
                                ftp.delete(files)
    
    
                    else:  # if it's not a file, enter the folder on the ftp server and create a folder in the download directory
                        print("\nEntering: " + files)
    
                        pdir = ftp.pwd()
                        ftp.cwd(files)
                        if downdir == musica:
                            pass
    
                        else:
                            try:
                                child_directory = childDir()
                                os.mkdir(downdir + child_directory)
    
                            except FileExistsError:
                                pass
    
                        downloadFiles(sdelete)
                        ftp.cwd(pdir)
    
                        if bdelete:
                            ftp.rmd(files)
    
                return
    
            downloadFiles("n")
    
            go = intInput("\nTo change device insert 1, to download other files insert 2, to quit insert 0: ", 0, 2)
    
            if go == 2:
                passed = True
    
            elif go == 0:
                quit()