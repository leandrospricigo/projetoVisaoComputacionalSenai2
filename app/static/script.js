/**
 * SupermarketVision AI - Frontend Controller
 * Gerencia o upload de imagens, comunicação com o endpoint POST /detect e
 * renderização das caixas delimitadoras e rótulos no elemento Canvas.
 */

// Mapeamento de cores vibrantes para cada classe de supermercado
const CLASS_COLORS = {
    apple: '#ef4444',       // Vermelho
    banana: '#facc15',      // Amarelo
    orange: '#f97316',      // Laranja
    carrot: '#fb923c',      // Cenoura
    broccoli: '#22c55e',    // Verde
    bottle: '#06b6d4',      // Ciano
    cup: '#3b82f6',         // Azul
    sandwich: '#d97706',    // Castanho/Dourado
    pizza: '#ea580c',       // Laranja escuro
    donut: '#ec4899',       // Rosa
    cake: '#a855f7',        // Roxo
    bowl: '#14b8a6',        // Verde-água
    default: '#38bdf8'      // Azul claro padrão
};

// Estado da aplicação
let currentFile = null;
let currentImage = null;
let lastApiResponse = null;

// Elementos da DOM
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const btnDetect = document.getElementById('btn-detect');
const btnSpinner = document.getElementById('btn-spinner');
const canvas = document.getElementById('detection-canvas');
const ctx = canvas.getContext('2d');
const emptyState = document.getElementById('empty-state');
const jsonCode = document.getElementById('json-code');

const metricStatus = document.getElementById('metric-status');
const metricTime = document.getElementById('metric-time');
const metricCount = document.getElementById('metric-count');

const tabVisual = document.getElementById('tab-visual');
const tabJson = document.getElementById('tab-json');
const contentVisual = document.getElementById('content-visual');
const contentJson = document.getElementById('content-json');

const chipsContainer = document.getElementById('chips-container');
const chipsList = document.getElementById('chips-list');
const btnDownload = document.getElementById('btn-download');
const btnCopyJson = document.getElementById('btn-copy-json');

// --- EVENTOS DE UPLOAD E DROPZONE ---

dropzone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
    }
});

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

// Suporte para botões de amostra rápida
document.querySelectorAll('.sample-pill').forEach((pill) => {
    pill.addEventListener('click', async () => {
        document.querySelectorAll('.sample-pill').forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');

        const src = pill.getAttribute('data-src');
        try {
            metricStatus.textContent = 'Carregando amostra...';
            const response = await fetch(src);
            const blob = await response.blob();
            const filename = src.split('/').pop();
            const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });
            handleFileSelect(file);
        } catch (err) {
            console.error('Erro ao carregar amostra:', err);
            alert('Não foi possível carregar a amostra.');
        }
    });
});

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione um arquivo de imagem válido (JPG, PNG ou WEBP).');
        return;
    }

    currentFile = file;
    btnDetect.disabled = false;
    metricStatus.textContent = 'Imagem Pronta';

    // Carrega a imagem para preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            currentImage = img;
            desenharImagemOriginal(img);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function desenharImagemOriginal(img) {
    emptyState.hidden = true;
    canvas.hidden = false;
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    // Reseta métricas
    metricCount.textContent = '0';
    chipsContainer.hidden = true;
    btnDownload.hidden = true;
    btnCopyJson.hidden = true;
}

// --- EXECUÇÃO DA INFERÊNCIA COM A API ---

btnDetect.addEventListener('click', async () => {
    if (!currentFile) return;

    // Estado visual de carregamento
    btnDetect.disabled = true;
    btnSpinner.hidden = false;
    metricStatus.textContent = 'Detectando...';
    metricStatus.className = 'metric-value text-highlight';

    const formData = new FormData();
    formData.append('file', currentFile);

    const startTime = performance.now();

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const endTime = performance.now();
        const latencyMs = Math.round(endTime - startTime);

        if (!response.ok) {
            const erroData = await response.json();
            throw new Error(erroData.detail || 'Erro na requisição');
        }

        const data = await response.json();
        lastApiResponse = data;

        // Atualiza métricas
        metricStatus.textContent = 'Sucesso';
        metricStatus.className = 'metric-value text-success';
        metricTime.textContent = `${latencyMs} ms`;
        metricCount.textContent = data.total_detections || 0;

        // Renderiza as bounding boxes na imagem
        desenharDeteccoes(data.detections || []);

        // Atualiza a visualização do JSON bruto
        jsonCode.textContent = JSON.stringify(data, null, 2);

        btnDownload.hidden = false;
        btnCopyJson.hidden = false;

    } catch (err) {
        console.error('Erro na inferência:', err);
        metricStatus.textContent = 'Erro';
        metricStatus.className = 'metric-value text-rose';
        alert(`Falha ao comunicar com a API: ${err.message}`);
    } finally {
        btnDetect.disabled = false;
        btnSpinner.hidden = true;
    }
});

