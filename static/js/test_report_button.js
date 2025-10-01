// Script de teste para forçar a exibição do botão de relatório por data
console.log('🔧 Executando script de teste para botão de relatório');

// Aguardar um pouco para garantir que a página carregou
setTimeout(() => {
    // Verificar se o container de filtros existe
    const filtersContainer = document.getElementById('filtersContainer');
    if (filtersContainer) {
        console.log('✅ Container de filtros encontrado');
        
        // Forçar exibição do container
        filtersContainer.style.display = 'block';
        filtersContainer.style.visibility = 'visible';
        filtersContainer.style.opacity = '1';
        
        // Procurar o botão de relatório por data
        const reportBtn = filtersContainer.querySelector('button[onclick="showReportByDateModal()"]');
        if (reportBtn) {
            console.log('✅ Botão de relatório encontrado:', reportBtn);
            
            // Forçar estilo do botão
            reportBtn.style.display = 'inline-block';
            reportBtn.style.backgroundColor = '#e74c3c';
            reportBtn.style.color = 'white';
            reportBtn.style.border = '2px solid #ff0000';
            reportBtn.style.padding = '8px 12px';
            reportBtn.style.borderRadius = '4px';
            reportBtn.style.cursor = 'pointer';
            reportBtn.style.fontWeight = 'bold';
            
            console.log('✅ Estilo do botão aplicado');
        } else {
            console.error('❌ Botão de relatório não encontrado no container');
            
            // Tentar encontrar em qualquer lugar da página
            const allBtns = document.querySelectorAll('button');
            console.log(`🔍 Total de botões na página: ${allBtns.length}`);
            
            allBtns.forEach((btn, index) => {
                if (btn.textContent.includes('Gerar Relatório')) {
                    console.log(`✅ Botão encontrado no índice ${index}:`, btn);
                    btn.style.backgroundColor = '#ff0000';
                    btn.style.display = 'block';
                }
            });
        }
    } else {
        console.error('❌ Container de filtros não encontrado');
        
        // Tentar adicionar o botão diretamente em algum lugar visível
        const body = document.body;
        const testBtn = document.createElement('button');
        testBtn.textContent = '🔧 TESTE: Gerar Relatório por Data';
        testBtn.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #e74c3c;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            z-index: 9999;
            font-size: 14px;
        `;
        testBtn.onclick = function() {
            if (typeof showReportByDateModal === 'function') {
                showReportByDateModal();
            } else {
                alert('Função showReportByDateModal não encontrada');
            }
        };
        body.appendChild(testBtn);
        console.log('✅ Botão de teste adicionado');
    }
}, 2000);

// Também executar imediatamente
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM carregado, verificando botão...');
    
    const btn = document.querySelector('button[onclick="showReportByDateModal()"]');
    if (btn) {
        console.log('✅ Botão encontrado no DOM:', btn);
        btn.style.backgroundColor = '#ff0000';
        btn.style.display = 'block';
    } else {
        console.log('❌ Botão não encontrado no DOM');
    }
});
