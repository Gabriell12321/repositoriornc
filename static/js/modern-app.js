/**
 * Sistema de Interface Interativa Moderna - IPPEL RNC
 * JavaScript moderno com ES6+, componentes reutilizáveis e performance otimizada
 */

// Utilitários base
const Utils = {
  /**
   * Debounce function para otimizar eventos
   */
  debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        if (!immediate) func(...args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func(...args);
    };
  },

  /**
   * Throttle function para eventos de scroll/resize
   */
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * Formatação de moeda brasileira
   */
  formatCurrency(value) {
    if (!value && value !== 0) return 'R$ 0,00';
    const number = parseFloat(value);
    if (isNaN(number)) return 'R$ 0,00';
    
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2
    }).format(number);
  },

  /**
   * Formatação de data brasileira
   */
  formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR').format(date);
  },

  /**
   * Formatação de data/hora relativa
   */
  formatRelativeTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = [
      { label: 'ano', seconds: 31536000 },
      { label: 'mês', seconds: 2592000 },
      { label: 'dia', seconds: 86400 },
      { label: 'hora', seconds: 3600 },
      { label: 'minuto', seconds: 60 },
      { label: 'segundo', seconds: 1 }
    ];
    
    for (const interval of intervals) {
      const count = Math.floor(diffInSeconds / interval.seconds);
      if (count >= 1) {
        return `há ${count} ${interval.label}${count > 1 ? 's' : ''}`;
      }
    }
    
    return 'agora';
  },

  /**
   * Gera ID único
   */
  generateId(prefix = 'id') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Copia texto para o clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback para navegadores mais antigos
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    }
  }
};

// Sistema de Notificações
class NotificationSystem {
  constructor() {
    this.container = this.createContainer();
    this.notifications = new Map();
  }

  createContainer() {
    let container = document.getElementById('notifications-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'notifications-container';
      container.className = 'fixed top-4 right-4 z-50 space-y-2';
      container.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 400px;
        pointer-events: none;
      `;
      document.body.appendChild(container);
    }
    return container;
  }

  show(message, type = 'info', duration = 5000) {
    const id = Utils.generateId('notification');
    const notification = this.createNotification(id, message, type, duration);
    
    this.container.appendChild(notification);
    this.notifications.set(id, notification);
    
    // Animação de entrada
    requestAnimationFrame(() => {
      notification.style.transform = 'translateX(0)';
      notification.style.opacity = '1';
    });
    
    // Auto-remove
    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }
    
    return id;
  }

  createNotification(id, message, type, duration) {
    const notification = document.createElement('div');
    notification.id = id;
    notification.className = `alert alert-${type} animate-slide-in-up`;
    notification.style.cssText = `
      pointer-events: auto;
      transform: translateX(100%);
      opacity: 0;
      transition: all 0.3s ease-out;
      cursor: pointer;
    `;
    
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    
    notification.innerHTML = `
      <div class="flex items-start gap-3">
        <span class="text-xl">${icons[type] || icons.info}</span>
        <div class="flex-1">
          <p class="text-sm font-medium">${message}</p>
          ${duration > 0 ? `<div class="notification-progress"></div>` : ''}
        </div>
        <button class="notification-close text-lg opacity-50 hover:opacity-100">×</button>
      </div>
    `;
    
    // Progress bar
    if (duration > 0) {
      const progress = notification.querySelector('.notification-progress');
      progress.style.cssText = `
        height: 2px;
        background-color: currentColor;
        opacity: 0.3;
        margin-top: 0.5rem;
        transform-origin: left;
        animation: progress-shrink ${duration}ms linear forwards;
      `;
    }
    
    // Event listeners
    notification.addEventListener('click', () => this.remove(id));
    
    return notification;
  }

  remove(id) {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.style.transform = 'translateX(100%)';
      notification.style.opacity = '0';
      
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
        this.notifications.delete(id);
      }, 300);
    }
  }

  success(message, duration = 3000) {
    return this.show(message, 'success', duration);
  }

  error(message, duration = 7000) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration = 5000) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration = 4000) {
    return this.show(message, 'info', duration);
  }
}

// Sistema de Loading
class LoadingSystem {
  constructor() {
    this.overlay = this.createOverlay();
    this.activeRequests = new Set();
  }

  createOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9998;
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
    `;
    
    overlay.innerHTML = `
      <div class="bg-white rounded-lg p-6 flex flex-col items-center gap-4 shadow-2xl">
        <div class="loading"></div>
        <p class="text-sm text-gray-600" id="loading-message">Carregando...</p>
      </div>
    `;
    
    document.body.appendChild(overlay);
    return overlay;
  }

  show(message = 'Carregando...') {
    const messageEl = this.overlay.querySelector('#loading-message');
    if (messageEl) {
      messageEl.textContent = message;
    }
    
    this.overlay.style.opacity = '1';
    this.overlay.style.visibility = 'visible';
    document.body.style.overflow = 'hidden';
  }

  hide() {
    this.overlay.style.opacity = '0';
    this.overlay.style.visibility = 'hidden';
    document.body.style.overflow = '';
  }

  showForElement(element, message = 'Carregando...') {
    const id = Utils.generateId('loading');
    this.activeRequests.add(id);
    
    const originalContent = element.innerHTML;
    element.innerHTML = `
      <div class="flex items-center justify-center gap-2 py-2">
        <div class="loading"></div>
        <span class="text-sm">${message}</span>
      </div>
    `;
    
    element.style.pointerEvents = 'none';
    element.style.opacity = '0.7';
    
    return () => {
      if (this.activeRequests.has(id)) {
        element.innerHTML = originalContent;
        element.style.pointerEvents = '';
        element.style.opacity = '';
        this.activeRequests.delete(id);
      }
    };
  }
}

// Sistema de Modais
class ModalSystem {
  constructor() {
    this.modals = new Map();
    this.bindEvents();
  }

