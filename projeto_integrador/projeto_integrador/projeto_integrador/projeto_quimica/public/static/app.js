"use strict";

const formulario = document.getElementById("formulario");
const campo = formulario.querySelector("input");
const resultado = document.getElementById("resultado");
const botao = document.getElementById("botao");
const lista = document.getElementById("lista-elementos");
const painel = document.getElementById("painel");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (botao.disabled) return;

    const origem = evento.submitter;
    const valor = origem?.name === campo.name ? origem.value : campo.value;
    campo.value = valor;

    botao.disabled = true;
    if (lista) lista.disabled = true;
    resultado.textContent = "Processando...";

    try {
        const resposta = await fetch(formulario.action, {
            method: "POST",
            body: new URLSearchParams({ [campo.name]: valor }),
        });

        if (resposta.status >= 500) throw new Error("Falha no servidor");

        const conteudo = await resposta.text();

        if (resposta.ok) {
            resultado.innerHTML = conteudo;
            if (painel) painel.open = false;
        }
        else
            resultado.textContent = conteudo;
    } catch {
        resultado.textContent = "Não foi possível receber a resposta. Tente novamente.";
    } finally {
        botao.disabled = false;
        if (lista) lista.disabled = false;
    }
});
