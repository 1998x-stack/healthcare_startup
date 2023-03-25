# healthcare_startup

## Url List

1. 医学百科:http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5
*  全国医院列表： http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8
*  药品百科：http://www.a-hospital.com/w/%E8%8D%AF%E5%93%81

2. news: 健康界 https://www.cn-healthcare.com/
* 医院排行榜 http://rank.cn-healthcare.com/fudan/national-general/year/2020

3. 益药：http://www.xinyao.com.cn/
4. 健康到家：药品 https://www.jianke.com/
5. 药品网：http://y.wksc.com/
6. 疾病大全： http://y.wksc.com/jbdq.html  http://y.wksc.com/jibing/
7. 疾病百科：https://www.youlai.cn/dise/
8. https://www.120ask.com/  （疾病库非常全，而且还有医生大全）
9. 药源网：https://www.yaopinnet.com/


## Code
1. jibinginfo.ipynb
* target: 获取每个科目下的疾病类型以及具体信息
* from: http://www.xywy.com/
* TODO: multiprocessing

2. ques_ans.ipynb and ques_ans.py
* target: 获取医生和患者的对话信息
* from: http://www.xywy.com/
* 后者采用多线程

3. hospital_info.ipynb and hospital_info.py
* target: 获取北京市所有医院的信息，医院里面所有医生的信息
* from: http://www.xywy.com/
* 后者采用多线程，暂时出现 TypeError: cannot pickle '_thread.lock' object

4. medician.ipynb and medician.py
* target: 获取各种药品的信息
* from: http://y.wksc.com/
* 后者采用多线程

## Data
### Input data
1. ./yiyuandiqu-beijing.csv (which euqal to ./beijing_hospital.json)
* it is get from http://z.xywy.com/yiyuandiqu-beijing.htm use instant scrap extension
* it gets all hospitals from beijing

2. ./dingxiang_hospital.csv (useless)
* it is got from 用药助手, but only 20 pages


## Output data
1. ./data/hospital
* 北京医院的信息，各个科室的信息，科室里面各个医生的信息

2. ./data/medician
* 各个药品的信息

3. ./jibinginfo.json (which equals to ./jibinginfo_copy.json)
* 关于疾病介绍的信息

4. ./ques_ans.json (which euqals to ./ques_ans_copy.json)
* 医生和患者问答的信息，还包括医生的简单介绍

# Target
* （可以让用户上传基础信息）建立患者信息档案，平台思维，而不是工具思维，建立护城河。 P0
* 体检报告解读 P0
1. 根据自己的描述（语音、文字），找到适合自己病情的医院、科室、医生。 P1
2. 和ChatGPT对话，回答患者的问题，比如给出问题分析，指导建议，注意事项，后续步骤。P2
3. 答案的可靠度---如何评价。 P3
4. 根据患者的问题，产生相应的问题供患者回答，优化相似的问题。 P2
5. 产生相应体检报告——提高患者和医生的交流效率。 P3
6. 后续上传X片等补充信息，帮患者提取最关心的信息。 P3

# 成本

## 最小可行单元的成本

### 最小可行单元： 
1. 患者信息档案（2C）==>当作和医院谈判的筹码！可以建立一个专家库，把用户的档案给医生，大大提升医生的效率（2B）
2. 据自己的描述（语音、文字），找到适合自己病情的医院、科室、医生
3. 和ChatGPT对话，回答患者的问题，比如给出问题分析，指导建议，注意事项，后续步骤
4. 小程序

### 假设：流量10000 questions/天

1. 服务器成本：200/天
2. ChatGPT接口：$0.002/1000 tokens * 4 * 400 * 10000 = 224 ¥
3. 营销
* 地推：专门针对医院 100元/人天 & 病友群
* 抖音：目前抖音信息流广告的一个CPC的价格为0.2元，即用户点击了广告主投放的广告链接，抖音广告系统会收取广告主0.2元的广告费。 优势： 投资转化率高：广告被点击才付费，而点击广告的用户几乎都是潜在用户，因为感兴趣才点击。
4. 时间成本


# 难点
1. 调用企业接口（卡的注册问题）
2. 服务器翻墙
3. company注册

## 额外的功能
1. Calendar 格式的输出
让ChatGPT生成日程安排，苹果 Calendar格式，可以直接部署到Calendar
```raw
好的，我可以帮你生成一个日程安排，以下是一个示例：

BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Apple Inc.//Mac OS X 10.15.4//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:20230325T110000Z-12345@example.com
DTSTAMP:20230325T110000Z
DTSTART:20230326T090000Z
DTEND:20230326T110000Z
SUMMARY:早餐会议
LOCATION:会议室A
DESCRIPTION:与同事讨论新项目
END:VEVENT
BEGIN:VEVENT
UID:20230325T120000Z-12346@example.com
DTSTAMP:20230325T120000Z
DTSTART:20230326T130000Z
DTEND:20230326T150000Z
SUMMARY:客户会议
LOCATION:客户办公室
DESCRIPTION:与客户讨论项目进展
END:VEVENT
BEGIN:VEVENT
UID:20230325T130000Z-12347@example.com
DTSTAMP:20230325T130000Z
DTSTART:20230327T100000Z
DTEND:20230327T120000Z
SUMMARY:设计审查
LOCATION:会议室B
DESCRIPTION:审查设计方案
END:VEVENT
END:VCALENDAR

这个日程安排包含三个事件，分别是早餐会议、客户会议和设计审查。你可以将上面的代码复制到一个文本编辑器中，并将文件保存为 .ics 文件。然后，将该文件发送到你的邮箱，并在 iPhone 或 Mac 上打开它，就可以将这些事件添加到你的日历中了。
```


# TODO
1. 将数据进行清洗，整理，导入到数据库之中（可以考虑爬取更多数据，进行整合）
2. 了解ChatGPT上插件的流程，尤其是收费流程
3. 小程序的设计和制作，小程序导入ChatGPT的接口进行使用（LangChain）

# DeBug
1. 乱码问题
2. 多线程问题


## requirements
```raw
conda create -n health
conda activate health
pip install -r requirement.txt
```