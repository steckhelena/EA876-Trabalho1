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
    arvore.add_text(xml)

    return arvore

def parseElements(elementsList, start):
    if start == -1:
        arvore = ElementRoot()
    else:
        arvore = Element(elementsList[start][0])

    end = start+1
    for i, elemento in enumerate(elementsList[start+1:]):
        if i+start+1 < end-1:
            continue
        if elemento[3] == 0:
            newElement, end = parseElements(elementsList, i+start+1)
            arvore.add_child(newElement)
        elif start != -1:
            arvore.add_text_indexes(elementsList[start][2], elemento[1])
            end += 1
            break
        end += 1

    return arvore, end

class ElementRoot:
    def __init__(self):
        self.childreen = []

    def add_child(self, child):
        self.childreen.append(child)

    def add_text(self, text):
        self.text = text

    def getText(self, child):
        return self.text[child.textStart:child.textEnd]

    def getAllPaths(self):
        paths = []

        for child in self.childreen:
            alo = [str(child.tag+"/"+i) for i in child.getAllPaths()]
            paths.extend(alo)

        if len(self.childreen) == 0:
            return [self.tag]
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

    def add_text_indexes(self, textStart, textEnd):
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

    
    
