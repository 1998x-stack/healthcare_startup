# healthcare_startup

## Info List

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


## code
1. jibinginfo.ipynb
* target: 获取每个科目下的疾病类型以及具体信息
* from: http://www.xywy.com/
* TODO: multiprocessing

2. ques_ans.ipynb and ques_ans.py
* target: 获取医生和患者的对话信息
* from: http://www.xywy.com/
* 后者采用多线程

## data
1. yiyuandiqu-beijing.csv 
* it is get from http://z.xywy.com/yiyuandiqu-beijing.htm use instant scrap extension
* it gets all hospitals from beijing

2. dingxiang_hospital.csv
* it is got from 用药助手, but only 20 pages



## requirements

conda create -n health
conda activate health
pip install -r requirement.txt
