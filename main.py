import pymongo
client = pymongo.MongoClient("mongodb+srv://Alisson:BSiUadYRPaVrmQTM@cluster0.cqpscdj.mongodb.net/?retryWrites=true&w"
                             "=majority")
db = client["covid19-data"]
# collection = db.create_collection('dados')
collection = db.get_collection('dados')


# Verifica se a palavra possui alguma letra repetida.
def verifica_palavra(pal):
    cont = 0
    for x in range(cont, len(pal)):
        for y in range(cont + 1, len(pal) - 1):
            if pal[x] == pal[y]:
                return 0
        cont += 1
    return 1


# Pega a palavra-chave
def palavra_chave():
    palavra = str(input("Insira a palavra para usar como palavra-chave para a criptografia: "))

    t = verifica_palavra(palavra)

    print(len(palavra))

    while t == 0:
        palavra = str(input("Insira a palavra válida para usar como palavra-chave para a criptografia: "))
        t = verifica_palavra(palavra)
    return palavra


# vetor com a numeração de cada letra na palavra
def ordem_letra(vet, pal):
    for x in range(len(pal)):
        cont = 0
        for y in range(len(pal)):
            if pal[x] >= pal[y]:
                cont += 1
        vet.append(cont)


def criptografa(chave, posicao, pal):
    cont = 1
    nova = ''
    while cont <= len(chave):
        posatual = 0
        for c in range(len(posicao)):
            if posicao[c] == cont:
                posatual = c
                break
        while posatual < len(pal):
            nova = nova + pal[posatual]
            posatual += len(chave)
        cont += 1
    return nova


def descriptografa(ord_letra, pal_cript, chave):
    lista = []
    lista2 = []

    for y in range(len(chave)):
        lista2.append(0)

    for y in range(len(ord_letra)):
        lista2[ord_letra[y] - 1] = y

    for x in range(len(pal_cript)):
        lista.append(';')

    inteiro = len(pal_cript) // len(lista2)
    resto = len(pal_cript) % len(lista2) - 1
    posicao = 0
    for k in range(len(lista2)):
        cont = lista2[k]
        if lista2[k] <= resto:
            for y in range(inteiro + 1):
                lista[cont] = pal_cript[posicao]
                posicao += 1
                cont += len(chave)
        else:
            for z in range(inteiro):
                lista[cont] = pal_cript[posicao]
                posicao += 1
                cont += len(chave)
    return ''.join(lista)


def insere_banco(pal, posicao):
    arquivo = open("covid_19_data.csv", 'r')

    for linha in arquivo:
        dados = {}
        prov = linha.split(',')
        dados["SNo"] = int(prov[0])
        dados["ObservationDate"] = prov[1]
        dados["Province/State"] = criptografa(pal, posicao, prov[2])
        dados["Country/Region"] = prov[3]
        dados["LastUpdate"] = prov[4]
        dados["Confirmed"] = float(prov[5])
        dados["Deaths"] = float(prov[6])
        dados["Recovered"] = float(prov[7])
        collection.insert_one(dados)


def mostra(dados):
    for k, v in dados.items():
        print(f'{k}: {v}')


def consulta1(pais):
    query = {"Country/Region": pais, "Confirmed": {"$gt": 0}}
    x = collection.find_one(query)
    mostra(x)
    opc_desc = str(input('Deseja descriptografar o valor Province/State? [S/N]')).upper()
    if opc_desc == 'S':
        palavra = palavra_chave()
        posicao = []
        ordem_letra(posicao, palavra)
        x["Province/State"] = descriptografa(posicao, x["Province/State"], palavra)
        mostra(x)


def consulta(chave_dict, valor_dict, cmp):
    query = None
    if chave_dict == "ObservationDate":
        query = {chave_dict: valor_dict}
    elif chave_dict == "LastUpdate":
        valor_dict = '^' + valor_dict
        query = {chave_dict: {"$regex": valor_dict}}
    x = collection.find(query)
    dados = x[0]
    for y in x:
        if y[cmp] > dados[cmp]:
            dados = y
    mostra(dados)
    opc_desc = str(input('Deseja descriptografar o valor Province/State? [S/N]')).upper()
    if opc_desc == 'S':
        palavra = palavra_chave()
        posicao = []
        ordem_letra(posicao, palavra)
        dados["Province/State"] = descriptografa(posicao, dados["Province/State"], palavra)
        mostra(dados)


while True:
    print('1 - Inserir dados no banco\n'
          '2 - Primeiro registro confirmado em determinado país\n'
          '3 - País que teve o maior numero de mortos em uma data de atualização\n'
          '4 - País que teve o maior número de recuperados em uma data de observação\n'
          '5 - Maior numero de casos confirmados em uma data de observação\n'
          '0 - Sair')
    opc = int(input('Escolha: '))
    if opc == 0:
        print('SAINDO...')
        break
    if opc == 1:
        pos = []
        palav = palavra_chave()
        ordem_letra(pos, palav)
        insere_banco(palav, pos)
    elif opc == 2:
        p = str(input('Informe o nome do país: '))
        consulta1(p)
    elif opc == 3:
        d = str(input('Informe a data no formato [aaaa-mm-dd]: '))
        consulta("LastUpdate", d, "Deaths")
    elif opc == 4:
        d = str(input('Informe a data no formato [mm/dd/aaaa]: '))
        consulta("ObservationDate", d, "Recovered")
    elif opc == 5:
        d = str(input('Informe a data no formato [mm/dd/aaaa]: '))
        consulta("ObservationDate", d, "Confirmed")
