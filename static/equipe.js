"use strict";

const janelaEquipe = document.getElementById("sobre-equipe");
const abrirEquipe = document.getElementById("abrir-equipe");

abrirEquipe.addEventListener("click", () => {
    janelaEquipe.showModal();
});

janelaEquipe.addEventListener("close", () => {
    abrirEquipe.focus();
});
