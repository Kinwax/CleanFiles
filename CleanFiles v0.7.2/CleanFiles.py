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
        line = line.strip()  # ȥ����β�հ��ַ�
        if not line:
            continue  # ��������
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]  # ��ȡ��������
            keyword_dicts[current_section] = []  # ����һ���յĹؼ����б�
        elif current_section is not None:
            keyword_dicts[current_section].append(line)  # ���ؼ�����ӵ���ǰ���ֵ��б���

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
        # ȡ��ֻ������������
        os.chmod(file_path, stat.S_IWRITE)
        subprocess.run(['attrib', '-h', file_path])  # ȡ����������
        #print(f"��ȡ���ļ� {file_path} ��ֻ�����������ԡ�")
    except Exception as e:
        print(f"�����ļ� {file_path} ʱ����{e}")
        input("�� Enter ���˳�...")
        
def get_file_permissions(file_path):
    try:
        # ��ȡ�ļ�����Ȩ��
        permissions = os.stat(file_path).st_mode
        #print(f"�ļ� {file_path} �Ŀ���Ȩ�ޣ�{permissions:o}")
    except Exception as e:
        print(f"��ȡ�ļ� {file_path} �Ŀ���Ȩ��ʱ����{e}")
        input("�� Enter ���˳�...")

def move_file(source_path, destination_path):
    remove_hidden_readonly(source_path)
    get_file_permissions(source_path)
    try:
        file_name = os.path.basename(source_path)
        new_file_name = generate_unique_file_name(destination_path, file_name)
        new_file_path = os.path.join(destination_path, new_file_name)
        shutil.move(source_path, new_file_path)
        print(f" {source_path} �ļ����ƶ��� {new_file_path}��")
    except Exception as e:
        print("�ļ��ƶ�ʧ��:", str(e))
        input("�� Enter ���˳�...")

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
            # ����һ���µ�Ŀ���ļ��������Ա���������ͻ
            new_folder_name = generate_unique_folder_name(source_path, destination_path)
            new_destination_path = os.path.join(destination_path, new_folder_name)
            shutil.move(source_path, new_destination_path)
            print(f" {source_path} �ļ����Ѽ��е� {new_destination_path}��")
        else:
            shutil.move(source_path, destination_path)
            print(f" {source_path} �ļ����Ѽ��е� delete �ļ��С�")
    except Exception as e:
        print("�ļ����ƶ�ʧ��:", str(e))
        input("�� Enter ���˳�...")

def generate_unique_folder_name(source_path, destination_path):
    base_name = os.path.basename(source_path)
    count = 1
    new_folder_name = f"{base_name}_{count}"
    while os.path.exists(os.path.join(destination_path, new_folder_name)):
        count += 1
        new_folder_name = f"{base_name}_{count}"
    return new_folder_name


