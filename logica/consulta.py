from dados.elementos import ELEMENTOS
from dados.nomes import NOMES
from dados.nomes import simbolo_nome


def consultar(texto):
    simbolo = texto.capitalize()

    if not simbolo:
        raise ValueError("Entrada vazia.")


    if simbolo not in ELEMENTOS:
        simbolo = NOMES.get(simbolo.lower())

    propriedades = ELEMENTOS.get(simbolo)

    if propriedades is None:
        raise ValueError("Elemento não encontrado.")

    nome = simbolo_nome[simbolo]

    return simbolo, nome, propriedades
