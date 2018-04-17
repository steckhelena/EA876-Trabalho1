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

    i = start
    while i < len(elementsList):
        if elementsList[i][3] == 0:
            newElement, i = parseElements(elementsList, i+1)
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error! Please use the following syntax to call the program:\nNFParser.py caminho_para_NF.xml")
        exit()

    content = ""

    with open(sys.argv[1], 'r', encoding="utf-8") as fileIn:
        content = fileIn.read()

    tree = createElementTree(content)
    for i in tree.getAllPaths():
        print(i)
        print(tree.getText(tree.getChildByPath(i)))

    
    
