import xml.etree.ElementTree as ET
from loguru import logger
import random

fname = "data/fashenme/fashenme.xml"

def is_surrunded(s: str):
    if s[0] == "'" and s[-1] == "'":
        return True
    elif s[0] == '"' and s[-1] == '"':
        return True
    else:
        return False

def get_fashenme(fsm_code: int):
    """返回编号对应内容"""
    res_string = f"{fsm_code}. {fashenme[fsm_code]}"
    return res_string

def find_fashenme(content: str):
    """在发什么里找内容"""
    content = content.strip()
    if is_surrunded(content):
        content = content[1:-1]
    res = []
    for i,x in enumerate(fashenme):
        if content in x:
            res.append(f"{i}. {x}")
    if len(res) == 0:
        return "么得么得么，么么得"
    else:
        res_string = random.choice(res)
        return res_string

def find_fashenme_how_many(prompt: str):
    prompt = prompt.strip()
    res = []
    for i,x in enumerate(fashenme):
        if prompt in x:
            res.append(f"{i}. {x}")
    return len(res)

def get_fashenme_size():
    """返回列表大小"""
    return len(fashenme)

def read_fashenme():
    """读取文件"""
    global fashenme
    fashenme = ['']
    tree = ET.parse(fname)
    root = tree.getroot()
    for child in root:
        fashenme.append(child.text)

def export_fashenme(filename: str):
    file_path = f"data/fashenme/{filename}.txt"
    try:
        with open(file_path, 'w') as fp:
            count = 0
            for l in fashenme:
                if len(l) <= 20:
                    fp.write(f"{l}\n")
                    count += 1
        return count
    except:
        return 0

def add_fashenme(str):
    """加发"""
    logger.info(f"adding fashenme: {str}")
    fashenme.append(str)

    tree = ET.parse(fname)
    root = tree.getroot()

    new_element = ET.Element('item')
    new_element.text = str
    root.append(new_element)

    tree.write(fname)

def has_duplicate(str):
    """列表内是否有重复"""
    tree = ET.parse(fname)
    root = tree.getroot()
    for child in root:
        if child.text == str:
            return True
    return False