  bindEvents() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-modal-trigger]')) {
        e.preventDefault();
        const modalId = e.target.getAttribute('data-modal-trigger');
        this.open(modalId);
      }
      
      if (e.target.matches('[data-modal-close]') || e.target.closest('.modal-backdrop')) {
        const modal = e.target.closest('.modal');
        if (modal) {
          this.close(modal.id);
        }
      }
    });
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeAll();
      }
    });
  }

  create(id, options = {}) {
    const {
      title = '',
      content = '',
      size = 'md',
      closeButton = true,
      backdrop = true
    } = options;
    
    const modalHtml = `
      <div class="modal-backdrop${backdrop ? '' : ' no-backdrop'}"></div>
      <div class="modal-content modal-${size}">
        ${title || closeButton ? `
          <div class="modal-header">
            ${title ? `<h3 class="modal-title">${title}</h3>` : ''}
            ${closeButton ? '<button class="modal-close" data-modal-close>×</button>' : ''}
          </div>
        ` : ''}
        <div class="modal-body">
          ${content}
        </div>
      </div>
    `;
    
    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal';
    modal.innerHTML = modalHtml;
    modal.style.display = 'none';
    
    document.body.appendChild(modal);
    this.modals.set(id, modal);
    
    return modal;
  }

  open(id, content = null) {
    let modal = this.modals.get(id);
    if (!modal) {
      modal = document.getElementById(id);
      if (modal) {
        this.modals.set(id, modal);
      }
    }
    
    if (!modal) {
      console.error(`Modal with id "${id}" not found`);
      return;
    }
    
    if (content) {
      const body = modal.querySelector('.modal-body');
      if (body) {
        body.innerHTML = content;
      }
    }
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    requestAnimationFrame(() => {
      modal.classList.add('show');
      const backdrop = modal.querySelector('.modal-backdrop');
      if (backdrop) {
        backdrop.classList.add('show');
      }
    });
  }

  close(id) {
    const modal = this.modals.get(id) || document.getElementById(id);
    if (!modal) return;
    
    modal.classList.remove('show');
    const backdrop = modal.querySelector('.modal-backdrop');
    if (backdrop) {
      backdrop.classList.remove('show');
    }
    
    setTimeout(() => {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }, 300);
  }

  closeAll() {
    this.modals.forEach((modal, id) => {
      if (modal.classList.contains('show')) {
        this.close(id);
      }
    });
  }
}

