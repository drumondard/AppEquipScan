let currentData = { id_registro: "", gcs_url: "" };
let selCache = null;

function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const preview = document.getElementById('preview');
        const container = document.getElementById('previewContainer');
        
        reader.onload = e => { 
            preview.src = e.target.result; 
            container.style.display = 'block'; // Garante que o div pai apareça
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function enviarFoto() {
    const btn = document.getElementById('btnAna');
    btn.innerText = "Processando..."; btn.disabled = true;
    const formData = new FormData();
    formData.append('file', document.getElementById('fileInput').files[0]);
    
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const result = await res.json();
    
    if (result.error) { alert("Erro: " + result.error); btn.innerText = "Analisar"; btn.disabled = false; return; }

    const d = typeof result.dados === 'string' ? JSON.parse(result.dados) : result.dados;
    currentData = { id_registro: result.id_registro, gcs_url: result.gcs_url };
    
    document.getElementById('out-modelo').innerText = d.modelo || '-';
    document.getElementById('out-hostname').innerText = d.hostname || '-';
    document.getElementById('out-fabricante').innerText = d.fabricante || '-';
    document.getElementById('out-serial').innerText = d.numero_serie || '-'; // Adicionado
    document.getElementById('out-funcao').innerText = d.funcao || '-';       // Adicionado
    
    document.getElementById('modelo').value = d.modelo || '';
    document.getElementById('serial_number').value = d.numero_serie || ''; // Adicionado
    document.getElementById('funcao').value = d.funcao || '';             // Adicionado

    document.getElementById('iaSection').style.display = 'block';
    document.getElementById('sapSection').style.display = 'block';
    btn.innerText = "Analisar com IA"; btn.disabled = false;
}

async function verificarSAP() {
    const res = await fetch('/verificar-sap', { method: 'POST', body: JSON.stringify({
        modelo: document.getElementById('modelo').value, 
        uf: document.getElementById('uf_input').value, 
        estacao: document.getElementById('est_input').value
    })});
    const result = await res.json();
    if (result.encontrados) {
        document.getElementById('listaCheck').style.display = 'block';
        document.getElementById('lista-matches').innerHTML = result.data.map(item => 
            `<div class="card-match" onclick="sel(this, '${JSON.stringify(item).replace(/"/g, '&quot;')}')">
                <strong>ID_SAP: ${item.equipamento}</strong> | <strong>Tipo: ${item.tipo_item}</strong> | <strong>Hostname: ${item.hostname}</strong>
            </div>
        `).join('');
    } else {
        document.getElementById('alertaSAP').style.display = 'block';
        document.getElementById('dataSection').style.display = 'block';
    }
}

function sel(el, data) {
    selCache = JSON.parse(data.replace(/&quot;/g, '"'));
    document.querySelectorAll('.card-match').forEach(c => c.classList.remove('match-selected'));
    el.classList.add('match-selected');
}

function confirmarMatch() {
    if (!selCache) return alert("Por favor, selecione um item da lista.");
    
    // Log para depurar o que o SAP está enviando
    console.log("Dados do SAP selecionado:", selCache);
    
    // Mapeamento correto: Garanta que os IDs do seu HTML são exatamente estes
    document.getElementById('ativo').value = selCache.equipamento || '';
    document.getElementById('hostname').value = selCache.hostname || '';
    document.getElementById('fabricante').value = selCache.fabricante || '';
    document.getElementById('modelo').value = selCache.modelo || '';
    document.getElementById('funcao').value = selCache.funcao || '';
    
    // Verifique se o campo no SAP se chama 'num_serie' ou 'serial_number'
    document.getElementById('serial_number').value = selCache.num_serie || selCache.serial_number || '';
    
    document.getElementById('listaCheck').style.display = 'none';
    document.getElementById('dataSection').style.display = 'block';
    
    alert("Dados do SAP carregados!");
}

// Salva dados e limpa a tela
async function salvarDados() {
    const payload = {
        id_registro: currentData.id_registro,
        gcs_url: currentData.gcs_url,
        idsap: document.getElementById('ativo').value,
        hostname: document.getElementById('hostname').value,
        fabricante: document.getElementById('fabricante').value,
        modelo: document.getElementById('modelo').value,
        funcao: document.getElementById('funcao').value,
        serial_number: document.getElementById('serial_number').value,
        uf: document.getElementById('uf_input').value,
        estacao: document.getElementById('est_input').value
    };

    const res = await fetch('/salvar', { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(payload) 
    });

    if(res.ok) {
        alert("Inventário registrado com sucesso!");
        limparTela();
    } else {
        alert("Erro ao salvar dados no BigQuery.");
    }
}

// Limpa todos os campos e estados da interface
function limparTela() {
    document.getElementById('iaSection').style.display = 'none';
    document.getElementById('sapSection').style.display = 'none';
    document.getElementById('listaCheck').style.display = 'none';
    document.getElementById('dataSection').style.display = 'none';
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('alertaSAP').style.display = 'none';

    document.getElementById('fileInput').value = "";
    document.querySelectorAll('input[type="text"], input[type="hidden"]').forEach(i => i.value = "");
    document.querySelectorAll('.ia-badge-value').forEach(el => el.innerText = "-");
    
    currentData = { id_registro: "", gcs_url: "" };
    selCache = null;
}