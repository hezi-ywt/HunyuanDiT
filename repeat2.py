import os
import json
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

lock = threading.Lock()

def isimage(file):
    """判断文件是否为图片"""
    end = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".PNG", ".JPG", ".JPEG", ".WEBP", ".BMP"]
    return any(file.endswith(i) for i in end)

def get_file_list(folder_path):
    """ 获取指定文件夹中的所有文件列表 """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if isimage(file):
                file_list.append(os.path.join(root, file))
    return file_list

def count_image_occurrences(file_list):
    """ 统计每个图片名称出现的次数 """
    image_count = {}
    for file in file_list:
        filename = os.path.basename(file)
        if filename in image_count:
            image_count[filename] += 1
        else:
            image_count[filename] = 1
    return image_count

def copy_image(file, meta_data, destination_folder, missing_files):
    """ 复制单个图片到对应文件夹中 """
    filename = str(os.path.basename(file).split('.')[0])

    if filename in meta_data:
        count = meta_data[filename].get("rp_num", 1)
        destination_path = os.path.join(destination_folder, f"{count}_repeat")
        
        # 使用锁来保证线程安全地创建目录
        with lock:
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
                
        shutil.copy(file, destination_path)
    else:
        print(f"File {filename} not found in metadata")
        missing_files.append(file)

def copy_images_to_folders_parallel(file_list, meta_data, destination_folder):
    """ 使用多线程并行复制图片到对应文件夹，并显示进度条 """
    missing_files = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(copy_image, file, meta_data, destination_folder, missing_files) for file in file_list]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Copying images"):
            future.result()
    
    return missing_files

def main():
    source_folder = "/home1/qbs/my_program1/datahun2/base"  # 替换为你的源文件夹路径
    destination_folder = "/home1/qbs/my_program1/datahun2/base_out"  # 替换为你的目标文件夹路径
    data_file = "/home1/qbs/my_program1/datahun2/caption.json"  # 替换为你的数据文件路径
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
    with open(data_file, 'r') as file:
        data = json.load(file)
    

    # 获取文件列表
    file_list = get_file_list(source_folder)

    # 复制图片到对应文件夹
    missing_files = copy_images_to_folders_parallel(file_list, data, destination_folder)
    
    # 处理未出现在字典中的文件名
    if missing_files:
        missing_folder = os.path.join(destination_folder, "missing_files")
        if not os.path.exists(missing_folder):
            os.makedirs(missing_folder)
        for file in missing_files:
            shutil.copy(file, missing_folder)
        print(f"共有 {len(missing_files)} 张图片不在字典中，它们已被复制到 {missing_folder} 文件夹中")

    print("图片已成功分类到对应文件夹中")
    
    for dir in os.listdir(destination_folder):
        dir_path = os.path.join(destination_folder, dir)
        if os.path.isdir(dir_path):
            print(f"文件夹 {dir} 中有 {len(os.listdir(dir_path))} 张图片")
            

                    
def remove_files():

    from concurrent.futures import ThreadPoolExecutor, as_completed

    # 读取目标 JSON 文件
    target_json = "/data2/hydit_basic_pids/hy_qq_pids.json"

    with open(target_json, 'r') as file:
        target_data = set(json.load(file))  # 使用集合以提高查找速度

    remove = 0
    destination_folder = "/data2/hunyuan_v3_out"  # 设定你的目标文件夹

    # 定义一个函数用于处理单个目录的文件
    def process_directory(dir_path):
        local_remove = 0  # 本地计数器
        for file in os.listdir(dir_path):
            pid = file.split(".")[0]
            if int(pid) not in target_data:
                try:
                    os.remove(os.path.join(dir_path, file))
                    local_remove += 1
                except Exception as e:
                    print(f"删除文件 {file} 时出错: {e}")
        return local_remove

    # 创建线程池并分配任务
    with ThreadPoolExecutor() as executor:
        futures = []
        for dir in os.listdir(destination_folder):
            dir_path = os.path.join(destination_folder, dir)
            if os.path.isdir(dir_path):
                futures.append(executor.submit(process_directory, dir_path))

        # 收集所有线程的返回值并计算总删除数
        for future in as_completed(futures):
            try:
                local_remove = future.result()
                remove += local_remove
            except Exception as e:
                print(f"处理目录时出错: {e}")

    print(f"共删除 {remove} 张图片")
    for dir in os.listdir(destination_folder):
        dir_path = os.path.join(destination_folder, dir)
        if os.path.isdir(dir_path):
            print(f"文件夹 {dir} 中有 {len(os.listdir(dir_path))} 张图片")
    
if __name__ == '__main__':
    main()
    # remove_files()
