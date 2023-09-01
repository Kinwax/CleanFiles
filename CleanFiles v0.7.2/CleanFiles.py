# -*- coding: gbk -*-

import sys
import os
import subprocess
import stat
import shutil
import configparser


def read_keywords_from_file():
    ini_path = os.path.join(os.path.dirname(sys.executable), "CleanFiles.txt")
    with open(ini_path, 'r', encoding='utf-8') as ini_file:
        lines = ini_file.readlines()

    current_section = None
    for line in lines:
        line = line.strip()  # 去掉首尾空白字符
        if not line:
            continue  # 跳过空行
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]  # 提取部分名称
            keyword_dicts[current_section] = []  # 创建一个空的关键字列表
        elif current_section is not None:
            keyword_dicts[current_section].append(line)  # 将关键字添加到当前部分的列表中

    print(f"Reading keywords from: {ini_path}")
    print(keyword_dicts)
    assert "full_keywords" in keyword_dicts
    assert "contains_all_keywords" in keyword_dicts
                                                               
def full_keywords(text):
    full_keywords_list = keyword_dicts["full_keywords"]
    match = any(keyword in text for keyword in full_keywords_list)
    return match

def all_keywords(text):
    contains_all_keywords_dict = keyword_dicts["contains_all_keywords"]
    for section, keywords in contains_all_keywords_dict.items():
        match_ak = all(keyword in text for keyword in keywords)
        if match_ak:
            return True
    return False


def remove_hidden_readonly(file_path):
    try:
        # 取消只读和隐藏属性
        os.chmod(file_path, stat.S_IWRITE)
        subprocess.run(['attrib', '-h', file_path])  # 取消隐藏属性
        #print(f"已取消文件 {file_path} 的只读和隐藏属性。")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错：{e}")
        input("按 Enter 键退出...")
        
def get_file_permissions(file_path):
    try:
        # 获取文件控制权限
        permissions = os.stat(file_path).st_mode
        #print(f"文件 {file_path} 的控制权限：{permissions:o}")
    except Exception as e:
        print(f"获取文件 {file_path} 的控制权限时出错：{e}")
        input("按 Enter 键退出...")

def move_file(source_path, destination_path):
    remove_hidden_readonly(source_path)
    get_file_permissions(source_path)
    try:
        file_name = os.path.basename(source_path)
        new_file_name = generate_unique_file_name(destination_path, file_name)
        new_file_path = os.path.join(destination_path, new_file_name)
        shutil.move(source_path, new_file_path)
        print(f" {source_path} 文件已移动到 {new_file_path}。")
    except Exception as e:
        print("文件移动失败:", str(e))
        input("按 Enter 键退出...")

def generate_unique_file_name(destination_path, file_name):
    base_name, ext = os.path.splitext(file_name)
    count = 1
    new_file_name = f"{base_name}_{count}{ext}"
    while os.path.exists(os.path.join(destination_path, new_file_name)):
        count += 1
        new_file_name = f"{base_name}_{count}{ext}"
    return new_file_name

def move_folder(source_path, destination_path):
    remove_hidden_readonly(source_path)
    get_file_permissions(source_path)
    try:
        if os.path.exists(destination_path):
            # 生成一个新的目标文件夹名，以避免命名冲突
            new_folder_name = generate_unique_folder_name(source_path, destination_path)
            new_destination_path = os.path.join(destination_path, new_folder_name)
            shutil.move(source_path, new_destination_path)
            print(f" {source_path} 文件夹已剪切到 {new_destination_path}。")
        else:
            shutil.move(source_path, destination_path)
            print(f" {source_path} 文件夹已剪切到 delete 文件夹。")
    except Exception as e:
        print("文件夹移动失败:", str(e))
        input("按 Enter 键退出...")

def generate_unique_folder_name(source_path, destination_path):
    base_name = os.path.basename(source_path)
    count = 1
    new_folder_name = f"{base_name}_{count}"
    while os.path.exists(os.path.join(destination_path, new_folder_name)):
        count += 1
        new_folder_name = f"{base_name}_{count}"
    return new_folder_name


