// GLOBALS
const URL_API_VOZES = "/vozes";
const URL_API_DIRETA = "/gerar_narracao";

let ideiasGlobais = [];
let srtGlobal = "";
let vozSelecionada = "pt-BR-AntonioNeural";
let vozesData = [];
let arquivoVozMixer = null;
let arquivoBgMixer = null;

window.onload = async function() {
    mudarAba('aba_reescritor', document.getElementById('btn_menu_reescritor'));
    aplicarPresetMixer();
    configurarDragAndDropLegends();
    configurarDragAndDropMixer('dropzone_mixer_voz', 'arquivo_mixer_voz', 'nome_mixer_voz', 'icone_mixer_voz');
    configurarDragAndDropMixer('dropzone_mixer_bg', 'arquivo_mixer_bg', 'nome_mixer_bg', 'icone_mixer_bg');
    
    try {
        const resposta = await fetch(URL_API_VOZES);
        const dados = await resposta.json();

        // BLINDAGEM: backend pode retornar lista direta OU objeto { vozes: [...] }
        if (Array.isArray(dados)) {
            vozesData = dados;
        } else if (dados && Array.isArray(dados.vozes)) {
            vozesData = dados.vozes;
        } else if (dados && Array.isArray(dados.data)) {
            vozesData = dados.data;
        } else if (dados && Array.isArray(dados.items)) {
            vozesData = dados.items;
        } else if (dados && Array.isArray(dados.result)) {
            vozesData = dados.result;
        } else {
            vozesData = [];
        }

        renderizarListaVozes();
    } catch (error) {
        console.log("Erro ao carregar vozes:", error);
        const lista = document.getElementById("lista_vozes");
        if (lista) {
            lista.innerHTML = "<div class='text-red-400 text-sm'>Falha ao carregar vozes. Recarregue a página.</div>";
        }
    }
};

// ==========================================
// CONTROLES DE UI (ABAS E NAVEGAÇÃO)
// ==========================================
function mudarAba(abaId, botaoAtivo) {
    document.querySelectorAll('.aba').forEach(aba => aba.classList.add('hidden'));
    document.getElementById(abaId).classList.remove('hidden');

    document.querySelectorAll('.menu-item').forEach(btn => btn.classList.remove('menu-item-active'));
    if (botaoAtivo) botaoAtivo.classList.add('menu-item-active');
}

// ==========================================
// VOICE SYNTH - LISTA DE VOZES
// ==========================================
function renderizarListaVozes() {
    const container = document.getElementById("lista_vozes");
    if (!container) return;

    container.innerHTML = "";

    if (!Array.isArray(vozesData) || vozesData.length === 0) {
        container.innerHTML = "<div class='text-gray-400 text-sm'>Nenhuma voz encontrada.</div>";
        return;
    }

    // Filtra só pt-BR se quiser (pode comentar se quiser tudo)
    const vozesPT = vozesData.filter(v => (v.Locale || "").toLowerCase() === "pt-br");

    const listaParaMostrar = vozesPT.length > 0 ? vozesPT : vozesData;

    listaParaMostrar.forEach(v => {
        const short = v.ShortName || v.shortName || v.Name || v.name || "Voz";
        const friendly = v.FriendlyName || v.friendlyName || short;
        const gender = v.Gender || v.gender || "";
        const locale = v.Locale || v.locale || "";

        const card = document.createElement("div");
        card.className = "voice-card";
        card.onclick = () => selecionarVoz(short);

        card.innerHTML = `
            <div class="voice-card-title">${friendly}</div>
            <div class="voice-card-sub">${short}</div>
            <div class="voice-card-meta">${locale} ${gender ? "• " + gender : ""}</div>
        `;

        // marca selecionado
        if (short === vozSelecionada) {
            card.classList.add("voice-card-active");
        }

        container.appendChild(card);
    });
}

function selecionarVoz(shortName) {
    vozSelecionada = shortName;
    renderizarListaVozes();
}

