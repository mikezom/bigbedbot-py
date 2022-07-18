import xml.etree.ElementTree as ET
import random

fname = "data/fashenme/fashenme.xml"

def get_fashenme(fsm_code: int):
    """返回编号对应内容"""
    res_string = f"{fsm_code}. {fashenme[fsm_code]}"
    return res_string

def find_fashenme(content: str):
    """在发什么里找内容"""
    content = content[:4]
    res = []
    for i,x in enumerate(fashenme):
        if content in x:
            res.append(f"{i}. {x}")
    if len(res) == 0:
        return "么得么得么，么么得"
    else:
        res_string = random.choice(res)
        return res_string

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

def add_fashenme(str):
    """加发"""
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