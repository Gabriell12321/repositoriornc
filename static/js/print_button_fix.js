/**
 * Solução para botão de impressão no dashboard
 * Este script garante que o botão de impressão esteja visível e funcionando
 */

// Auto-executar quando a página carregar
(function() {
    // Esperar DOM estar pronto
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🔄 Script de correção do botão de impressão iniciado');
        
        // Adicionar botão direto na seção de ações rápidas
        setTimeout(adicionarBotaoImpressao, 500);
        
        // Tentar novamente após 2 segundos (caso o DOM ainda não esteja pronto)
        setTimeout(adicionarBotaoImpressao, 2000);
    });
    
    function adicionarBotaoImpressao() {
        // Verificar se o botão já existe
        if (document.getElementById('printReportBtnFixed')) {
            return;
        }
        
        // Buscar o container de ações rápidas
        const actionsHeading = Array.from(document.querySelectorAll('.right-section h3')).find(h => 
            h.textContent.includes('⚡ Ações Rápidas'));
        
        let actionsContainer = null;
        if (actionsHeading) {
            actionsContainer = actionsHeading.parentNode.querySelector('div');
        }
        
        if (!actionsContainer) {
            console.error('❌ Container de ações rápidas não encontrado');
            
            // Tentar encontrar qualquer div na seção direita
            const rightSection = document.querySelector('.right-section');
            if (rightSection) {
                const divs = rightSection.querySelectorAll('div');
                if (divs.length > 0) {
                    divs[0].appendChild(criarBotaoImpressao());
                    console.log('✅ Botão adicionado à primeira div disponível');
                }
            }
            return;
        }
        
        // Adicionar o botão ao container
        actionsContainer.appendChild(criarBotaoImpressao());
        console.log('✅ Botão de impressão adicionado às ações rápidas');
    }
    
    function criarBotaoImpressao() {
        const btn = document.createElement('button');
        btn.id = 'printReportBtnFixed';
        btn.innerHTML = '🖨️ Imprimir Relatório';
        btn.style.cssText = `
            padding: 10px 15px;
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
            transition: transform .15s ease, box-shadow .15s ease;
        `;
        
        // Adicionar efeito hover
        btn.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 6px 20px rgba(231,76,60,.4)';
        });
        
        btn.addEventListener('mouseout', function() {
            this.style.transform = '';
            this.style.boxShadow = '0 4px 15px rgba(231,76,60,.3)';
        });
        
        // Adicionar evento click
        btn.addEventListener('click', function() {
            if (typeof showPrintReportModal === 'function') {
                showPrintReportModal();
            } else {
                const modal = document.getElementById('printReportModal');
                if (modal) {
                    modal.style.display = 'flex';
                } else {
                    alert('Erro: Modal de impressão não encontrado');
                }
            }
        });
        
        return btn;
    }
    
})();
            const parts = selector.split(':contains');
            const baseSelector = parts[0];
            const text = parts[1].replace(/['"()]/g, '').trim();
            
            const elements = document.querySelectorAll(baseSelector);
            const results = [];
            
            for (let i = 0; i < elements.length; i++) {
                if (elements[i].textContent.includes(text)) {
                    results.push(elements[i]);
                }
            }
            
            return results;
        }
        
        return document.querySelectorAll(selector);
    };
})();