// ==========================================
// VOICE SYNTH - GERAR NARRAÇÃO
// ==========================================
async function sintetizarVoz() {
    const texto = document.getElementById("texto_narracao").value.trim();
    if (!texto) return alert("Cole um texto para narrar.");

    const velocidade = document.getElementById("velocidade").value;
    const pitch = document.getElementById("pitch").value;

    const payload = {
        texto: texto,
        voz: vozSelecionada,
        velocidade: velocidade,
        pitch: pitch
    };

    try {
        const res = await fetch(URL_API_DIRETA, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Erro ao sintetizar voz.");

        // ajuste conforme seu backend retornar (audio_url / base64 etc.)
        // aqui deixo genérico:
        console.log("Resposta TTS:", data);
        alert("Narração gerada! (ver console / implemente player conforme retorno)");

    } catch (err) {
        console.error(err);
        alert("Erro ao sintetizar: " + err.message);
    }
}

// ==========================================
// MINER (ENDPOINT RELATIVO)
// ==========================================
async function minerarConteudo(fonte) {
    let url = "/miner/" + fonte;

    try {
        const res = await fetch(url);
        const data = await res.json();
        console.log("Miner:", data);
    } catch (e) {
        console.error("Erro miner:", e);
    }
}

// ==========================================
// AUDIO MIXER (ENDPOINT RELATIVO)
// ==========================================
function aplicarPresetMixer() {
    // Presets/valores iniciais do mixer (se você já usa)
}

function configurarDragAndDropMixer(dropzoneId, inputId, nomeId, iconeId) {
    const dropzone = document.getElementById(dropzoneId);
    const input = document.getElementById(inputId);
    const nomeArquivo = document.getElementById(nomeId);
    const icone = document.getElementById(iconeId);

    if (!dropzone || !input) return;

    dropzone.addEventListener("click", () => input.click());

    input.addEventListener("change", () => {
        if (input.files && input.files[0]) {
            nomeArquivo.textContent = input.files[0].name;
            if (icone) icone.classList.remove("hidden");

            if (inputId === "arquivo_mixer_voz") arquivoVozMixer = input.files[0];
            if (inputId === "arquivo_mixer_bg") arquivoBgMixer = input.files[0];
        }
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dropzone-active");
    });

    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dropzone-active"));

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dropzone-active");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            input.files = e.dataTransfer.files;
            nomeArquivo.textContent = e.dataTransfer.files[0].name;
            if (icone) icone.classList.remove("hidden");

            if (inputId === "arquivo_mixer_voz") arquivoVozMixer = e.dataTransfer.files[0];
            if (inputId === "arquivo_mixer_bg") arquivoBgMixer = e.dataTransfer.files[0];
        }
    });
}

async function processarMixer() {
    if (!arquivoVozMixer || !arquivoBgMixer) {
        return alert("Envie o áudio da voz e o áudio do BG.");
    }

    const formData = new FormData();
    formData.append("voz", arquivoVozMixer);
    formData.append("bg", arquivoBgMixer);

    try {
        const res = await fetch("/audio_mixer", { method: 'POST', body: formData });
        const data = await res.json();
        console.log("Mixer:", data);
    } catch (e) {
        console.error("Erro mixer:", e);
    }
}

// ==========================================
// GEN LEGENDS (ENDPOINT RELATIVO)
// ==========================================
function configurarDragAndDropLegends() {
    // se já tiver
}

async function gerarLegends() {
    const inputFile = document.getElementById("arquivo_legends");
    if (!inputFile || !inputFile.files || !inputFile.files[0]) {
        return alert("Envie um arquivo para gerar legends.");
    }

    const formData = new FormData();
    formData.append("arquivo", inputFile.files[0]);

    try {
        const res = await fetch("/gen_legends", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        console.log("Legends:", data);
    } catch (e) {
        console.error("Erro legends:", e);
    }
}

// ==========================================
// BOTÕES (se seus HTML chamam funções direto)
// ==========================================
window.sintetizarVoz = sintetizarVoz;
window.processarMixer = processarMixer;
window.gerarLegends = gerarLegends;
window.minerarConteudo = minerarConteudo;
