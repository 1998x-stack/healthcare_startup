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