// --- DESENHO DAS DETECÇÕES NO CANVAS ---

function desenharDeteccoes(detections) {
    if (!currentImage) return;

    // Redesenha a imagem base limpa
    canvas.width = currentImage.naturalWidth;
    canvas.height = currentImage.naturalHeight;
    ctx.drawImage(currentImage, 0, 0);

    chipsList.innerHTML = '';
    const classesEncontradas = new Set();

    detections.forEach((det) => {
        const { class_name, confidence, box } = det;
        const cor = CLASS_COLORS[class_name] || CLASS_COLORS.default;
        classesEncontradas.add(class_name);

        const { x_min, y_min, x_max, y_max } = box;
        const largura = x_max - x_min;
        const altura = y_max - y_min;

        // 1. Desenha o retângulo da bounding box
        ctx.strokeStyle = cor;
        ctx.lineWidth = Math.max(3, Math.round(canvas.width / 250));
        ctx.strokeRect(x_min, y_min, largura, altura);

        // 2. Prepara o texto do rótulo
        const porcentagem = Math.round(confidence * 100);
        const textoRotulo = `${class_name} ${porcentagem}%`;

        const fontSize = Math.max(14, Math.round(canvas.width / 40));
        ctx.font = `bold ${fontSize}px 'Plus Jakarta Sans', sans-serif`;
        const textMetrics = ctx.measureText(textoRotulo);
        const padding = 6;
        const labelWidth = textMetrics.width + (padding * 2);
        const labelHeight = fontSize + (padding * 2);

        // Posiciona a etiqueta acima da caixa (ou dentro se tocar a borda superior)
        let labelY = y_min - labelHeight;
        if (labelY < 0) labelY = y_min;

        // 3. Fundo da etiqueta com cantos arredondados simulados
        ctx.fillStyle = cor;
        ctx.fillRect(x_min, labelY, labelWidth, labelHeight);

        // 4. Texto da etiqueta
        ctx.fillStyle = '#ffffff';
        ctx.textBaseline = 'top';
        ctx.fillText(textoRotulo, x_min + padding, labelY + padding);
    });

    // Atualiza chips com as classes encontradas
    if (classesEncontradas.size > 0) {
        chipsContainer.hidden = false;
        classesEncontradas.forEach((cls) => {
            const cor = CLASS_COLORS[cls] || CLASS_COLORS.default;
            const chip = document.createElement('span');
            chip.className = 'detection-chip';
            chip.style.backgroundColor = `${cor}25`;
            chip.style.border = `1px solid ${cor}`;
            chip.style.color = cor;
            chip.textContent = cls.toUpperCase();
            chipsList.appendChild(chip);
        });
    } else {
        chipsContainer.hidden = true;
    }
}

// --- NAVEGAÇÃO ENTRE ABAS ---

tabVisual.addEventListener('click', () => {
    tabVisual.classList.add('active');
    tabJson.classList.remove('active');
    contentVisual.hidden = false;
    contentJson.hidden = true;
});

tabJson.addEventListener('click', () => {
    tabJson.classList.add('active');
    tabVisual.classList.remove('active');
    contentJson.hidden = false;
    contentVisual.hidden = true;
});

// --- DOWNLOAD E COPIAR JSON ---

btnDownload.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = `rotulado_${currentFile ? currentFile.name : 'deteccao.png'}`;
    link.href = canvas.toDataURL('image/png');
    link.click();
});

btnCopyJson.addEventListener('click', () => {
    if (!lastApiResponse) return;
    navigator.clipboard.writeText(JSON.stringify(lastApiResponse, null, 2)).then(() => {
        const textoOriginal = btnCopyJson.textContent;
        btnCopyJson.textContent = '✅ Copiado!';
        setTimeout(() => {
            btnCopyJson.textContent = textoOriginal;
        }, 2000);
    });
});
