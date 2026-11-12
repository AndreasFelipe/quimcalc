from flask import Flask, Response, request, render_template
from logica.consulta import consultar
from logica.analise import analisar
from logica.solucoes import calcular_solucao
from logica.estequiometria import MAX_LINHAS, calcular, ler_linhas

from dados.nomes import NOMES
from dados.nomes import simbolo_nome


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096


@app.get('/solucoes')
def pagina_solucoes():
    return render_template("solucoes.html")


@app.post('/calcular-solucoes')
def renderizar_solucoes():
    try:
        dados = calcular_solucao(request.form)
    except ValueError as erro:
        return Response(str(erro), status=400, mimetype="text/plain")
    return render_template("resultado_solucoes.html", **dados)


@app.template_filter("medida")
def formatar_medida(valor, casas=4):
    if valor == 0:
        return "0"
    if abs(valor) < 10 ** -casas or abs(valor) >= 1e9:
        return format(valor, ".4e").replace(".", ",")
    texto = format(valor, f".{casas}f")
    if casas != 2:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")


@app.get('/estequiometria')
def pagina_estequiometria():
    return render_template("estequiometria.html", max_linhas=MAX_LINHAS)


@app.post('/calcular-estequiometria')
def renderizar_estequiometria():
    request.max_content_length = 32768
    try:
        conhecidas = ler_linhas(request.form, "conhecida", True)
        desejadas = ler_linhas(request.form, "desejada", False)
        dados = calcular(conhecidas, desejadas)
    except ValueError as erro:
        return Response(str(erro), status=400, mimetype="text/plain")
    return render_template("resultado_estequiometria.html", **dados)


@app.template_filter("numero")
def formatar_numero(valor):
    return format(valor, ".10g").replace(".", ",")


@app.get('/analise')
def pagina_analise():
    return render_template("analise.html")


@app.post('/analisar')
def renderizar_analise():
    try:
        dados = analisar(request.form.get("formula", ""))
    except ValueError as e:
        return Response(str(e), status=400, mimetype="text/plain")
    except RecursionError:
        return Response("A fórmula contém níveis demais de parênteses. Simplifique os grupos.", status=400, mimetype="text/plain")

    return render_template("resultado_analise.html", **dados, nome=simbolo_nome)


@app.post("/consultar")
def renderizar_consulta():
    try:
        simbolo, nome, propriedades = consultar(request.form.get("consulta", '').strip())
    except ValueError as e:
        return Response(str(e), status=404,mimetype="text/plain")

    return render_template("resultado_consulta.html", simbolo=simbolo, nome=nome, propriedades=propriedades)


@app.get('/')
def inicio():
    return render_template("inicio.html")


@app.get('/elementos')
def index():
    return render_template("index.html", nomes=NOMES)


@app.errorhandler(413)
def entrada_muito_grande(erro):
    return Response("A consulta é muito grande.", status=413, mimetype="text/plain")


if __name__ == "__main__":
    app.run()