// Sistema de API
class APIClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    };
  }

  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      data = null,
      headers = {},
      showLoading = false,
      loadingMessage = 'Processando...'
    } = options;

    const url = this.baseURL + endpoint;
    const config = {
      method,
      headers: { ...this.defaultHeaders, ...headers },
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    let hideLoading;
    if (showLoading) {
      App.loading.show(loadingMessage);
      hideLoading = () => App.loading.hide();
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (hideLoading) hideLoading();
      
      return result;
    } catch (error) {
      if (hideLoading) hideLoading();
      console.error('API Request failed:', error);
      throw error;
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  post(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', data });
  }

  put(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', data });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

// Sistema de Formulários
class FormValidator {
  constructor(form) {
    this.form = typeof form === 'string' ? document.getElementById(form) : form;
    this.rules = new Map();
    this.errors = new Map();
    this.bindEvents();
  }

  bindEvents() {
    if (!this.form) return;
    
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.validate().then(isValid => {
        if (isValid) {
          this.handleSubmit();
        }
      });
    });
    
    // Validação em tempo real
    this.form.addEventListener('blur', (e) => {
      if (e.target.matches('input, textarea, select')) {
        this.validateField(e.target.name);
      }
    }, true);
    
    this.form.addEventListener('input', Utils.debounce((e) => {
      if (e.target.matches('input, textarea') && this.errors.has(e.target.name)) {
        this.validateField(e.target.name);
      }
    }, 300));
  }

  addRule(fieldName, validator, message) {
    if (!this.rules.has(fieldName)) {
      this.rules.set(fieldName, []);
    }
    this.rules.get(fieldName).push({ validator, message });
    return this;
  }

  required(fieldName, message = 'Este campo é obrigatório') {
    return this.addRule(fieldName, (value) => {
      return value !== null && value !== undefined && value.toString().trim() !== '';
    }, message);
  }

  email(fieldName, message = 'Digite um email válido') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return this.addRule(fieldName, (value) => {
      return !value || emailRegex.test(value);
    }, message);
  }

  minLength(fieldName, min, message) {
    return this.addRule(fieldName, (value) => {
      return !value || value.toString().length >= min;
    }, message || `Mínimo de ${min} caracteres`);
  }

  maxLength(fieldName, max, message) {
    return this.addRule(fieldName, (value) => {
      return !value || value.toString().length <= max;
    }, message || `Máximo de ${max} caracteres`);
  }

  pattern(fieldName, regex, message = 'Formato inválido') {
    return this.addRule(fieldName, (value) => {
      return !value || regex.test(value);
    }, message);
  }

  async validateField(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field || !this.rules.has(fieldName)) return true;
    
    const value = field.value;
    const rules = this.rules.get(fieldName);
    
    this.clearFieldError(fieldName);
    
    for (const rule of rules) {
      const isValid = await rule.validator(value, this.getFormData());
      if (!isValid) {
        this.setFieldError(fieldName, rule.message);
        return false;
      }
    }
    
    return true;
  }

  async validate() {
    this.clearAllErrors();
    
    const promises = Array.from(this.rules.keys()).map(fieldName => 
      this.validateField(fieldName)
    );
    
    const results = await Promise.all(promises);
    return results.every(result => result === true);
  }

  setFieldError(fieldName, message) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field) return;
    
    field.classList.add('is-invalid');
    this.errors.set(fieldName, message);
    
    let errorElement = field.parentNode.querySelector('.form-error');
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'form-error';
      field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
  }

  clearFieldError(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field) return;
    
    field.classList.remove('is-invalid');
    this.errors.delete(fieldName);
    
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) {
      errorElement.remove();
    }
  }

  clearAllErrors() {
    this.errors.clear();
    this.form.querySelectorAll('.is-invalid').forEach(field => {
      field.classList.remove('is-invalid');
    });
    this.form.querySelectorAll('.form-error').forEach(error => {
      error.remove();
    });
  }

  getFormData() {
    const formData = new FormData(this.form);
    const data = {};
    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }
    return data;
  }

  handleSubmit() {
    // Implementar em subclasse ou via callback
    console.log('Form submitted:', this.getFormData());
  }
}

