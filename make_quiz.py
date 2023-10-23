# coding=utf-8

# 最新版的selenium(4.x.x)已经不支持PhantomJS。如要用PhantomJS，可用旧版本selenium。如pip install selenium==3.8.0。
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import xlwt
import re
import argparse


browser = webdriver.Chrome()
WAIT = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)

m_from_s = 0  #从搜索结果的第n个句子开始引用，比如之前已经生成了3份试卷，又想再生成1份试卷，所以最后从第4个句子开始，就不会和之前的重复
m_fast = 0 #快速模式，即不需要选择句子

def getText(text, cnt):
    try:
        print('开始访问....',text)
        browser.get("https://zaojv.com/wordQueryDo.php")

        input_info = WAIT.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/table/tbody/tr/td[2]/form/input[5]")))
        submit = WAIT.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div/div[1]/table/tbody/tr/td[2]/form/input[6]')))
        
        input_info.send_keys(text)
        submit.click()

#        WAIT.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]')) or EC.presence_of_element_located((By.XPATH, '//*[@id="content"]')))
        print("get result")
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')

        div_bs4 = soup.find('div', id = "all")
        if(div_bs4 is None):
            div_bs4 = soup.find('div', id = "content")
            
        if(div_bs4 is None):
            print("error:没有查找到句子:",text)
            return "error"

        a=[]        
        dstFile = text+"_all.txt"
        mon1 = open(dstFile,"w",encoding='utf-8') 
                
        for item in div_bs4:
            jz = item.text
            jz = jz.replace(text, "___"+text+"___")
            a.append(jz)	
            mon1.write(jz+"\n")
        mon1.flush()
        mon1.close()
        
        b=[]
        if(m_fast == 1):
            for i in range(cnt):
                b.append(a[i+1][2:])
                
        else:
            sel = 0
            i = m_from_s+1
            print("你有 ",len(a)," 个选择")
            while (sel<cnt) and i<len(a):
                print(a[i])
                keyin=input("采纳直接按回车，否则按空格再回车")
                if(keyin!=""):
                    print("next")
                else:
                    print("ok")
                    sel+=1
                    b.append(a[i][2:])
                i += 1
            print("end",cnt)
            
        if len(b)==cnt:
            return b      
        else:
            print("error:",text, " len:",len(a))
            return a  
            
            
    except TimeoutException:
        return "search TimeoutException"    
  

    
def get_file(srcFile, cnt):
	
    ms = open(srcFile,encoding='utf-8')  
    lines=ms.readlines()
    textArray = []  #词语表
    a=[]    #格式为[text][cnt]

    for i in range(len(lines)):
        textArray.append(lines[i].strip())
        
    for i in range(len(textArray)):
        print("\n\n处理第 ", i ," 个词语：", textArray[i])
        b = getText(textArray[i], cnt)  #每个词语生成cnt个句子
#        print("len b:",len(b))
        if len(b) != cnt:
            print("error word: ", textArray[i])
        a.append(b)
        
    
    
    
    
    c=[]    #格式[cnt][text]   

    for i in range(cnt):
        d=[] 
        for j in range(len(textArray)):
            d.append(a[j][i])
        c.append(d)
    print("len c:",len(c))
    
    for i in range(cnt):
        print("\n\nanswers_", i+1, ":")
        d=c[i]
        e=[]
        for j in range(len(d)):
            e.append(d[j])
        e.sort()	#打乱顺序
        dstFile = srcFile[:-4]+"_answers_"+str(i)+".txt"   #答案文件
        mon1 = open(dstFile,"w",encoding='utf-8') 
        for j in range(len(textArray)):
            que = ""+str(j+1)+"、"+e[j]
            print(que)
            mon1.write(que+"\n")
        mon1.flush()
        mon1.close()
            
    e=[] #  [cnt][text]   
    for i in range(cnt):
        print("\n\nquestions_", i+1, ":")
        d=c[i] 
        e=[]
        for j in range(len(textArray)):
#            print(textArray[i])
            question = d[j].replace(textArray[j],"__________")            
#            print(j+1,"、",question)
            e.append(question)
        e.sort()
        dstFile = srcFile[:-4]+"_questions_"+str(i)+".txt"  ##问题文件
        mon1 = open(dstFile,"w",encoding='utf-8') 

        for j in range(len(textArray)):
            que = ""+str(j+1)+"、"+e[j]
            print(que)
            mon1.write(que+"\n")
        mon1.flush()
        mon1.close()

    ms.close()            
            
 

if __name__ == "__main__":
    # Parse command line options
    #python zaoju.py b.txt -n 3 -s 0
    #python zaoju.py b.txt -n 3 -s 0 -f 1
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help="src file to search")
    parser.add_argument("-n", "--n", help="生成n份试卷", default=3, type=int)
    parser.add_argument("-s", "--s", help="从第s个例句开始选择", default=0, type=int)
    parser.add_argument("-f", "--f", help="快速模式，不需用户选择句子", default=0, type=int)
    args = parser.parse_args()
    	  
    srcFile = args.srcFile
    n=args.n
    m_from_s=args.s
    m_fast=args.f
    
    try:
        get_file(srcFile, n)
    
        print(__name__+'from get_file.main')          
    
    finally:
        browser.close()     
    print("end") 
