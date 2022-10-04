import matplotlib.pyplot as plt
import IPython.display as ipd

import os
import json
import math
import torch
import pypinyin
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

import commons
import utils
from data_utils import TextAudioLoader, TextAudioCollate, TextAudioSpeakerLoader, TextAudioSpeakerCollate
from models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence

from scipy.io.wavfile import write

import time
from scipy.io.wavfile import write

def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm

hps_mt = utils.get_hparams_from_file("test/vits/configs/genshin.json")

npcList = ['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶',
           '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉', '优菈',
           '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗',
           '甘雨', '七七', '刻晴', '神里绫华', '戴因斯雷布', '雷泽',
           '神里绫人', '罗莎莉亚', '阿贝多', '八重神子', '宵宫',
           '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎',
           '散兵', '女士', '达达利亚', '莫娜', '班尼特', '申鹤',
           '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云',
           '菲谢尔', '诺艾尔', '迪奥娜', '鹿野院平藏']

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

net_g_mt = SynthesizerTrn(
    len(symbols),
    hps_mt.data.filter_length // 2 + 1,
    hps_mt.train.segment_size // hps_mt.data.hop_length,
    n_speakers=hps_mt.data.n_speakers,
    **hps_mt.model).to(device)
_ = net_g_mt.eval()

_ = utils.load_checkpoint("test/vits/G_809000.pth", net_g_mt, None)

s = time.time()
speaker = '派蒙'
t_mt='''
蒙涅至冥阿耨俱諸槃皤有夜奢菩缽耶冥摩世所密奢即。
'''
stn_tst_mt = get_text(t_mt.replace("\n", ""), hps_mt)
print(stn_tst_mt)

with torch.no_grad():
    x_tst_mt = stn_tst_mt.to(device).unsqueeze(0)
    x_tst_mt_lengths = torch.LongTensor([stn_tst_mt.size(0)]).to(device)
    sid_mt = torch.LongTensor([npcList.index(speaker)]).to(device)
    audio_mt = net_g_mt.infer(x_tst_mt, x_tst_mt_lengths, sid=sid_mt, noise_scale=.667, noise_scale_w=.8, length_scale=1.2)[0][0,0].data.cpu().float().numpy()
print(time.time() - s)
write('paimon_test.wav', hps_mt.data.sampling_rate, audio_mt)