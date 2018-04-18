# NFParser
NFParser é um trabalho feito para a matéria EA876 no primeiro semestre de 2018 ministrada pelo Professor Tiago Fernandes Tavares.

---
# Descrição
Processa uma nota fiscal eletronica em formato XML e gera um arquivo de saida
em formato CSV no seguinte formato:

MUNICIPIO_GERADOR,MUNICIPIO_PRESTADOR,VALOR_NF,VALOR_ISS_RETIDO
## Modo de uso
```
usage: NFParser.py [-h] [-v] [--dry-run] path

Processa uma nota fiscal eletronica em formato XML e gera um arquivo de saida
em formato CSV no seguinte formato:
MUNICIPIO_GERADOR,MUNICIPIO_PRESTADOR,VALOR_NF,VALOR_ISS_RETIDO

positional arguments:
  path           Caminho para o arquivo xml da nota fiscal.

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Imprime a saida csv do programa em stdin.
  --dry-run      Nao gera os arquivos csv mas executa o programa.
```
## Instalação
#### **NFParser** requer Python >= 3
Para instalar basta apenas digitar em uma sessão do terminal
`git clone https://github.com/steckmarco/EA876-Trabalho1.git`

