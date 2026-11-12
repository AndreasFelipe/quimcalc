from math import isfinite

from logica.analise import analisar


def ler_positivo(texto, nome):
    try:
        valor = float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"{nome}: informe um número maior que zero, usando vírgula ou ponto decimal.") from None
    if not isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser um número finito maior que zero.")
    return valor


def verificar_resultado(valor):
    if not isfinite(valor) or valor <= 0:
        raise ValueError("Os valores informados excedem a faixa numérica do cálculo. Use valores menos extremos.")
    return valor


def calcular_solucao(campos):
    modo = campos.get("modo", "")
    if modo not in ("solido", "diluicao"):
        raise ValueError("Selecione um modo de preparo válido.")

    concentracao = ler_positivo(campos.get("concentracao", ""), "A concentração desejada")
    volume = ler_positivo(campos.get("volume", ""), "O volume final")
    unidade = campos.get("unidade", "")
    if unidade not in ("mL", "L"):
        raise ValueError("Selecione uma unidade de volume válida: mL ou L.")

    dados = {"modo": modo, "concentracao": concentracao,
             "volume": volume, "unidade": unidade}

    if modo == "solido":
        formula = campos.get("formula", "").strip()
        if formula and formula[0].isdigit():
            raise ValueError("Informe a fórmula sem um coeficiente antes dela.")
        try:
            massa_molar = analisar(formula)["massa_molar"]
        except RecursionError:
            raise ValueError("Simplifique os níveis de parênteses da fórmula.") from None

        volume_litros = verificar_resultado(volume / 1000 if unidade == "mL" else volume)
        mol = verificar_resultado(concentracao * volume_litros)
        massa = verificar_resultado(mol * massa_molar)
        dados.update(formula=formula, massa_molar=massa_molar,
                     volume_litros=volume_litros, mol=mol, massa=massa)
    else:
        estoque = ler_positivo(campos.get("estoque", ""), "A concentração da solução estoque")
        if concentracao >= estoque:
            raise ValueError("A concentração desejada deve ser menor que a concentração da solução estoque para realizar uma diluição.")
        # V1 e V2 podem usar a mesma unidade; não é preciso converter para L.
        volume_estoque = verificar_resultado((concentracao / estoque) * volume)
        dados.update(estoque=estoque, volume_estoque=volume_estoque)

    return dados
