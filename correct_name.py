
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))


import shutil

def rename_files(path):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path):
            # 如果是文件夹，则递归调用重命名函数
            rename_files(file_path)
        else:
            try:
                # 尝试用utf-8解码文件名，如果能成功，则不是乱码
                decoded_file_name = file_name.encode('utf-8').decode('utf-8')
                if decoded_file_name != file_name:
                    # 文件名有变化，说明有乱码，进行重命名
                    new_file_path = os.path.join(path, decoded_file_name)
                    os.rename(file_path, new_file_path)
                    print(f'Renamed file {file_path} to {new_file_path}')
            except UnicodeDecodeError:
                # 解码失败，说明是乱码，进行重命名
                new_file_name = 'renamed-' + file_name
                new_file_path = os.path.join(path, new_file_name)
                os.rename(file_path, new_file_path)
                print(f'Renamed file {file_path} to {new_file_path}')

        if os.path.isdir(file_path):
            try:
                # 尝试用utf-8解码文件夹名，如果能成功，则不是乱码
                decoded_folder_name = file_name.encode('utf-8').decode('utf-8')
                if decoded_folder_name != file_name:
                    # 文件夹名有变化，说明有乱码，进行重命名
                    new_folder_path = os.path.join(path, decoded_folder_name)
                    shutil.move(file_path, new_folder_path)
                    print(f'Moved folder {file_path} to {new_folder_path}')
            except UnicodeDecodeError:
                # 解码失败，说明是乱码，进行重命名
                new_folder_name = 'renamed-' + file_name
                new_folder_path = os.path.join(path, new_folder_name)
                shutil.move(file_path, new_folder_path)
                print(f'Moved folder {file_path} to {new_folder_path}')

if __name__ == '__main__':
    rename_files('./')