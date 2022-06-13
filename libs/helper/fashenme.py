import xml.etree.ElementTree as ET

fname = "data/fashenme/fashenme.xml"

def get_fashenme(fsm_code: int):
    """返回编号对应内容"""
    return fashenme[fsm_code]

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