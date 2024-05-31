import os

def remove_prefix_from_filenames(directory, prefix):
    for filename in os.listdir(directory):
        new_filename = filename.replace("_PPT","")
        old_file_path = os.path.join(directory, filename)
        new_file_path = os.path.join(directory, new_filename)
        os.rename(old_file_path, new_file_path)

# 使用方法
directory_path = 'E:\数学\pdf'  # 指定目录路径
prefix_to_remove = '去水印-'  # 需要去掉的前缀
remove_prefix_from_filenames(directory_path, prefix_to_remove)