import os
import shutil

file_path = input("Enter your file path :  ")
filecrepath = input(" Enter your File creating path :  ")
images = ["jpg", "png", "jpeg", "gif"]
Documents = ["pdf", "docx", "txt", "xlsx"]
Videos = ["mp4", "mkv", "avi"]
Audio = ["mp3", "wav"]
Executables = ["exe", "bat", "msi"]
Archives = ["zip", "rar", "7z"]
image_count = 0
video_count = 0
document_count = 0
audio_count = 0
Executable_count = 0
archives_count = 0
if not os.path.exists(file_path):
    print("There is no file in your path")
else:
    print("File founded successfully")
no_of_files = len(os.listdir(file_path))
list_dir = os.listdir(file_path)
print(f" The number of files in this directory : {no_of_files}")
for file in list_dir:
    file_format = file.split(".")[-1].lower()
    print(file_format)
    if file_format in images:
        image_count += 1  
        os.makedirs(os.path.join(filecrepath,"Images"), exist_ok= True)
        isnr = os.path.join(file_path,file)
        idsn = os.path.join(filecrepath,"Images",file)
        shutil.move(isnr,idsn)
    if file_format in Videos:
        video_count += 1
        os.makedirs(os.path.join(filecrepath,"Videos"),exist_ok=True)
        vsnr = os.path.join(file_path,file)
        vdsn = os.path.join(filecrepath,"Videos",file)
        shutil.move(vsnr,vdsn)
    if file_format in Audio:
        audio_count += 1
        os.makedirs(os.path.join(filecrepath,"Audios"),exist_ok=True)
        snr = os.path.join(file_path,file) 
        dsn = os.path.join(filecrepath,"Audios",file)
        shutil.move(snr,dsn)
    if file_format in Documents:
        document_count += 1
        os.makedirs(os.path.join(filecrepath,"Documents"),exist_ok=True)
        dsns = os.path.join(file_path,file)
        ddsn = os.path.join(filecrepath,"Documents",file)
        shutil.move(dsns,ddsn)
    if file_format in Executables:
        Executable_count += 1
        os.makedirs(os.path.join(filecrepath,"Executables"),exist_ok= True)
        esns = os.path.join(file_path,file)
        edsn = os.path.join(filecrepath,"Executables",file)
        shutil.move(esns,edsn)
    if file_format in Archives:
        archives_count += 1
        os.makedirs(os.path.join(filecrepath,"Archives"),exist_ok= True)
        asns = os.path.join(file_path,file)
        adsn = os.path.join(filecrepath,"Archives",file)
        shutil.move(asns,adsn)
print(f" {image_count} files were moved in Images Folder")
print(f" {video_count} files were moved in Videos Folder")
print(f" {audio_count} files were moved in Audios Folder")
print(f" {document_count} files were moved in Documents Folder")
print(f" {Executable_count} files were moved in Executables Folder")
print(f" {archives_count} files were moved in Archive Folder")
