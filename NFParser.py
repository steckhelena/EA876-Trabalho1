import sys
import re

def createElementTree(xml):
    """
    Visita cada no do arquivo xml e retorna uma arvore com todas as relacoes.

    Esta funcao retorna um ElementRoot criado a partir das tags encontradas no
    arquivo xml, ela primeiramente encontra as tags de abertura e fechamento e
    as ordena em uma lista unica para entao ser passada para a funcao
    parseElements que montara a arvore em si.
    """
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
    """
    A partir da elementsList monta recursivamente uma arvore de relacoes xml.

    Esta funcao monta recursivamente a raiz e os membros filhos de cada no da
    classe ElementRoot, realiza isso chamando recursivamente ela mesma quando
    encontra uma tag de abertura e retornando quando acha uma tag de fechamento.
    Esta funcao apenas funciona com arquivos xml validos.
    """
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
    """
    Classe que representa a raiz de uma arvore de relacoes xml.
    """
    def __init__(self):
        self.childreen = []

    def addChild(self, child):
        """Adiciona um no filho ao elemento da arvore."""
        self.childreen.append(child)

    def addText(self, text):
        """Adiciona uma string a partir da qual getText extraira os seus membros."""
        self.text = text

    def getText(self, child):
        """Retorna todo o texto encontrado entre as tags de abertura e fechamento do no."""
        return self.text[child.textStart:child.textEnd]

    def getAllPaths(self):
        """
        Retorna todos os caminhos da raiz ate as folhas.

        O formato dos caminhos se da como: child/child1/child2/.../childN/
        """
        paths = []

        for child in self.childreen:
            alo = [str(child.tag+"/"+i) for i in child.getAllPaths()]
            paths.extend(alo)

        if len(self.childreen) == 0:
            return [""]
        return paths

    def getChildByPath(self, path):
        """Retorna um elemento da arvore a partir do caminho no mesmo formato do retornado por getAllPaths"""
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
    """
    Classe que representa um elemento que nao a raiz da arvore de relacoes xml.
    """
    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    def addTextIndexes(self, textStart, textEnd):
        """Adiciona os indices do texto que representam o conteudo entre as tags deste elemento."""
        self.textStart = textStart
        self.textEnd = textEnd

def abbreviationHeuristics(tree, lista):
    """
    Esta funcao atribui um score para cada caminho na arvore de ser alguma abreviacao das palavras na lista.
    """
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
                    # Procura todos os indices que separam o caminho
                    pathSepIndexes = [index for index, value in enumerate(path) if value == '/']
                    possible = []
                    for index in abbIndexes:
                        aux = index
                        # Ultimo indice da palavra em que foi encontrada a letra que pode estar na abreviacao
                        lastWordIndex = 0
                        # Tamanho da abreviacao
                        abbLen = 0
                        # Representa o indice da lista pathSepIndexes que contem a string atual procurada
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
                        # Calcula o scroe da palavra atual ser uma abreviacao de 'word' de 0 a 1
                        possible.append((abbLen/len(word))*((aux-index)/len(path[sepStart:sepEnd])))
                    if possible:
                        prob += max(possible)
            # Limita a probabilidade entre 0 e 1
            prob = prob/len(filtro)
            # Adiciona ao score a probabilidade com um fator relacionado ao seu indice na lista de este caminho ser a resposta
            score += prob*(len(lista)-lista.index(filtro))
        # Adiciona o elemento representado pelo caminho e seu score a lista de retorno
        answers.append((tree.getChildByPath(path), score))
    
    return answers

