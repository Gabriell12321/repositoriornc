// Script de diagnóstico para debugar botão de impressão
// Salve este arquivo como debug_print_button.js

// Adicionar este script à página dashboard_improved.html
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Iniciando diagnóstico do botão de impressão');
    
    // Verificar se o botão existe
    const printBtn = document.getElementById('printReportBtn');
    if (!printBtn) {
        console.error('❌ Botão de impressão não encontrado no DOM!');
    } else {
        console.log('✅ Botão de impressão encontrado no DOM');
        
        // Verificar propriedades de estilo
        const computedStyle = window.getComputedStyle(printBtn);
        console.log('📊 Estilo do botão:', {
            display: computedStyle.display,
            visibility: computedStyle.visibility,
            opacity: computedStyle.opacity,
            position: computedStyle.position,
            width: computedStyle.width,
            height: computedStyle.height,
            zIndex: computedStyle.zIndex
        });
        
        // Forçar visibilidade
        printBtn.style.display = 'flex';
        printBtn.style.visibility = 'visible';
        printBtn.style.opacity = '1';
        printBtn.style.position = 'relative';
        printBtn.style.zIndex = '999';
        printBtn.style.backgroundColor = '#FF0000';
        printBtn.innerHTML = '🖨️ Imprimir Relatório (DEBUG)';
        
        console.log('🔧 Aplicadas propriedades de visibilidade forçada');
        
        // Verificar o modal
        const printModal = document.getElementById('printReportModal');
        if (!printModal) {
            console.error('❌ Modal de impressão não encontrado!');
        } else {
            console.log('✅ Modal de impressão encontrado');
        }
        
        // Verificar a função de exibição
        if (typeof showPrintReportModal !== 'function') {
            console.error('❌ Função showPrintReportModal não definida!');
        } else {
            console.log('✅ Função showPrintReportModal definida');
        }
    }
    
    // Adicionar botão de diagnóstico
    const diagBtn = document.createElement('button');
    diagBtn.textContent = '🛠️ Teste Impressão';
    diagBtn.style.position = 'fixed';
    diagBtn.style.bottom = '20px';
    diagBtn.style.right = '20px';
    diagBtn.style.zIndex = '9999';
    diagBtn.style.padding = '10px';
    diagBtn.style.background = '#007bff';
    diagBtn.style.color = 'white';
    diagBtn.style.border = 'none';
    diagBtn.style.borderRadius = '5px';
    diagBtn.style.cursor = 'pointer';
    
    diagBtn.onclick = function() {
        console.log('🖱️ Botão de diagnóstico clicado');
        if (typeof showPrintReportModal === 'function') {
            showPrintReportModal();3
            console.log('🔍 Função showPrintReportModal chamada');
        } else {
            console.error('❌ Impossível chamar showPrintReportModal - não definida');
            
            // Tentar abrir modal diretamente
            const modal = document.getElementById('printReportModal');
            if (modal) {
                modal.style.display = 'flex';
                console.log('🔍 Modal aberto diretamente via style.display');
            }
        }
    };
    
    document.body.appendChild(diagBtn);
    console.log('✅ Botão de diagnóstico adicionado');
});
