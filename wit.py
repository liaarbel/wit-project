# Upload 177
import datetime
from distutils.dir_util import copy_tree
import os
import random
import shutil
from shutil import copyfile
import sys

from dateutil.tz import tzlocal
from graphviz import Digraph


chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f']


def create_folders(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def init():
    newpath1 = os.path.join(os.getcwd(), ".wit")
    newpath2 = os.path.join(newpath1, "images")
    newpath3 = os.path.join(newpath1, "staging_area")
    path_list = (newpath1, newpath2, newpath3)
    for path in path_list:
        create_folders(path)
    new_txt = os.path.join(os.getcwd(), ".wit", "activated.txt")
    with open(new_txt, 'w') as master:
        master.write("master")
    return "Check .wit"


def add(path):
    folders = path.split("\\")
    area = os.path.join(os.getcwd(), ".wit", "staging_area")
    my_folders = area.split("\\")
    for i, folder in enumerate(folders[:-1]):
        if folder != my_folders[i]:
            area = os.path.join(area, folder)
            os.makedirs(area, exist_ok=True)
    if os.path.isdir(path):
        folder = folders[-1]
        area = os.path.join(area, folder)
        os.makedirs(area, exist_ok=True)
        fromDirectory = path
        toDirectory = area
        copy_tree(fromDirectory, toDirectory)
    elif os.path.isfile(path):
        name = folders[-1]
        src = path
        dst = os.path.join(area, name)
        copyfile(src, dst)
    return "Check .wit"


def search_head():
    if not os.path.exists(r".wit\references.txt"):
        with open(r".wit\references.txt", 'a') as re:
            re.write('')
    with open(r".wit\references.txt", 'r') as re:
        data = re.read()
        info_id = data.split("\n")
        if len(info_id) > 1:
            ids = []
            for line in info_id:
                lst = line.split("=")
                if lst[0] == "HEAD":
                    ids.append(lst[-1])
            return ids[-1]
        return None


def commit(message, special_parent=None):
    path1 = os.path.join(os.getcwd(), ".wit", "images")
    area = os.path.join(os.getcwd(), ".wit", "staging_area")
    legal = False
    parent = search_head()
    while not legal:
        chars_folder = random.choices(chars, k=40)
        chars_folder = ''.join(chars_folder)
        path2 = os.path.join(path1, chars_folder)
        legal = create_folders(path2)
    path3 = path2 + ".txt"
    last_name = get_name()
    name_id = get_name_id(last_name)
    last_head = search_head()
    with open(path3, 'w') as commit_id_txt:
        date = datetime.datetime.now(tzlocal()).strftime("%a %b %d %H:%M:%S %Y %z")
        if special_parent is not None:
            parent = f"{parent},{special_parent}"
        commit_id_txt.write(f"Parent={parent}\nDate={date}\nMessage={message}\n")
    fromDirectory = os.path.join(area)
    toDirectory = path2
    copy_tree(fromDirectory, toDirectory)
    txt = os.path.join(os.getcwd(), ".wit", "activated.txt")
    with open(txt, 'r') as activated:
        activated = activated.read()
    with open(r".wit\references.txt", 'a') as re:
        re.write(f"HEAD={chars_folder}\n{activated}={chars_folder}\n")
    if name_id == last_head:
        branch(last_name)


def comparing_folders(path1, path2):
    directories1 = list(os.listdir(path1))
    directories2 = list(os.listdir(path2))
    result = []
    not_exist = []
    for d in directories2:
        if d not in directories1:
            not_exist.append(d)
        else:
            path3 = os.path.join(path2, d)
            path4 = os.path.join(path1, d)
            if os.stat(path3).st_ctime > os.stat(path4).st_ctime:
                result.append(d)
    return result, not_exist


def status():
    head = search_head()
    print(f"commit id: {head}")
    path1 = os.path.join(os.getcwd(), ".wit", "images", head)
    area = os.path.join(os.getcwd(), ".wit", "staging_area")
    comp1, _ = comparing_folders(path1, area)
    print("Changes to be committed:")
    for d in comp1:
        print(d)
    print("Changes not staged for commit:")
    path2 = os.getcwd()
    comp2, not_exist = comparing_folders(area, path2)
    for d in comp2:
        print(d)
    print("Untracked files:")
    for i in not_exist:
        print(i)


def checkout(commit_id):
    if len(commit_id) != 40:
        name = commit_id
        commit_id = get_name_id(commit_id)
    else:
        name = get_name()
    with open(r".wit\references.txt", 'a') as re:
        re.write(f"HEAD={commit_id}\n")
    original = os.getcwd()
    new_txt = os.path.join(original, ".wit", "activated.txt")
    dirs1 = list(os.listdir(original))
    commit_path = os.path.join(original, ".wit", "images", commit_id)
    dirs2 = list(os.listdir(commit_path))
    comp, not_exist = comparing_folders(commit_path, original)
    if len(comp) == 0:
        for d in dirs1:
            path_d = os.path.join(original, d)
            if d in dirs2 and os.path.isdir(path_d):
                shutil.rmtree(path_d)
            elif d in dirs2 and os.path.isfile(path_d):
                os.remove(path_d)
        copy_tree(commit_path, original)
    with open(new_txt, 'w') as activated:
        activated.write(f"{name}")
        

def get_parent(commit_id):
    if type(commit_id) is str:
        path = os.path.join(os.getcwd(), ".wit", "images", commit_id + ".txt")
        with open(path, 'r') as data:
            data = data.read()
            info_id = data.split("\n")
            for i, line in enumerate(info_id):
                info_id[i] = line.split("=")
            result = info_id[0][-1]
            if len(result) > 40:
                result = result.split(',')
                return result
            return result
    return None


def graph():
    head = search_head()
    g = Digraph('G', filename='hello.gv')
    if head == 'None':
        return None
    lst = [head]
    for i in lst:
        if i != 'None':
            parent = get_parent(i)
            if type(parent) is list:
                for par in parent:
                    if par != 'None':
                        g.edge(i, par)
                    if par not in lst:
                        lst.append(par)
            else:
                if parent != 'None':
                    g.edge(parent, i)
                if parent not in lst:
                    lst.append(parent)
    g.view()


def get_name():
    with open(r".wit\references.txt", 'r') as re:
        data = re.read()
        info_id = data.split("\n")
        names = []
        for line in info_id:
            lst = line.split("=")
            if lst[0] != "HEAD":
                names.append(lst[0])
        return names[-1]


def get_name_id(name):
    with open(r".wit\references.txt", 'r') as re:
        re = re.read()
        lines = re.split("\n")
        lst_ids = []
        for line in lines:
            j = line.split('=')
            if j[0] == name:
                lst_ids.append(j[-1])
        return lst_ids[-1]


def branch(name):
    head = search_head()
    references = os.path.join(os.getcwd(), ".wit", "references.txt")
    with open(references, 'a') as add_name:
        add_name.write(f"{name}={head}\n")


def parents(any_id):
    parents = [any_id]
    for parent in parents:
        new_parent = get_parent(parent)
        if new_parent != 'None':
            if type(new_parent) is list:
                for np in new_parent:
                    parents.append(np)
            else:
                parents.append(new_parent)
    parents.reverse()
    return parents


def merge(branch_name):
    name_id = get_name_id(branch_name)
    head = search_head()
    parents1 = parents(name_id)
    parents2 = parents(head)
    common_list = set(parents1) & set(parents2)
    max_cml = 0
    for cml in common_list:
        path = os.path.join(os.getcwd(), ".wit", "images", cml)
        if os.stat(path).st_ctime > max_cml:
            max_cml = os.stat(path).st_ctime
            max_path = path
    path1 = os.path.join(os.getcwd(), ".wit", "images", name_id)
    path3 = os.path.join(os.getcwd(), ".wit", "images", max_path)
    comp, _ = comparing_folders(path1, path3)
    for path in comp:
        add(path)
    commit("After merge", name_id)


# try:
#     arg = sys.argv[1]
# except IndexError:
#     print("You didn\'t call to any functions.")
# else:
#     if arg == "init":
#         print(init())
#     elif arg == "add":
#         print(add(sys.argv[2]))
#     elif arg == "commit":
#         commit(sys.argv[2])
#     elif arg == "status":
#         status()
#     elif arg == "checkout":
#         checkout(sys.argv[-1])
#     elif arg == "graph":
#         graph()
#     elif arg == "branch":
#         branch(sys.argv[-1])
#     elif arg == "merge":
#         merge(sys.argv[-1])
#     else:
#         print("I don\'t recognize this function")
graph()