def process_folder(folder_path, delete_folder_path): # �����ļ��У��ļ���·���������ļ���·����
    for root, dirs, files in os.walk(folder_path): # �ݹ鴦��Ŀ¼�µ������ļ��к��ļ�����ø����ļ����ǣ��ļ���
        
        if os.path.samefile(root, delete_folder_path):
            dirs[:] = []  # ������ļ����б�����delete�ļ����ڵ�����
            print('skip')
            continue
        
        for file in files:
            file_path = os.path.join(root, file)#ƴ�ӳ��ļ�·��
            print(file_path)
            if full_keywords(file):
                print('match full keywords')
                move_file(file_path, delete_folder_path)
                
            elif all_keywords(file):
                print('match all keywords')
                move_file(file_path, delete_folder_path)
                
            elif file.lower().endswith('.txt'):#ʶ����ı��ļ�
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if full_keywords(content):  # ���ж� full_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    elif all_keywords(content):  # ��������� full_keywords() ���ж� all_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    else:
                        print(f" {file_path} ��.txt�ļ�δ������������") #��ע�Ϳ���̫�������
            
            elif file.lower().endswith('.url'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if full_keywords(content):  # ���ж� full_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    elif all_keywords(content):  # ��������� full_keywords() ���ж� all_keywords()
                        f.close()
                        move_file(file_path, delete_folder_path)
                    else:
                        print(f" {file_path} ��.url�ļ�δ������������") #��ע�Ϳ���̫�������
            else :
                print('unmatch')
        #print('��Ŀ¼��ȫ��txt��url�ļ���ʶ��ת�����')  



        for directory in dirs:
            dir_path = os.path.join(root, directory)#ƴ�ӳ��ļ���·��
            
            if full_keywords(dir_path):  # ���ж� full_keywords()
                move_folder(dir_path, delete_folder_path)
            elif all_keywords(dir_path):  # ��������� full_keywords() ���ж� all_keywords()
                move_folder(dir_path, delete_folder_path)
            #else:
                #print(f"���ļ��� {dir_path} δ������������")  #��ע�͵�����Ȼ�ܶ�Ŀ¼���ᱻ��ӡ����
        #print('��Ŀ¼��ȫ���ļ��У�ʶ��ת�����')    
    
def ask_to_list_delete_contents(delete_folder_path):
    while True:
        user_input = input("�Ƿ���Ҫ�г� delete �ļ����µ������ļ����ļ��У�(y/n): ").lower()
        if user_input == 'y':
            list_delete_contents(delete_folder_path)
            break
        elif user_input == 'n':
            break
        else:
            print("��Ч�����룬������ 'y' �� 'n'��")

def list_delete_contents(delete_folder_path):
    #print(delete_folder_path)
    if os.path.exists(delete_folder_path) and os.path.isdir(delete_folder_path):
        print("delete �ļ��������б�:")
        for item in os.listdir(delete_folder_path):
            item_path = os.path.join(delete_folder_path, item)
            item_type = "�ļ�" if os.path.isfile(item_path) else "�ļ���"
            print(f"{item_type}: {item}")
    else:
        print("delete �ļ��в����ڻ���һ���ļ��С�")

def ask_to_delete_delete_folder(delete_folder_path):
    while True:
        user_input = input("�Ƿ���Ҫɾ�� delete �ļ��м����е��������ݣ�(y/n): ").lower()
        if user_input == 'y':
            delete_delete_folder(delete_folder_path)
            break
        elif user_input == 'n':
            break
        else:
            print("��Ч�����룬������ 'y' �� 'n'��")

def delete_delete_folder(delete_folder_path): #ɾ����������ֻ��/�����ļ�/ϵͳ�ļ�
    if os.path.exists(delete_folder_path) and os.path.isdir(delete_folder_path):
        try:
            shutil.rmtree(delete_folder_path)
            print("delete �ļ��м����е����������ѳɹ�ɾ����")
        except Exception as e:
            print("ɾ�� delete �ļ���ʧ��:", str(e))
    else:
        print("delete �ļ��в����ڻ���һ���ļ��С�")





if __name__ == "__main__":
    
    keyword_dicts = {    # ȫ���ֵ䣬�洢�� .ini �ļ��ж�ȡ�Ĺؼ���
    "full_keywords": {},
    "contains_all_keywords": {}
    }
    
    read_keywords_from_file()#���������ļ�
    
    print(keyword_dicts)

    if len(sys.argv) <= 1:
        input("�뽫�ļ�����ק��������������ϴ���� Enter ������...")
    else:
        for arg in sys.argv[1:]: #�����������Ķ���ļ�
            if os.path.exists(arg): #������ļ�����
                if os.path.isdir(arg): #������ļ���һ���ļ���
                    delete_folder_path = os.path.join(arg, "delete") #�趨���ļ��е��µ�delete�ļ���
                    os.makedirs(delete_folder_path, exist_ok=True) #�������ļ��е��µ�delete�ļ���
                
                    process_folder(arg, delete_folder_path) #������ļ��У��������ļ���·����delete�ļ���·����
                
                    ask_to_list_delete_contents(delete_folder_path)
                    ask_to_delete_delete_folder(delete_folder_path)


                else: #��������ļ��У���������
                    print(f"���棺{arg} ����һ���ļ��У��������ԡ�")
                    input("�� Enter ���˳�...")
            else: #���������ļ������ڣ���������
                print(f"���棺{arg} �����ڣ��������ԡ�")
                input("�� Enter ���˳�...")
        input("�����ļ�������ɣ��� Enter ���˳�...")        
    
        