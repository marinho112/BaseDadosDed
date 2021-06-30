import bs4
import urllib.request as urllib_request
import pandas
import json

from urllib.request import Request,urlopen
from bs4 import BeautifulSoup

def buscarInfo(fileSoup):

    soup=fileSoup

    
    #var=soup.find('table',{"class": "statBlock"})
    #print(json.dumps(dict(var)))
    #print(var)
    numTable=0
    tables=[]
    for table in soup.find_all('table',{"class": "statBlock"}):
        numTable+=1
        thFirst=True
        trs=[]
        for tr in table.find_all('tr'):
            ths=[]
            for th in tr.find_all('th'):
                ths.append(th.get_text().strip())
            if(thFirst):
                ths.pop(0)    
                trs.append(["Name:",ths])
                #j[strVar(numTable)]={"Name":ths}
                thFirst=False
            else:
                tds=[]
                for td in tr.find_all('td'):
                    tds.append(td.get_text().strip())
                trs.append([ths[0],tds])
                #j[strVar(numTable)]={ths[0]:tds}
        strVar="{"        
        for x in range(len(trs)):
            item = trs[x]
            strVar+='"'+item[0]+'":['
            for i in range(len(item[1])):
                subItem=item[1][i]
                strVar+='"'+subItem+'"'
                if(i<(len(item[1])-1)):
                    strVar+=','
                else:
                    strVar+=']'
            if(x<(len(trs)-1)):
                strVar+=',\n'
            else:
                strVar+='}'
        #j=json.loads(strVar)
        tables.append(strVar)
        
    strVar="{"
    for t in range(len(tables)):
        tabela=tables[t]
        strVar+='"'+str(t+1)+'":'+tabela
        if(t<(len(tables)-1)):
            strVar+=','
        else:
            strVar+='}'
    j=json.loads(strVar)

    return j

def EsquerdaPraDireita_CimaPraBaixo(lista,nome,header):
    j={nome:{}}
    #print(header)
    for item in lista:
        if(len(item)>0):
            son={}
            nomeCampo=""
            x=0
            y=0
            for i in range(len(item)):
                val=item[i]
                if(i==0):
                    nomeCampo=val
                else:
                    if(len(header[i-x])==1):
                        son[header[i-x][0]]=val
                    else:
                        if(y==0):
                            son[header[i-x][0][0]]={}
                        son[header[i-x][0][0]][header[i-x][1][y]]=val
                        y+=1
                        if(y<len(header[i-x][1])):
                            x+=1
                        else:    
                            y=0
            j[nome][nomeCampo]=son
    #print(j)        
    return j

def listaParaJson(lista,nome,header,tipo):
    if(tipo=="EsquerdaPraDireita_CimaPraBaixo"):
        return EsquerdaPraDireita_CimaPraBaixo(lista,nome,header)
    print("Não reconhece tipo de tabela escolhido")
    return {}

def tabelaToJson(tabela):
    lista=[]
    p=-1
    tableName=None
    x=tabela.find("caption")
    if(x!=None):
        tableName=x.get_text().strip()
    elif(str(x.attrs).count('id')!=None):
        tableName=str(x['id'])
    if(tableName==None):
        print("Não foi possivel obter o nome da tabela: ")
        print(tabela)
        return
    h={}
    for tr in tabela.find_all('tr'):
        #name=tr.get_text().strip()
        lista.append([])
        p+=1
        lsTh=[]
        for th in tr.find_all('th'):
            value=[th.get_text().strip()]
            if(str(th.attrs).count('colspan')!=0):
                l=[]
                for i in range(int(th['colspan'])):
                    l.append(None)
                value=[value,l]
            lsTh.append(value)
        if(len(lsTh)>0):
            h[str(p)]=lsTh
        for td in tr.find_all('td'):
            lista[p].append(td.get_text().strip())
            #j[name]=td.get_text().strip()
        header=[]
        
    for i in h.keys():
        if(header==[]):
            for x in range(len(h[i])):
               header.append(h[i][x])
        else:
            k=0
            for x in range(len(h[i])):
                item=h[i][x][0]
                for e in range(len(header)):
                    if(len(header[e])>1):
                        for w in range(len(header[e][1])):
                            if((item!=None)and(header[e][1][w]==None)):
                                header[e][1][w]=item
                                item=None

    tipo="EsquerdaPraDireita_CimaPraBaixo"
    return listaParaJson(lista,tableName,header,tipo)
   
