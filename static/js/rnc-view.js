// JavaScript para melhorar a interatividade da visualização da RNC

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 RNC View Enhanced JavaScript carregado!');
    
    // Inicializar todas as funcionalidades
    initializeTooltips();
    initializeAnimations();
    initializeInteractiveElements();
    initializePrintEnhancements();
    initializeAccessibility();
    
    console.log('✅ Todas as funcionalidades foram inicializadas!');
});

// Sistema de tooltips avançado
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
    
    console.log(`🔍 ${tooltipElements.length} tooltips configurados`);
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'enhanced-tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.position = 'fixed';
    tooltip.style.top = rect.top - tooltipRect.height - 10 + 'px';
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltipRect.width / 2) + 'px';
    tooltip.style.zIndex = '10000';
    
    element.tooltipElement = tooltip;
    
    // Animar entrada
    setTimeout(() => tooltip.classList.add('show'), 10);
}

function hideTooltip(event) {
    const element = event.target;
    if (element.tooltipElement) {
        element.tooltipElement.classList.remove('show');
        setTimeout(() => {
            if (element.tooltipElement && element.tooltipElement.parentNode) {
                element.tooltipElement.parentNode.removeChild(element.tooltipElement);
            }
            element.tooltipElement = null;
        }, 200);
    }
}

// Sistema de animações avançado
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Adicionar delay baseado na posição
                const delay = Array.from(entry.target.parentNode.children).indexOf(entry.target) * 100;
                entry.target.style.animationDelay = `${delay}ms`;
            }
        });
    }, observerOptions);
    
    // Observar todos os elementos animáveis
    const animatableElements = document.querySelectorAll('.info-card, .signature-card, .status-card, .text-field');
    animatableElements.forEach(el => observer.observe(el));
    
    console.log(`🎬 ${animatableElements.length} elementos configurados para animação`);
}

// Sistema de elementos interativos
function initializeInteractiveElements() {
    // Melhorar cards de informação
    const infoCards = document.querySelectorAll('.info-card');
    infoCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('expanded');
            
            // Adicionar efeito de ripple
            createRippleEffect(this, event);
        });
        
        // Adicionar indicador de interatividade
        if (this.querySelector('.info-value').textContent.trim() !== 'Não informado') {
            this.classList.add('interactive');
        }
    });
    
    // Melhorar campos de texto
    const textFields = document.querySelectorAll('.text-field');
    textFields.forEach(field => {
        field.addEventListener('click', function() {
            this.classList.toggle('focused');
        });
    });
    
    // Melhorar status cards
    const statusCards = document.querySelectorAll('.status-card');
    statusCards.forEach(card => {
        card.addEventListener('click', function() {
            // Toggle visual state
            this.classList.toggle('user-selected');
        });
    });
    
    console.log('🖱️ Elementos interativos configurados');
}

// Efeito de ripple para cliques
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);
}

// Melhorias para impressão
function initializePrintEnhancements() {
    window.addEventListener('beforeprint', function() {
        document.body.classList.add('printing');
        
        // Preparar elementos para impressão
        prepareForPrint();
    });
    
    window.addEventListener('afterprint', function() {
        document.body.classList.remove('printing');
        
        // Restaurar elementos após impressão
        restoreAfterPrint();
    });
    
    console.log('🖨️ Melhorias de impressão configuradas');
}

function prepareForPrint() {
    // Adicionar classes para impressão
    document.body.classList.add('print-mode');
    
    // Ocultar elementos desnecessários para impressão
    const printHiddenElements = document.querySelectorAll('.print-controls, .btn');
    printHiddenElements.forEach(el => el.style.display = 'none');
    
    // Ajustar cores para impressão
    const colorElements = document.querySelectorAll('.rnc-header, .section-title i');
    colorElements.forEach(el => el.style.webkitPrintColorAdjust = 'exact');
}