def process_folder(folder_path, delete_folder_path): # 处理文件夹（文件夹路径，储存文件夹路径）
    for root, dirs, files in os.walk(folder_path): # 递归处理目录下的所有文件夹和文件，获得根，文件夹们，文件们
        
        if os.path.samefile(root, delete_folder_path):
            dirs[:] = []  # 清空子文件夹列表，跳过delete文件夹内的内容
            print('skip')
            continue
        
        for file in files:
            file_path = os.path.join(root, file)#拼接出文件路径
            print(file_path)
            if full_keywords(file):
                print('match full keywords')
                move_file(file_path, delete_folder_path)
                
            elif all_keywords(file):
                print('match all keywords')
                move_file(file_path, delete_folder_path)
                
            elif file.lower().endswith('.txt'):#识别出文本文件
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if full_keywords(content):  # 先判断 full_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    elif all_keywords(content):  # 如果不满足 full_keywords() 再判断 all_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    else:
                        print(f" {file_path} 该.txt文件未满足适配条件") #不注释可能太多干扰项
            
            elif file.lower().endswith('.url'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if full_keywords(content):  # 先判断 full_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    elif all_keywords(content):  # 如果不满足 full_keywords() 再判断 all_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    else:
                        print(f" {file_path} 该.url文件未满足适配条件") #不注释可能太多干扰项
            else :
                print('unmatch')
        #print('该目录下全部txt或url文件，识别并转移完成')  



        for directory in dirs:
            dir_path = os.path.join(root, directory)#拼接出文件夹路径
            
            if full_keywords(dir_path):  # 先判断 full_keywords()
                move_folder(dir_path, delete_folder_path)
            elif all_keywords(dir_path):  # 如果不满足 full_keywords() 再判断 all_keywords()
                move_folder(dir_path, delete_folder_path)
            #else:
                #print(f"该文件夹 {dir_path} 未满足适配条件")  #已注释掉，不然很多目录都会被打印出来
        #print('该目录下全部文件夹，识别并转移完成')    
    
def ask_to_list_delete_contents(delete_folder_path):
    while True:
        user_input = input("是否需要列出 delete 文件夹下的所有文件和文件夹？(y/n): ").lower()
        if user_input == 'y':
            list_delete_contents(delete_folder_path)
            break
        elif user_input == 'n':
            break
        else:
            print("无效的输入，请输入 'y' 或 'n'。")

def list_delete_contents(delete_folder_path):
    #print(delete_folder_path)
    if os.path.exists(delete_folder_path) and os.path.isdir(delete_folder_path):
        print("delete 文件夹内容列表:")
        for item in os.listdir(delete_folder_path):
            item_path = os.path.join(delete_folder_path, item)
            item_type = "文件" if os.path.isfile(item_path) else "文件夹"
            print(f"{item_type}: {item}")
    else:
        print("delete 文件夹不存在或不是一个文件夹。")

def ask_to_delete_delete_folder(delete_folder_path):
    while True:
        user_input = input("是否需要删除 delete 文件夹及其中的所有内容？(y/n): ").lower()
        if user_input == 'y':
            delete_delete_folder(delete_folder_path)
            break
        elif user_input == 'n':
            break
        else:
            print("无效的输入，请输入 'y' 或 'n'。")

def delete_delete_folder(delete_folder_path): #删除过程遇到只读/隐藏文件/系统文件
    if os.path.exists(delete_folder_path) and os.path.isdir(delete_folder_path):
        try:
            shutil.rmtree(delete_folder_path)
            print("delete 文件夹及其中的所有内容已成功删除。")
        except Exception as e:
            print("删除 delete 文件夹失败:", str(e))
    else:
        print("delete 文件夹不存在或不是一个文件夹。")





if __name__ == "__main__":
    
    keyword_dicts = {    # 全局字典，存储从 .ini 文件中读取的关键字
    "full_keywords": {},
    "contains_all_keywords": {}
    }
    
    read_keywords_from_file()#加载配置文件
    
    print(keyword_dicts)

    if len(sys.argv) <= 1:
        input("请将文件夹拖拽到本程序上来清洗。按 Enter 键继续...")
    else:
        for arg in sys.argv[1:]: #逐个处理拖入的多个文件
            if os.path.exists(arg): #如果该文件存在
                if os.path.isdir(arg): #如果该文件是一个文件夹
                    delete_folder_path = os.path.join(arg, "delete") #设定该文件夹底下的delete文件夹
                    os.makedirs(delete_folder_path, exist_ok=True) #创建该文件夹底下的delete文件夹
                
                    process_folder(arg, delete_folder_path) #处理该文件夹（被处理文件夹路径，delete文件夹路径）
                
                    ask_to_list_delete_contents(delete_folder_path)
                    ask_to_delete_delete_folder(delete_folder_path)


                else: #如果不是文件夹，弹出警告
                    print(f"警告：{arg} 不是一个文件夹，将被忽略。")
                    input("按 Enter 键退出...")
            else: #如果拖入的文件不存在，弹出警告
                print(f"警告：{arg} 不存在，将被忽略。")
                input("按 Enter 键退出...")
        input("所有文件处理完成，按 Enter 键退出...")        
    
        