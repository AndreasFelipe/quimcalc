"use strict";

const formulario = document.getElementById("formulario-estequiometria");
const campos = document.getElementById("campos-estequiometria");
const resultado = document.getElementById("resultado");
const aviso = document.getElementById("aviso-linhas");
const grupos = {
    conhecida: document.getElementById("conhecidas"),
    desejada: document.getElementById("desejadas"),
};

function numerarLinhas() {
    for (const [grupo, container] of Object.entries(grupos)) {
        container.querySelectorAll("[data-linha]").forEach((linha, indice) => {
            const nome = `${grupo === "conhecida" ? "Reagente" : "Produto"} ${indice + 1}`;
            linha.querySelector("legend").textContent = nome;
            const remover = linha.querySelector("[data-remover]");
            if (remover) remover.setAttribute("aria-label", `Remover ${nome.toLowerCase()}`);
        });
    }
}

formulario.addEventListener("click", (evento) => {
    const adicionar = evento.target.closest("[data-adicionar]");
    const remover = evento.target.closest("[data-remover]");
    if (adicionar) {
        const grupo = adicionar.dataset.adicionar;
        const container = grupos[grupo];
        if (container.children.length >= Number(formulario.dataset.maxLinhas)) {
            aviso.textContent = `Use até ${formulario.dataset.maxLinhas} substâncias por seção.`;
            return;
        }
        const modelo = document.getElementById(`linha-${grupo}`);
        container.append(modelo.content.cloneNode(true));
        container.lastElementChild.querySelector("input").focus();
    } else if (remover) {
        const linha = remover.closest("[data-linha]");
        const anterior = linha.previousElementSibling;
        if (!anterior) return;
        linha.remove();
        anterior.querySelector("input").focus();
    } else {
        return;
    }
    aviso.textContent = "";
    resultado.textContent = "Dados alterados. Clique em Calcular.";
    numerarLinhas();
});

formulario.addEventListener("input", () => {
    resultado.textContent = "Dados alterados. Clique em Calcular.";
});

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (campos.disabled) return;
    // Os dados precisam ser coletados antes de desabilitar os campos.
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

numerarLinhas();
