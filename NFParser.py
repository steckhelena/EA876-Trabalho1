import sys
import re

def createElementTree(xml):
    tagInicio = re.compile("(<[^/\!\?].*?>)", re.IGNORECASE | re.UNICODE)
    tagFim = re.compile("(</.*?>)", re.IGNORECASE | re.UNICODE)

    tagsInicio = tagInicio.finditer(xml)
    tagsFim = tagFim.finditer(xml)

    elementos = []

    for m in tagsInicio:
        elementos.append((m.group().strip('<>').split(' ')[0].lower(), m.start(), m.end(), 0)) # zero representa inicio tag

    for m in tagsFim:
        elementos.append((m.group().strip('<>').split(' ')[0][1:].lower(), m.start(), m.end(), 1)) # um representa fim da tag

    elementos = sorted(elementos, key=lambda x: x[1])

    arvore, _ = parseElements(elementos, -1)
    arvore.addText(xml)

    return arvore

def parseElements(elementsList, start):
    if start == -1:
        arvore = ElementRoot()
        newElement, end = parseElements(elementsList, 0)
        arvore.addChild(newElement)
        return arvore, len(elementsList)
    
    arvore = Element(elementsList[start][0])
    
    i = start+1
    while i < len(elementsList):
        if elementsList[i][3] == 0:
            newElement, i = parseElements(elementsList, i)
            arvore.addChild(newElement)
        else:
            arvore.addTextIndexes(elementsList[start][2], elementsList[i][1])
            return arvore, i
        i += 1

    return arvore, i

class ElementRoot:
    def __init__(self):
        self.childreen = []

    def addChild(self, child):
        self.childreen.append(child)

    def addText(self, text):
        self.text = text

    def getText(self, child):
        return self.text[child.textStart:child.textEnd]

    def getAllPaths(self):
        paths = []

        for child in self.childreen:
            alo = [str(child.tag+"/"+i) for i in child.getAllPaths()]
            paths.extend(alo)

        if len(self.childreen) == 0:
            return [""]
        return paths

    def getChildByPath(self, path):
        path = path.split('/')
        parent = self
        for p in path:
            for child in parent.childreen:
                if child.tag == p:
                    parent = child
                    break
        if parent != self:
            return parent
        else:
            return None


class Element(ElementRoot):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    def addTextIndexes(self, textStart, textEnd):
        self.textStart = textStart
        self.textEnd = textEnd

def abbreviationHeuristics(tree, lista):
    answers = []
    for path in tree.getAllPaths():
        score = 0
        for filtro in lista:
            prob = 0
            for word in filtro:
                if word in path:
                    prob += 1
                else:
                    # Procura todos os indices que podem conter a primeira letra da palavra
                    abbIndexes = [index for index, value in enumerate(path) if value == word[0]]
                    pathSepIndexes = [index for index, value in enumerate(path) if value == '/']
                    possible = []
                    for index in abbIndexes:
                        aux = index
                        lastWordIndex = 0
                        abbLen = 0
                        closestSepIndex = 0
                        for i, v in enumerate(pathSepIndexes):
                            if v < index:
                                closestSepIndex = i
                            else:
                                break
                        while True:
                            aux += 1
                            if path[aux] != '/' and path[aux] in word[lastWordIndex:]:
                                abbLen += 1
                                lastWordIndex = word.find(path[aux], lastWordIndex)
                            else:
                                break
                        sepStart = pathSepIndexes[closestSepIndex]
                        sepEnd = pathSepIndexes[closestSepIndex+1]
                        possible.append((abbLen/len(word))*((aux-index)/len(path[sepStart:sepEnd])))
                    if possible:
                        prob += max(possible)
            prob = prob/len(filtro)
            score += prob*(len(lista)-lista.index(filtro))
            if score > 9:
                print(path, score)
        answers.append((tree.getChildByPath(path), score))
    
    return answers