def genericToFloat(tree, element):
    """
    Retorna um numero qualquer em string como float.

    Para qualquer numero formatado com casas de milhares e separador decimal 
    retorna um float.
    Exemplo:
    "1999,7" -> 1999.7
    "1,999.7" -> 1999.7
    "1.999,7" -> 1999.7
    """
    text = tree.getText(element).replace(',', '.')
    ret = text.split('.')[:-1]
    ret = [''.join(ret).replace('.', '')]
    ret.append(text.split('.')[-1])
    return float('.'.join(ret))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error! Please use the following syntax to call the program:\nNFParser.py caminho_para_NF.xml")
        exit()
    
    # Estas sao as listas com os filtros utilizados para procurar os conteudo na nota fiscal, cada sublista eh um filtro
    # A posicao do filtro na lista determina o seu peso, quanto mais para o inicio maior sera seu peso.
    listaGerador = [["tomador", "cidade"], ["tomador", "municipio"], ["tomador", "cep"], ["tomador", "codigo", "municipio"]]
    listaPrestador = [["prestador", "cidade"], ["prestador", "municipio"], ["prestador", "cep"], ["prestador", "codigo"," municipio"]]
    listaValor = [["valor", "nota"], ["valorservicos"], ["valor", "servico"]]
    listaIss = [["valoriss"], ["valor", "iss"], ["iss", "ret"]]
    
    content = ""  # Conteudo do arquivo xml
    encoding = ""  # Encoding do arquivo xml

    # Busca o encoding do arquivo xml se um header xml com o encoding estiver presente
    with open(sys.argv[1], 'rb') as fileIn:
        encoding = re.match("<\?xml.*?encoding=.*?\?>", str(fileIn.readline(), "utf-8"))
        if encoding is not None:
            encoding = re.search("encoding=\".*?\"", encoding.group()).group()
            encoding = encoding[len("encoding=\""):-1]
        else:
            # Encoding padrao do xml
            encoding = "utf-8"
    
    # Recupera o conteudo do arquivo xml
    with open(sys.argv[1], 'r', encoding=encoding) as fileIn:
        content = fileIn.read()
    
    # Estas listas conterao os possiveis elementos da arvore xml que sao as respostas procuradas na NF
    mGerador = []
    mPrestador = []
    valor = []
    issRetido = []
    
    # Gera a arvore xml e procura pelas respostas em seus caminhos utilizando os filtros declarados acima
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
    
    # Se utilizando os filtros alguma das listas continua vazias utiliza uma heuristica para tentar encontrar
    # o caminho com maior probabilidade de conter o elemento que se procura.
    if not mGerador:
        mGerador = abbreviationHeuristics(tree, listaGerador)
    if not mPrestador:
        mPrestador = abbreviationHeuristics(tree, listaPrestador)
    if not valor:
        valor = abbreviationHeuristics(tree, listaValor)
    if not issRetido:
        issRetido = abbreviationHeuristics(tree, listaIss)
    
    # Extrai o municipio gerador da lista mGerador, que contem as possiveis respostas
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
    
    # Extrai o municipio prestador da lista mPrestador, que contem as possiveis respostas
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

    # Extrai o valor da NF da lista valor, que contem as possiveis respostas
    valor = [v for v in valor if tree.getText(v[0]).replace(',', '.').replace('.','').isdigit()]
    valorMax = max(valor, key=lambda x: x[1])[1]
    valor = [v for v in valor if v[1] >= valorMax]
    valor = [genericToFloat(tree, v[0]) for v in valor if genericToFloat(tree, v[0]) > 0]
    valorServico = max(valor)
    
    # Extrai o valor do iss retido da lista issRetido, que contem as possiveis respostas
    issRetido = [v for v in issRetido if tree.getText(v[0]).replace(',', '.').replace('.','').isdigit()]
    issMax = max(issRetido, key=lambda x: x[1])[1]
    issRetido = [v for v in issRetido if v[1] >= issMax]
    issRetido = [genericToFloat(tree, v[0]) for v in issRetido if (genericToFloat(tree, v[0]) > 0 and genericToFloat(tree, v[0]) != valorServico)]
    if issRetido:
        iss = max(issRetido)
    else:
        iss = 0.0
    
    print(municipioGerador, municipioPrestador, valorServico, iss, sep=',')

    