// Sistema Principal da Aplicação
class IPPELApp {
  constructor() {
    this.notifications = new NotificationSystem();
    this.loading = new LoadingSystem();
    this.modals = new ModalSystem();
    this.api = new APIClient('/api');
    this.components = new Map();
    
    this.init();
  }

  init() {
    this.addProgressStyles();
    this.bindGlobalEvents();
    this.initComponents();
    
    // Indicar que a aplicação está carregada
    document.documentElement.classList.add('app-loaded');
  }

  addProgressStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes progress-shrink {
        from { transform: scaleX(1); }
        to { transform: scaleX(0); }
      }
      
      .notification-progress {
        transform-origin: left center;
      }
    `;
    document.head.appendChild(style);
  }

  bindGlobalEvents() {
    // Formulários AJAX
    document.addEventListener('submit', async (e) => {
      if (e.target.matches('[data-ajax-form]')) {
        e.preventDefault();
        await this.handleAjaxForm(e.target);
      }
    });
    
    // Botões de ação
    document.addEventListener('click', async (e) => {
      if (e.target.matches('[data-action]')) {
        e.preventDefault();
        await this.handleAction(e.target);
      }
      
      // Copiar para clipboard
      if (e.target.matches('[data-clipboard]')) {
        e.preventDefault();
        const text = e.target.getAttribute('data-clipboard');
        const success = await Utils.copyToClipboard(text);
        
        if (success) {
          this.notifications.success('Copiado para a área de transferência!');
        } else {
          this.notifications.error('Erro ao copiar');
        }
      }
    });
    
    // Auto-save em formulários
    document.addEventListener('input', Utils.debounce((e) => {
      if (e.target.matches('[data-auto-save]')) {
        this.autoSaveField(e.target);
      }
    }, 1000));
  }

  async handleAjaxForm(form) {
    const url = form.action || window.location.href;
    const method = form.method || 'POST';
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
      const response = await this.api.request(url, {
        method,
        data,
        showLoading: true,
        loadingMessage: 'Salvando...'
      });
      
      if (response.success) {
        this.notifications.success(response.message || 'Operação realizada com sucesso!');
        
        // Redirecionar se especificado
        if (response.redirect) {
          setTimeout(() => {
            window.location.href = response.redirect;
          }, 1000);
        }
      } else {
        this.notifications.error(response.message || 'Erro na operação');
        
        // Mostrar erros de validação
        if (response.errors) {
          this.showValidationErrors(form, response.errors);
        }
      }
    } catch (error) {
      this.notifications.error('Erro de conexão. Tente novamente.');
      console.error('Form submission error:', error);
    }
  }

  async handleAction(button) {
    const action = button.getAttribute('data-action');
    const confirm = button.getAttribute('data-confirm');
    
    if (confirm && !window.confirm(confirm)) {
      return;
    }
    
    const hideLoading = this.loading.showForElement(button, 'Processando...');
    
    try {
      switch (action) {
        case 'delete-rnc':
          await this.deleteRNC(button.getAttribute('data-rnc-id'));
          break;
        case 'toggle-status':
          await this.toggleRNCStatus(button.getAttribute('data-rnc-id'));
          break;
        case 'refresh-stats':
          await this.refreshDashboardStats();
          break;
        default:
          console.warn(`Unknown action: ${action}`);
      }
    } catch (error) {
      this.notifications.error('Erro ao executar ação');
      console.error('Action error:', error);
    } finally {
      hideLoading();
    }
  }

  showValidationErrors(form, errors) {
    errors.forEach(error => {
      const field = form.querySelector(`[name="${error.field}"]`);
      if (field) {
        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = error.message;
        field.parentNode.appendChild(errorElement);
        field.classList.add('is-invalid');
      }
    });
  }

  async autoSaveField(field) {
    const url = field.getAttribute('data-auto-save');
    const data = {
      field: field.name,
      value: field.value,
      id: field.getAttribute('data-record-id')
    };
    
    try {
      await this.api.post(url, data);
      // Visual feedback sutil
      field.style.borderColor = 'var(--success-500)';
      setTimeout(() => {
        field.style.borderColor = '';
      }, 1000);
    } catch (error) {
      field.style.borderColor = 'var(--error-500)';
      setTimeout(() => {
        field.style.borderColor = '';
      }, 2000);
    }
  }

  initComponents() {
    // Inicializar componentes específicos
    this.initDataTables();
    this.initCharts();
    this.initRealTimeUpdates();
  }

  initDataTables() {
    document.querySelectorAll('[data-table]').forEach(table => {
      // Implementar funcionalidade de tabela avançada
      this.enhanceTable(table);
    });
  }

  enhanceTable(table) {
    // Adicionar ordenação
    const headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        this.sortTable(table, header.getAttribute('data-sort'));
      });
    });
    
    // Adicionar busca se existir input
    const searchInput = document.querySelector(`[data-search="${table.id}"]`);
    if (searchInput) {
      searchInput.addEventListener('input', Utils.debounce((e) => {
        this.filterTable(table, e.target.value);
      }, 300));
    }
  }

  sortTable(table, column) {
    // Implementação de ordenação de tabela
    console.log('Sorting table by:', column);
  }

  filterTable(table, query) {
    const rows = table.querySelectorAll('tbody tr');
    const searchTerm = query.toLowerCase();
    
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
  }

  initCharts() {
    // Inicializar gráficos com Chart.js se disponível
    if (typeof Chart !== 'undefined') {
      document.querySelectorAll('[data-chart]').forEach(canvas => {
        this.createChart(canvas);
      });
    }
  }

  createChart(canvas) {
    const type = canvas.getAttribute('data-chart');
    const dataUrl = canvas.getAttribute('data-url');
    
    if (dataUrl) {
      this.api.get(dataUrl).then(response => {
        new Chart(canvas, {
          type,
          data: response.data,
          options: this.getChartOptions(type)
        });
      });
    }
  }

  getChartOptions(type) {
    // Opções base para gráficos
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    };
  }

  initRealTimeUpdates() {
    // Sistema de atualizações em tempo real
    if (window.WebSocket) {
      this.setupWebSocket();
    } else {
      // Polling como fallback
      this.setupPolling();
    }
  }

  setupWebSocket() {
    // Implementar WebSocket para updates em tempo real
    console.log('WebSocket support detected');
  }

  setupPolling() {
    // Polling para atualizações
    setInterval(() => {
      this.checkForUpdates();
    }, 30000); // 30 segundos
  }

  async checkForUpdates() {
    try {
      const response = await this.api.get('/updates/check');
      if (response.hasUpdates) {
        this.notifications.info('Novas atualizações disponíveis', 0);
      }
    } catch (error) {
      // Silencioso em caso de erro de polling
    }
  }

  // Métodos específicos da aplicação
  async deleteRNC(id) {
    const response = await this.api.delete(`/rnc/${id}`);
    if (response.success) {
      this.notifications.success('RNC excluída com sucesso');
      // Remover da interface
      const row = document.querySelector(`[data-rnc-id="${id}"]`)?.closest('tr');
      if (row) {
        row.remove();
      }
    }
  }

  async toggleRNCStatus(id) {
    const response = await this.api.post(`/rnc/${id}/toggle-status`);
    if (response.success) {
      this.notifications.success('Status atualizado');
      // Atualizar interface
      location.reload();
    }
  }

  async refreshDashboardStats() {
    const response = await this.api.get('/dashboard/stats');
    if (response.success) {
      this.updateDashboardStats(response.data);
      this.notifications.success('Estatísticas atualizadas');
    }
  }

  updateDashboardStats(stats) {
    Object.entries(stats).forEach(([key, value]) => {
      const element = document.querySelector(`[data-stat="${key}"]`);
      if (element) {
        if (typeof value === 'number' && key.includes('price') || key.includes('value')) {
          element.textContent = Utils.formatCurrency(value);
        } else {
          element.textContent = value;
        }
      }
    });
  }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  window.App = new IPPELApp();
});

// Exportar para uso global
window.Utils = Utils;
window.NotificationSystem = NotificationSystem;
window.LoadingSystem = LoadingSystem;
window.ModalSystem = ModalSystem;
window.APIClient = APIClient;
window.FormValidator = FormValidator;
