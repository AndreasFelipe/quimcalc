"use strict";

const formulario = document.getElementById("formulario-solucoes");
const campos = document.getElementById("campos-solucoes");
const solido = document.getElementById("modo-solido");
const diluicao = document.getElementById("modo-diluicao");
const resultado = document.getElementById("resultado");

function atualizarModo() {
    const usarSolido = formulario.elements.modo.value === "solido";
    solido.hidden = solido.disabled = !usarSolido;
    diluicao.hidden = diluicao.disabled = usarSolido;
}

formulario.addEventListener("change", (evento) => {
    if (evento.target.name === "modo") atualizarModo();
    resultado.textContent = "Dados alterados. Clique em Calcular.";
});

formulario.addEventListener("input", () => {
    resultado.textContent = "Dados alterados. Clique em Calcular.";
});

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (campos.disabled) return;
    const dados = new URLSearchParams(new FormData(formulario));
    campos.disabled = true;
    resultado.setAttribute("aria-busy", "true");
    resultado.textContent = "Calculando...";
    try {
        const resposta = await fetch(formulario.action, { method: "POST", body: dados });
        if (resposta.status >= 500) throw new Error("Falha no servidor");
        const conteudo = await resposta.text();
        if (resposta.ok) resultado.innerHTML = conteudo;
        else resultado.textContent = conteudo;
    } catch {
        resultado.textContent = "Não foi possível receber a resposta. Tente novamente.";
    } finally {
        campos.disabled = false;
        resultado.setAttribute("aria-busy", "false");
    }
});

atualizarModo();
