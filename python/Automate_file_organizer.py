import os
import shutil

images = ["jpg", "png", "jpeg", "gif"]; Documents = ["pdf", "docx", "txt", "xlsx"]; Videos = ["mp4", "mkv", "avi"]; Audio = ["mp3", "wav"]; Executables = ["exe", "bat", "msi"]; Archives = ["zip", "rar", "7z"]
img_ct = 0; vid_ct = 0; doc_ct = 0; aud_ct = 0; Exe_ct = 0; arch_ct = 0
file_path = input("Enter your file path : ")
folder_cre_path = input(" Enter the path where you want to create the folder : ")
if not os.path.exists(file_path):
    print(" File weren not found")
else:
    print("file were found successfully")
no_of_files = len(os.listdir(file_path))
print(no_of_files)
lst_dir = os.listdir(file_path)
def fol_cre_fle_mov(file_type, increment_var, folder_cre_path, folder_name, file_path, file ):
    file_format = file.split(".")[-1].lower()
    if file_format in file_type:
        increment_var +=1
        os.makedirs(os.path.join(folder_cre_path,folder_name),exist_ok= True)
        snr = os.path.join(file_path,file)
        dns = os.path.join(folder_cre_path,folder_name,file)
        shutil.move(snr,dns)
    return increment_var      
for file in lst_dir:
    img_ct = fol_cre_fle_mov( images, img_ct, folder_cre_path, "Images" , file_path, file)       
    vid_ct = fol_cre_fle_mov(Videos, vid_ct, folder_cre_path, "Videos", file_path, file)
    doc_ct = fol_cre_fle_mov(Documents, doc_ct, folder_cre_path, "Documents", file_path, file)
    aud_ct = fol_cre_fle_mov(Audio, aud_ct , folder_cre_path, "Audios", file_path, file)
    Exe_ct = fol_cre_fle_mov(Executables, Exe_ct, folder_cre_path, "Executables", file_path, file)
    arch_ct = fol_cre_fle_mov(Archives, arch_ct , folder_cre_path, "Archives", file_path, file)
print(f"{"="*110}\n{" "*50} Summary {" "*50} \n{"="*110}")    
print(f"{img_ct} files were moved Images folder")       
print(f"{vid_ct} files were moved Videos folder") 
print(f"{doc_ct} files were moved Documents folder")  
print(f"{aud_ct} files were moved Audio folder")
print(f"{Exe_ct} files were moved Executables folder") 
print(f"{arch_ct} files were moved Archives folder") 