function restoreAfterPrint() {
    // Remover classes de impressão
    document.body.classList.remove('print-mode');
    
    // Restaurar elementos
    const printHiddenElements = document.querySelectorAll('.print-controls, .btn');
    printHiddenElements.forEach(el => el.style.display = '');
    
    // Restaurar cores
    const colorElements = document.querySelectorAll('.rnc-header, .section-title i');
    colorElements.forEach(el => el.style.webkitPrintColorAdjust = '');
}

// Melhorias de acessibilidade
function initializeAccessibility() {
    // Adicionar navegação por teclado
    const interactiveElements = document.querySelectorAll('.info-card, .signature-card, .status-card, .text-field');
    
    interactiveElements.forEach((element, index) => {
        element.setAttribute('tabindex', '0');
        element.setAttribute('role', 'button');
        element.setAttribute('aria-label', `Elemento ${index + 1} - Clique para interagir`);
        
        element.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.click();
            }
        });
    });
    
    // Adicionar indicadores de foco
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
    
    console.log('♿ Melhorias de acessibilidade configuradas');
}

// Sistema de notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto-remover após 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Função para download de PDF (placeholder melhorado)
function downloadPDF() {
    showNotification('📄 Preparando PDF para download...', 'info');
    
    // Simular processo de geração
    setTimeout(() => {
        showNotification('⚠️ Funcionalidade de PDF será implementada em breve!', 'warning');
    }, 2000);
}

// Sistema de busca e filtros
function initializeSearchAndFilters() {
    // Adicionar barra de busca se necessário
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.innerHTML = `
        <input type="text" placeholder="Buscar na RNC..." class="search-input">
        <button class="search-btn">
            <i class="fas fa-search"></i>
        </button>
    `;
    
    // Inserir antes do primeiro section
    const firstSection = document.querySelector('.section');
    if (firstSection) {
        firstSection.parentNode.insertBefore(searchContainer, firstSection);
    }
    
    // Configurar funcionalidade de busca
    const searchInput = searchContainer.querySelector('.search-input');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        searchInRNC(searchTerm);
    });
}

function searchInRNC(searchTerm) {
    const searchableElements = document.querySelectorAll('.info-value, .text-field-content, .signature-name');
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const parent = element.closest('.info-card, .text-field, .signature-card');
        
        if (searchTerm === '' || text.includes(searchTerm)) {
            parent.style.opacity = '1';
            parent.style.filter = 'none';
        } else {
            parent.style.opacity = '0.3';
            parent.style.filter = 'grayscale(100%)';
        }
    });
}

// Inicializar busca e filtros se necessário
if (document.querySelector('.rnc-content').children.length > 5) {
    initializeSearchAndFilters();
}

// Sistema de modo escuro (opcional)
function initializeDarkMode() {
    const darkModeToggle = document.createElement('button');
    darkModeToggle.className = 'dark-mode-toggle';
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    darkModeToggle.title = 'Alternar modo escuro';
    
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const icon = this.querySelector('i');
        
        if (document.body.classList.contains('dark-mode')) {
            icon.className = 'fas fa-sun';
            showNotification('🌙 Modo escuro ativado', 'info');
        } else {
            icon.className = 'fas fa-moon';
            showNotification('☀️ Modo claro ativado', 'info');
        }
    });
    
    // Adicionar ao header de controles
    const controlsRight = document.querySelector('.controls-right');
    if (controlsRight) {
        controlsRight.appendChild(darkModeToggle);
    }
}

// Inicializar modo escuro
initializeDarkMode();

// Sistema de métricas e analytics
function trackUserInteraction(element, action) {
    console.log(`📊 Interação: ${action} em ${element.tagName.toLowerCase()}`);
    
    // Aqui você pode adicionar código para enviar métricas para um sistema de analytics
    // Por exemplo: gtag('event', 'rnc_interaction', { action: action, element: element.tagName });
}

// Adicionar tracking a todas as interações
document.addEventListener('click', function(event) {
    const target = event.target.closest('.info-card, .signature-card, .status-card, .text-field, .btn');
    if (target) {
        trackUserInteraction(target, 'click');
    }
});

console.log('🚀 RNC View Enhanced JavaScript completamente carregado e funcionando!');
