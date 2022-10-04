# bigbedbot-py

A rework of a personal bot

基于 [Graia-Ariadne](../../../../GraiaProject/Ariadne) 搭建。

## Usage

### Configuration

根据自身情况以及 `config_example.json` 和 `group_permission_example.json` 创建对应的文件

### Launch

1. 使用 `python 3.10.5` 安装对应的库 (由于poetry总是有莫名其妙的包冲突，故弃用)
2. 打开 `mcl` （版本需高于2.0）
3. `python3 main.py`

## 功能

详见 [功能列表](features.md)，这里只列出几个主要功能：

### 播放音频

使用 `[9]播放 <单位持续时间(ms)>;<简谱>` 进行简谱到音频的转换，是否使用`9播放`影响接受的简谱格式。详见功能列表内的[简谱格式](features.md#播放音频)

### 什么值得买

使用 `smzdm [物品名]` 在什么值得买上查询折扣消息，不加物品名则为随机推送折扣。

### 发什么

使用 `发什么 {编号|字符串}` 在大床发什么库中查询，`加发` 添加词条，`发什么十连` 返回一次十连查询。

## 鸣谢

- [BBot-Graia](../../../../djkcyl/BBot-Graia) 学习文件结构以及permission模块
- [VITS](../../../../jaywalnut310/vits/) 使用基于VITS的原神TTS
