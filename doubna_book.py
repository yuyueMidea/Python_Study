Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:06:47) [MSC v.1914 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> from bs4 import BeautifulSoup
>>> import requests
>>> from openpyxl import Workbook
>>> excel_name = "书籍.xlsx"
>>> wb = Workbook()
>>> ws1 = wb.active
>>> ws1.title='书籍'
>>> def get_html(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    html = requests.get(url, headers=header).content
    return html

>>> def get_con(html):
    soup = BeautifulSoup(html,'html.parser')
    book_list = soup.find('div', attrs={'class': 'article'})
    page = soup.find('div', attrs={'class': 'paginator'})
    next_page = page.find('span', attrs={'class': 'next'}).find('a')
    name = []
    for i in book_list.find_all('table'):
        book_name = i.find('div', attrs={'class': 'pl2'})
        m = list(book_name.find('a').stripped_strings)
        if len(m)>1:
            x = m[0]+m[1]
        else:
            x = m[0]
        #print(x)
        name.append(x)
    if next_page:
        return name, next_page.get('href')
    else:
        return name, None

>>> def main():
    url = 'https://book.douban.com/top250'
    name_list=[]
    while url:
        html = get_html(url)
        name, url = get_con(html)
        name_list = name_list + name
    for i in name_list:
        location = 'A%s'%(name_list.index(i)+1)
        print(i)
        print(location)
        ws1[location]=i
    wb.save(filename=excel_name)

    
>>> if __name__ == '__main__':
    main()

    
追风筝的人
A1
解忧杂货店
A2
小王子
A3
白夜行
A4
围城
A5
三体: “地球往事”三部曲之一
A6
挪威的森林
A7
嫌疑人X的献身
A8
活着
A9
红楼梦
A10
百年孤独
A11
不能承受的生命之轻
A12
看见
A13
达·芬奇密码
A14
平凡的世界（全三部）
A15
三体Ⅱ: 黑暗森林
A16
三体Ⅲ: 死神永生
A17
简爱（英文全本）
A18
哈利·波特与魔法石
A19
天才在左 疯子在右: 国内第一本精神病人访谈手记
A20
送你一颗子弹
A21
傲慢与偏见
A22
我们仨
A23
飘
A24
倾城之恋
A25
明朝那些事儿（壹）: 洪武大帝
A26
目送
A27
月亮和六便士
A28
情人
A29
恶意
A30
哈利·波特与阿兹卡班的囚徒
A31
霍乱时期的爱情
A32
狼图腾
A33
1Q84 BOOK 1: 4月～6月
A34
哈利·波特与火焰杯
A35
边城
A36
哈利·波特与密室
A37
穆斯林的葬礼
A38
莲花
A39
许三观卖血记
A40
撒哈拉的故事
A41
万历十五年
A42
向左走·向右走
A43
哈利·波特与混血王子
A44
盗墓笔记: 七星鲁王宫
A45
黄金时代: 时代三部曲
A46
苏菲的世界
A47
窗边的小豆豆
A48
天龙八部
A49
三国演义（全二册）
A50
哈利·波特与凤凰社
A51
悟空传: 修订版
A52
牧羊少年奇幻之旅
A53
海边的卡夫卡
A54
灿烂千阳
A55
呼啸山庄
A56
兄弟（上）
A57
亲爱的安德烈
A58
少有人走的路: 心智成熟的旅程
A59
老人与海
A60
基督山伯爵
A61
民主的细节: 美国当代政治观察随笔
A62
笑傲江湖（全四册）
A63
人类简史: 从动物到上帝
A64
1984
A65
福尔摩斯探案全集（上中下）
A66
无声告白
A67
遇见未知的自己
A68
人间失格
A69
情书
A70
茶花女
A71
神雕侠侣
A72
一个陌生女人的来信
A73
白鹿原
A74
沉默的大多数: 王小波杂文随笔全编
A75
当我谈跑步时我谈些什么
A76
这些人，那些事
A77
东方快车谋杀案
A78
肖申克的救赎
A79
这些都是你给我的爱
A80
鲁滨逊漂流记
A81
局外人
A82
巴黎圣母院
A83
羊脂球
A84
喜宝
A85
陪安东尼度过漫长岁月
A86
呐喊
A87
红玫瑰与白玫瑰
A88
巨人的陨落: 世纪三部曲
A89
无人生还
A90
爱你就像爱生命
A91
华胥引（全二册）
A92
了不起的盖茨比
A93
鬼吹灯之精绝古城: 之精绝古城
A94
乌合之众: 大众心理研究
A95
安徒生童话故事集
A96
动物农场
A97
半生缘
A98
地下铁
A99
射雕英雄传（全四册）
A100
骆驼祥子
A101
月亮忘記了
A102
此间的少年
A103
如何阅读一本书
A104
孤独六讲
A105
一個人住第5年
A106
步步惊心
A107
常识
A108
时间旅行者的妻子
A109
寻路中国: 从乡村到工厂的自驾之旅
A110
一个人的朝圣
A111
阿Q正传
A112
荆棘鸟
A113
哭泣的骆驼
A114
刀锋
A115
孩子你慢慢来
A116
一只特立独行的猪
A117
失恋33天: 小说，或是指南
A118
你好，旧时光（上 下）
A119
格林童话全集
A120
尘埃落定
A121
麦琪的礼物: 欧·亨利短篇小说经典
A122
梦里花落知多少
A123
那些回不去的年少时光
A124
金锁记
A125
历史深处的忧虑: 近距离看美国之一
A126
海贼王: ONE PIECE
A127
鹿鼎记（全五册）
A128
大地之灯
A129
悲惨世界（上中下）
A130
史蒂夫·乔布斯传
A131
城南旧事: 纪念普及版
A132
球状闪电
A133
东霓
A134
菊与刀: 日本文化的类型
A135
长恨歌
A136
我不喜欢这世界，我只喜欢你
A137
看不见的城市
A138
你一定爱读的极简欧洲史: 为什么欧洲对现代文明的影响这么深
A139
香水: 一个谋杀犯的故事
A140
橙: 陪安东尼度过漫长岁月 Ⅱ
A141
一九八四·动物农场
A142
飞鸟集
A143
房思琪的初恋乐园
A144
往事并不如烟
A145
匆匆那年（上下）
A146
查令十字街84号
A147
把时间当作朋友: 运用心智获得解放
A148
江城
A149
世界尽头与冷酷仙境
A150
伊豆的舞女
A151
影响力
A152
冰与火之歌（卷一）: 权力的游戏
A153
倚天屠龙记(共四册)
A154
中国历代政治得失
A155
富爸爸，穷爸爸
A156
七夜雪
A157
蔷薇岛屿
A158
那些年，我们一起追的女孩
A159
ZOO
A160
阿狸·梦之城堡
A161
红与黑
A162
时间简史: 插图本
A163
天使与魔鬼
A164
朝花夕拾
A165
最初的爱情 最后的仪式
A166
水浒传（全二册）
A167
佛祖在一号线
A168
陆犯焉识
A169
国境以南 太阳以西
A170
生活在别处
A171
西游记（全二册）
A172
雷雨
A173
最好的我们
A174
瓦尔登湖
A175
杀死一只知更鸟
A176
心是孤独的猎手
A177
京华烟云
A178
设计中的设计
A179
自控力: 斯坦福大学最受欢迎心理学课程
A180
我执
A181
偷书贼
A182
夏洛的网
A183
变形记: 卡夫卡小说
A184
狂人日记
A185
没有色彩的多崎作和他的巡礼之年
A186
激荡三十年（上）: 中国企业1978-2008
A187
海底两万里
A188
文学回忆录（全2册）: 1989—1994
A189
人性的弱点全集
A190
九州·缥缈录
A191
一句顶一万句
A192
尼罗河上的惨案
A193
呼兰河传: 1947年版本・原版珍藏
A194
你今天真好看
A195
我的精神家园: 王小波杂文自选集
A196
人生
A197
我与地坛: 史铁生代表作
A198
占星术杀人魔法
A199
浪潮之巅
A200
舞！舞！舞！
A201
野火集: 二十年纪念版
A202
妻妾成群
A203
浮生六记
A204
高效能人士的七个习惯（精华版）
A205
海子的诗
A206
项链: 莫泊桑中短篇小说选
A207
教父
A208
娱乐至死
A209
观念的水位
A210
带一本书去巴黎
A211
寻羊冒险记
A212
中国大历史
A213
罗杰疑案
A214
子不语1
A215
巨流河
A216
动物凶猛
A217
父与子全集
A218
小姨多鹤
A219
第一炉香
A220
退步集
A221
爱的艺术
A222
斯通纳
A223
芳华
A224
云中歌1
A225
人间词话
A226
来不及说我爱你
A227
夹边沟记事
A228
未来简史
A229
可爱的洪水猛兽
A230
一千零一夜
A231
相约星期二
A232
白银时代: 时代三部曲
A233
台北人
A234
告白
A235
万水千山走遍
A236
哈姆莱特
A237
罗生门
A238
后宫·甄嬛传Ⅰ
A239
面纱
A240
琅琊榜
A241
阿麦从军：全新修订版
A242
雨季不再来
A243
朗读者
A244
星空
A245
雾都孤儿
A246
枪炮、病菌与钢铁: 人类社会的命运
A247
红拂夜奔
A248
深夜食堂 01
A249
万物有灵且美
A250


>>> 