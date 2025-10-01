/**
 * Solução definitiva para o botão de impressão
 * Este script injeta um botão de impressão no dashboard independente do HTML original
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando script de injeção do botão de impressão');
    
    // Aguardar o carregamento completo da página
    setTimeout(injetarBotaoImpressao, 1000);
    
    function injetarBotaoImpressao() {
        console.log('🔍 Procurando seção para injetar botão...');
        
        // Tentar encontrar a seção direita do dashboard
        const rightSection = document.querySelector('.right-section');
        if (!rightSection) {
            console.error('❌ Seção direita não encontrada, tentando novo selector...');
            injetarNaQualquerDiv();
            return;
        }
        
        // Criar botão
        const btn = document.createElement('button');
        btn.id = 'printReportBtnInjected';
        btn.innerHTML = '🖨️ Imprimir Relatório RNC';
        btn.style.cssText = `
            padding: 12px 16px;
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: calc(100% - 20px);
            margin: 15px 10px;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
            transition: transform .15s ease, box-shadow .15s ease;
        `;
        
        // Adicionar efeitos hover
        btn.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 6px 20px rgba(231,76,60,.4)';
        });
        
        btn.addEventListener('mouseout', function() {
            this.style.transform = '';
            this.style.boxShadow = '0 4px 15px rgba(231,76,60,.3)';
        });
        
        // Adicionar evento de clique
        btn.addEventListener('click', function() {
            console.log('🖱️ Botão de impressão clicado');
            abrirModalImpressao();
        });
        
        // Inserir no início da seção direita
        if (rightSection.firstChild) {
            rightSection.insertBefore(btn, rightSection.firstChild);
        } else {
            rightSection.appendChild(btn);
        }
        
        console.log('✅ Botão de impressão injetado com sucesso na seção direita');
    }
    
    function injetarNaQualquerDiv() {
        // Encontrar qualquer div na página que possa conter o botão
        const divs = document.querySelectorAll('div');
        if (divs.length > 0) {
            // Procurar por uma div que parece um container de ações
            for (let i = 0; i < divs.length; i++) {
                const div = divs[i];
                if (div.querySelector('button') || div.querySelector('h3')) {
                    // Criar o botão
                    const btn = document.createElement('button');
                    btn.id = 'printReportBtnInjected';
                    btn.innerHTML = '🖨️ Imprimir Relatório (Alt)';
                    btn.style.cssText = `
                        padding: 12px 16px;
                        background: linear-gradient(135deg, #e74c3c, #c0392b);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 15px;
                        display: block;
                        width: 100%;
                        margin: 10px 0;
                        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                    `;
                    
                    // Adicionar evento de clique
                    btn.addEventListener('click', function() {
                        console.log('🖱️ Botão alternativo de impressão clicado');
                        abrirModalImpressao();
                    });
                    
                    div.appendChild(btn);
                    console.log('✅ Botão alternativo de impressão injetado');
                    return;
                }
            }
            
            // Se não encontrar nenhum container adequado, injetar no body
            injetarBotaoFlutuante();
        }
    }
    
    function injetarBotaoFlutuante() {
        const btn = document.createElement('button');
        btn.id = 'printReportBtnFloating';
        btn.innerHTML = '🖨️ Imprimir RNC';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 20px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            z-index: 9999;
        `;
        
        btn.addEventListener('click', function() {
            console.log('🖱️ Botão flutuante de impressão clicado');
            abrirModalImpressao();
        });
        
        document.body.appendChild(btn);
        console.log('✅ Botão flutuante de impressão injetado');
    }
    
    function abrirModalImpressao() {
        // Tentar usar a função existente
        if (typeof window.showPrintReportModal === 'function') {
            window.showPrintReportModal();
            console.log('✅ Modal aberto via função showPrintReportModal');
            return;
        }
        
        // Se a função não existir, tentar abrir o modal diretamente
        const modal = document.getElementById('printReportModal');
        if (modal) {
            modal.style.display = 'flex';
            console.log('✅ Modal aberto diretamente via style.display');
            return;
        }
        
        // Se o modal não existir, criar um modal básico
        criarModalImpressao();
    }
    
    function criarModalImpressao() {
        console.log('🔧 Criando modal de impressão alternativo');
        
        // Criar overlay do modal
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';
        modalOverlay.id = 'printReportModalAlternative';
        modalOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        
        // Criar conteúdo do modal
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        `;
        
        // Adicionar título
        const modalTitle = document.createElement('h3');
        modalTitle.textContent = 'Imprimir Relatório RNC';
        modalTitle.style.cssText = `
            margin-top: 0;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        `;
        
        // Adicionar formulário
        const form = document.createElement('form');
        form.action = '/print_rnc_report';
        form.method = 'post';
        form.target = '_blank';
        
        // Adicionar seleção de formato
        const formatLabel = document.createElement('label');
        formatLabel.textContent = 'Formato do Relatório:';
        formatLabel.style.cssText = `
            display: block;
            margin: 15px 0 5px;
            font-weight: bold;
        `;
        
        const formatSelect = document.createElement('select');
        formatSelect.name = 'format';
        formatSelect.style.cssText = `
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
        `;
        
        // Opções de formato
        const formats = [
            {value: 'detailed', text: 'Detalhado - Todas as informações'},
            {value: 'summary', text: 'Resumido - Informações principais'},
            {value: 'charts', text: 'Gráficos - Visualização estatística'}
        ];
        
        formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.value;
            option.textContent = format.text;
            formatSelect.appendChild(option);
        });
        
        // Botões
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
        `;
        
        const cancelButton = document.createElement('button');
        cancelButton.type = 'button';
        cancelButton.textContent = 'Cancelar';
        cancelButton.style.cssText = `
            padding: 8px 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        `;
        cancelButton.addEventListener('click', function() {
            document.body.removeChild(modalOverlay);
        });
        
        const printButton = document.createElement('button');
        printButton.type = 'submit';
        printButton.textContent = 'Imprimir';
        printButton.style.cssText = `
            padding: 8px 15px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        `;
        
        // Montar o formulário
        form.appendChild(formatLabel);
        form.appendChild(formatSelect);
        buttonContainer.appendChild(cancelButton);
        buttonContainer.appendChild(printButton);
        form.appendChild(buttonContainer);
        
        // Montar o modal
        modalContent.appendChild(modalTitle);
        modalContent.appendChild(form);
        modalOverlay.appendChild(modalContent);
        
        // Adicionar ao body
        document.body.appendChild(modalOverlay);
        
        console.log('✅ Modal alternativo criado e exibido');
    }
});
