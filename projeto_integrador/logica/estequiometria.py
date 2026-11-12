from math import isclose, isfinite

from logica.analise import analisar


MAX_LINHAS = 20
TOLERANCIA = 1e-9


def ler_linhas(formulario, grupo, conhecida):
    """Transforma campos repetidos do formulário em uma lista de substâncias."""
    campos = ["coeficiente", "formula", "unidade"]
    if conhecida:
        campos.append("quantidade")
    colunas = [formulario.getlist(f"{grupo}_{campo}") for campo in campos]
    if any(len(coluna) != len(colunas[0]) for coluna in colunas):
        raise ValueError("Há uma linha incompleta no formulário. Confira os campos.")
    return [dict(zip(campos, valores)) for valores in zip(*colunas)]


def numero_calculado(valor):
    """Impede resultados infinitos ou positivos tão pequenos que virem zero."""
    if not isfinite(valor) or valor <= 0:
        raise ValueError("Os valores informados excedem a faixa numérica do cálculo. Use quantidades e coeficientes menores ou menos extremos.")
    return valor


def preparar_linhas(linhas, conhecida):
    grupo = "Substância conhecida" if conhecida else "Substância desejada"
    if not linhas:
        raise ValueError(f"Informe pelo menos uma {grupo.lower()}.")
    if len(linhas) > MAX_LINHAS:
        raise ValueError(f"Use até {MAX_LINHAS} substâncias por seção.")

    preparadas = []
    formulas_vistas = set()
    for indice, linha in enumerate(linhas, 1):
        try:
            texto = linha["coeficiente"].strip()
            if not texto.isascii() or not texto.isdigit() or len(texto) > 64 or int(texto) <= 0:
                raise ValueError("Informe um coeficiente inteiro maior que zero, com até 64 algarismos.")
            coeficiente = int(texto)
            unidade = linha["unidade"]
            if unidade not in ("g", "mol"):
                raise ValueError("Selecione uma unidade válida: g ou mol.")

            formula = linha["formula"].strip()
            if formula and formula[0].isdigit():
                raise ValueError("Informe o coeficiente no campo próprio, separado da fórmula.")
            dados = analisar(formula)
            # Evita tratar H2 e H₂ como dois reagentes diferentes.
            identidade = tuple(sorted((i["simbolo"], i["quantidade"]) for i in dados["composicao"]))
            if identidade in formulas_vistas:
                raise ValueError("Esta fórmula já foi informada nesta seção. Use uma única linha por substância.")
            formulas_vistas.add(identidade)

            item = {"formula": formula, "coeficiente": coeficiente,
                    "unidade": unidade, "massa_molar": dados["massa_molar"]}
            if conhecida:
                try:
                    quantidade = float(linha["quantidade"].strip().replace(",", "."))
                except ValueError:
                    raise ValueError("Informe uma quantidade maior que zero. Use vírgula ou ponto decimal, sem separador de milhares.") from None
                if not isfinite(quantidade) or quantidade <= 0:
                    raise ValueError("Informe uma quantidade finita maior que zero.")
                mol = quantidade / item["massa_molar"] if unidade == "g" else quantidade
                item.update(quantidade=quantidade, mol=numero_calculado(mol),
                            razao=numero_calculado(mol / coeficiente))
            preparadas.append(item)
        except ValueError as erro:
            raise ValueError(f"{grupo} {indice}: {erro}") from None
        except RecursionError:
            raise ValueError(f"{grupo} {indice}: simplifique os níveis de parênteses da fórmula.") from None
    return preparadas


def calcular(conhecidas, desejadas):
    reagentes = preparar_linhas(conhecidas, True)
    produtos = preparar_linhas(desejadas, False)
    proporcao = min(item["razao"] for item in reagentes)
    limitantes = [item["formula"] for item in reagentes
                  if isclose(item["razao"], proporcao, rel_tol=TOLERANCIA, abs_tol=0)]

    for produto in produtos:
        mol = numero_calculado(proporcao * produto["coeficiente"])
        quantidade = mol * produto["massa_molar"] if produto["unidade"] == "g" else mol
        produto.update(mol=mol, quantidade=numero_calculado(quantidade))

    for reagente in reagentes:
        # A tolerância apenas elimina resíduos numéricos nas proporções empatadas.
        esgotado = reagente["formula"] in limitantes
        consumido_mol = reagente["mol"] if esgotado else min(reagente["mol"], proporcao * reagente["coeficiente"])
        restante_mol = max(0.0, reagente["mol"] - consumido_mol)
        fator = reagente["massa_molar"] if reagente["unidade"] == "g" else 1
        restante = min(reagente["quantidade"], restante_mol * fator)
        reagente.update(consumido_mol=consumido_mol, restante_mol=restante_mol,
                        restante=restante, consumido=reagente["quantidade"] - restante)

    return {"reagentes": reagentes, "produtos": produtos, "proporcao": proporcao,
            "limitantes": limitantes, "varios": len(reagentes) > 1,
            "proporcionais": len(limitantes) == len(reagentes)}