def genericToFloat(tree, element):
    text = tree.getText(element).replace(',', '.')
    ret = text.split('.')[:-1]
    ret = [''.join(ret).replace('.', '')]
    ret.append(text.split('.')[-1])
    return float('.'.join(ret))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        #print("Error! Please use the following syntax to call the program:\nNFParser.py caminho_para_NF.xml")
        exit()
    
    listaGerador = [["tomador", "cidade"], ["tomador", "municipio"], ["tomador", "cep"], ["tomador", "codigo", "municipio"]]
    listaPrestador = [["prestador", "cidade"], ["prestador", "municipio"], ["prestador", "cep"], ["prestador", "codigo"," municipio"]]
    listaValor = [["valor", "nota"], ["valorservicos"], ["valor", "servico"]]
    listaIss = [["valoriss"], ["valor", "iss"], ["iss", "ret"]]

    content = ""
    encoding = ""

    # Retrieves file encoding if header is present
    with open(sys.argv[1], 'rb') as fileIn:
        encoding = re.match("<\?xml.*?encoding=.*?\?>", str(fileIn.readline(), "utf-8"))
        if encoding is not None:
            encoding = re.search("encoding=\".*?\"", encoding.group()).group()
            encoding = encoding[len("encoding=\""):-1]
        else:
            encoding = "utf-8"

    with open(sys.argv[1], 'r', encoding=encoding) as fileIn:
        content = fileIn.read()

    mGerador = []
    mPrestador = []
    valor = []
    issRetido = []

    tree = createElementTree(content)
    for path in tree.getAllPaths():
        for filtro in listaGerador:
            if all(word in path for word in filtro):
                mGerador.append((tree.getChildByPath(path), len(listaGerador)-listaGerador.index(filtro)))
                break
        for filtro in listaPrestador:
            if all(word in path for word in filtro):
                mPrestador.append((tree.getChildByPath(path), len(listaPrestador)-listaPrestador.index(filtro)))
                break
        for filtro in listaValor:
            if all(word in path for word in filtro):
                valor.append((tree.getChildByPath(path), len(listaValor)-listaValor.index(filtro)))
                break
        for filtro in listaIss:
            if all(word in path for word in filtro):
                issRetido.append((tree.getChildByPath(path), len(listaIss)-listaIss.index(filtro)))
                break

    if not mGerador:
        mGerador = abbreviationHeuristics(tree, listaGerador)
    if not mPrestador:
        mPrestador = abbreviationHeuristics(tree, listaPrestador)
    if not valor:
        valor = abbreviationHeuristics(tree, listaValor)
    if not issRetido:
        issRetido = abbreviationHeuristics(tree, listaIss)

    tmpGerador = []
    for v in mGerador:
        text = tree.getText(v[0])
        if text.isdigit() and 7 <= len(text) <= 8:
            tmpGerador.append(v)
        elif not text.isdigit():
            tmpGerador.append(v)
    geradorMax = max(tmpGerador, key=lambda x: x[1])[1]
    mGerador = [v for v in tmpGerador if v[1] >= geradorMax]
    municipioGerador = tree.getText(mGerador[0][0])
    
    mPrestador = [v for v in mPrestador if v[0] != mGerador[0][0]]
    tmpPrestador = []
    for v in mPrestador:
        text = tree.getText(v[0])
        if text.isdigit() and 7 <= len(text) <= 8:
            tmpPrestador.append(v)
        elif not text.isdigit():
            tmpPrestador.append(v)
    prestadorMax = max(tmpPrestador, key=lambda x: x[1])[1]
    mPrestador = [v for v in tmpPrestador if v[1] >= prestadorMax]
    municipioPrestador = tree.getText(mPrestador[0][0])

    valor = [v for v in valor if tree.getText(v[0]).replace(',', '.').replace('.','').isdigit()]
    valorMax = max(valor, key=lambda x: x[1])[1]
    valor = [v for v in valor if v[1] >= valorMax]
    valor = [genericToFloat(tree, v[0]) for v in valor if genericToFloat(tree, v[0]) > 0]
    valorServico = max(valor)
    
    issRetido = [v for v in issRetido if tree.getText(v[0]).replace(',', '.').replace('.','').isdigit()]
    issMax = max(issRetido, key=lambda x: x[1])[1]
    issRetido = [v for v in issRetido if v[1] >= issMax]
    issRetido = [genericToFloat(tree, v[0]) for v in issRetido if (genericToFloat(tree, v[0]) > 0 and genericToFloat(tree, v[0]) != valorServico)]
    if issRetido:
        iss = max(issRetido)
    else:
        iss = 0.0

    print(municipioGerador, municipioPrestador, valorServico, iss)