def buscaComplemento(fileSoup):
    soup=fileSoup
    var=soup.find('body')
    listaRemover=var.find_all('table',{"class": "statBlock"})
    for tabela in listaRemover:
        #print(tabela)
        tabela.replaceWith("")
    var.find("div",{"id": "header"}).replaceWith("")
    var.find("div",{"class": "footer"}).replaceWith("")
    for script in var.find_all("script"):
        script.replaceWith("")
    tabelas = []#soup.find_all('table')
    for table in soup.find_all('table'):
        tabelas.append(tabelaToJson(table))
        table.replaceWith("")
    
    #texto=var.get_text().split('\n')
    #novoTexto=[]
    #for linha in texto:
    #    if(linha!=""):
    #        novoTexto.append(linha)
    
    listaTags=var.find_all_next()
    listaNomes=[""]
    listaTexto=[""]
    position=0
    for tag in listaTags:
        textoTag=tag.get_text().strip()
        if(textoTag!=""):
            if(tag.name[0]=='h'):
                listaNomes.append(textoTag)
                listaTexto.append("")
                position+=1
            else:
                listaTexto[position]+=textoTag
    lista=[]
    for x in range(len(listaNomes)):
        nome=listaNomes[x]
        if(nome==""):
            nome=str(x)
        lista.append([nome,listaTexto[x]])
    return [lista,tabelas]
    
def verificaRelacao(key,jayKey,j):
    if key.lower().count(jayKey.lower()) != 0:
        return True
    else:
        splitType=j[key]["Size/Type:"].split('(')
        listType=None
        if(len(splitType)>1):
            listType=splitType[1].replace(')','')
            listType=listType.split(',')
            for tpe in listType:    
                if(jayKey.lower()==tpe.lower()):
                    return True
    return False  

def verificaRelacaoTabela(key,jayKey,j):
    split=key.split(',')
    for s in split:
        if jayKey.lower().count(s.lower().strip()) != 0:
            return True
    
    splitType=j[key]["Size/Type:"].split('(')
    listType=None
    if(len(splitType)>1):
        listType=splitType[1].replace(')','')
        listType=listType.split(',')
        for tpe in listType:    
            if(jayKey.lower()==tpe.lower()):
                return True
    return False  

    
file = "elemental"
url = 'https://www.d20srd.org/srd/monsters/'+file+'.htm'

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urlopen(req)
html = response.read()

soup = BeautifulSoup(html, 'html.parser')
j=buscarInfo(soup)
out=buscaComplemento(soup)
lista=out[0]
tabelas=out[1]

#listaTamanhos=["Small","Medium","Large","Huge","Greater","Elder"]

novoJ={}
nomeAtual=""
for key in j.keys():
    tamanho=len(j[key]["Name:"])
    for i in range(tamanho):
        for subKey in j[key].keys():
            item = j[key][subKey][i]
            if(subKey=="Name:"):
                nomeAtual=item
                novoJ[nomeAtual]={}
            else:
                novoJ[nomeAtual][subKey]=item
#print(novoJ)
listaKeys=novoJ.keys()
conteudos=[]
posiConteudo=-1
seted=False
for item in lista:
    seted=False
    for key in listaKeys:
        if key.lower().count(item[0].lower()) != 0 :
            seted=True
    if(seted):
        conteudos.append([item[0],{item[0]:item[1]}])
        posiConteudo+=1
    else:
        if(posiConteudo>=0):
            conteudos[posiConteudo][1][item[0]]=item[1]
jay={}
for item in conteudos:
    jay[item[0]]=item[1]
    
jayKeys=jay.keys()
for key in listaKeys:
    novoJ[key]["Features"]={}
    for jayKey in jayKeys:
        if verificaRelacao(key,jayKey,novoJ) :
            novoJ[key]["Features"][jayKey]=jay[jayKey]

for key in listaKeys:
    novoJ[key]["Tables"]={}
    for tabela in tabelas:
        tabKeys=tabela.keys()
        for tabKey in tabKeys:
            if verificaRelacaoTabela(key,tabKey,novoJ) :
                novoJ[key]["Tables"][tabKey]=tabela[tabKey]

#print(jay)
#arquivo = open('Monstros/'+file+'.json', 'w')
arquivo = open('Monstros/'+file+'aa.json', 'w')
arquivo.write(json.dumps(novoJ))
arquivo.close()