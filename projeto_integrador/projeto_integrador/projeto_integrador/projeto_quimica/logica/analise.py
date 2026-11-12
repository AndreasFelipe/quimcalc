from math import fsum
from string import ascii_letters, digits

from periodictable import formula
from pyparsing import ParseBaseException


SUBSCRITOS = str.maketrans("₀₁₂₃₄₅₆₇₈₉·", "0123456789+")
CARACTERES = frozenset(ascii_letters + digits + "()[]{}+-. \t\r\n")


def analisar(texto):
    texto = texto.strip()
    if not texto:
        raise ValueError("Digite uma fórmula química.")
    if len(texto) > 256:
        raise ValueError("Use uma fórmula com até 256 caracteres.")

    normalizada = texto.translate(SUBSCRITOS)
    # Restringe a entrada a fórmulas; exclui misturas em %, densidades e sequências.
    if any(caractere not in CARACTERES for caractere in normalizada):
        raise ValueError("Há caracteres não aceitos. Consulte os exemplos de notação.")

    try:
        composto = formula(normalizada)
    except (ParseBaseException, ValueError, KeyError, ZeroDivisionError):
        raise ValueError("Fórmula inválida. Confira símbolos, isótopos, cargas e parênteses.") from None
    except TypeError:
        # No periodictable 2.1.0, Og[294], por exemplo, falha ao calcular a densidade.
        raise ValueError("A biblioteca não consegue processar este isótopo isolado por falta de dados de densidade. Tente o símbolo sem o isótopo.") from None

    if hasattr(composto, "total_mass") or hasattr(composto, "thickness"):
        raise ValueError("Digite apenas a fórmula, sem unidades como g, mL ou nm.")

    composicao = []
    total_atomos = 0
    tem_ions = False
    for atomo, quantidade in composto.atoms.items():
        if quantidade <= 0 or quantidade != int(quantidade):
            raise ValueError("As quantidades finais de átomos devem ser inteiras e positivas.")

        quantidade = int(quantidade)
        massa = atomo.mass
        contribuicao = quantidade * massa
        composicao.append({
            "simbolo": str(atomo),
            "quantidade": quantidade,
            "massa": massa,
            "contribuicao": contribuicao,
        })
        total_atomos += quantidade
        tem_ions = tem_ions or atomo.charge != 0

    massa_molar = fsum(item["contribuicao"] for item in composicao)

    for item in composicao:
        item["percentual"] = item["contribuicao"] * 100 / massa_molar

    return {
        "formula": texto,
        "composicao": composicao,
        "total_atomos": total_atomos,
        "massa_molar": massa_molar,
        "tem_ions": tem_ions,
    }
