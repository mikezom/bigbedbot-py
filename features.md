# 功能列表

## 管理员指令

### 开启/关闭功能

`{开启|关闭}<功能名>`

开启或者关闭功能，只有bot拥有者才能使用，具体功能名可以查询[功能名称](config/function_name.json)

### 群发公告

好像还没做

### 导出发什么

`导出发什么`

导出20字符以内的发什么词条来给群友玩你画我猜。

## 环境功能

环境功能，用于回应一些事件。

### 复读

群内发送消息时，bot有概率复读消息。

### 禁嘟

群内发送包含`嘟`的消息时出警，提醒群友本群禁嘟。

## 用户指令

### 播放音频

`播放 <单位持续时间(ms)>;<简谱>`

进行简谱到音频的转换。简谱的格式为：

- `1-7` : 对应`do, re, mi, fa, sol, la, ti`, `la = 440Hz`，只对`播放`有效。
- `A-G` : 同上，只对`9播放`有效。
- `b`   : 降半音，写在对应的音前。
- `#`   : 升半音，写在对应的音前。
- `` ` `` : 高八度，写在对应的音后。
- `.`   : 低八度，写在对应的音后。
- `-`   : 延长前一个音`1`单位。

例子
: ~~你不会真的以为我会写吧~~

### 测试1

`测试1`

看看自己权限多少。

### 发什么

`发什么 {编号|字符串}`

在大床发什么库中查询。

### 加发

`加发 {字符串}`

往发什么库里扔垃圾，暂不支持图片。

### 发什么十连

`发什么十连`

gacha要素

### 基金

`基金 <code>`

查看基金当日涨跌，api来自[doctorxiong](api.doctorxiong.club)

### 查询流量

`{查询流量|流量查询}`

看看梯子还有多少流量，由于某机场经常换ip、登录验证方式所以不总是能用。

### Solidot

`solidot [n]`

看看新闻，来源是[solidot](www.solidot.org)。加数字`1-5`可以看新闻具体内容以及链接。

### 什么值得买

`smzdm [物品名]`

在什么值得买上查询折扣消息，不加物品名则为随机推送折扣。

### 随机塔菲

`随机塔菲`

随机播放sample来自塔菲按钮，大量披风内容发生。

### 国旗

`/国旗`

给你的头像加一面很酷的国旗吧大概。