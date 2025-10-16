/* 
Sistema de Notificações Melhorado - Frontend JavaScript
Integração com Socket.IO e APIs REST para notificações em tempo real
*/

class NotificationSystem {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.retryCount = 0;
        this.maxRetries = 5;
        this.retryDelay = 1000;
        this.notifications = [];
        this.unreadCount = 0;
        
        // Elementos DOM
        this.badge = document.getElementById('notification-badge');
        this.panel = document.getElementById('notification-panel');
        this.list = document.getElementById('notification-list');
        this.toggleButton = document.getElementById('notification-toggle');
        this.markAllButton = document.getElementById('mark-all-read');
        this.loadMoreButton = document.getElementById('load-more-notifications');
        
        this.init();
    }
    
    init() {
        this.connectSocket();
        this.bindEvents();
        this.loadInitialNotifications();
        this.requestNotificationPermission();
    }
    
    connectSocket() {
        try {
            // Conectar ao namespace de notificações
            this.socket = io('/notifications', {
                autoConnect: true,
                transports: ['websocket', 'polling']
            });
            
            this.socket.on('connect', () => {
                this.isConnected = true;
                this.retryCount = 0;
                console.log('Conectado ao sistema de notificações');
                this.showConnectionStatus('online');
            });
            
            this.socket.on('disconnect', () => {
                this.isConnected = false;
                console.log('Desconectado do sistema de notificações');
                this.showConnectionStatus('offline');
                this.scheduleReconnect();
            });
            
            // Eventos de notificação
            this.socket.on('notifications_sync', (data) => {
                this.handleNotificationsSync(data);
            });
            
            this.socket.on('new_notification', (notification) => {
                this.handleNewNotification(notification);
            });
            
            this.socket.on('notification_read', (data) => {
                this.handleNotificationRead(data);
            });
            
            this.socket.on('all_notifications_read', (data) => {
                this.handleAllNotificationsRead(data);
            });
            
            this.socket.on('notification_dismissed', (data) => {
                this.handleNotificationDismissed(data);
            });
            
            this.socket.on('unread_count_update', (data) => {
                this.updateUnreadCount(data.count);
            });
            
            this.socket.on('system_notification', (notification) => {
                this.handleSystemNotification(notification);
            });
            
            this.socket.on('notifications_list', (data) => {
                this.handleNotificationsList(data);
            });
            
            this.socket.on('error', (error) => {
                console.error('Erro no Socket.IO:', error);
                this.showError(error.message || 'Erro de comunicação');
            });
            
        } catch (error) {
            console.error('Erro ao conectar Socket.IO:', error);
            this.scheduleReconnect();
        }
    }
    
    scheduleReconnect() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            const delay = this.retryDelay * Math.pow(2, this.retryCount - 1); // Backoff exponencial
            
            setTimeout(() => {
                console.log(`Tentativa de reconexão ${this.retryCount}/${this.maxRetries}`);
                this.connectSocket();
            }, delay);
        }
    }
    
    bindEvents() {
        // Toggle do painel de notificações
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.togglePanel();
            });
        }
        
        // Marcar todas como lidas
        if (this.markAllButton) {
            this.markAllButton.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }
        
        // Carregar mais notificações
        if (this.loadMoreButton) {
            this.loadMoreButton.addEventListener('click', () => {
                this.loadMoreNotifications();
            });
        }
        
        // Fechar painel ao clicar fora
        document.addEventListener('click', (e) => {
            if (this.panel && !this.panel.contains(e.target) && !this.toggleButton.contains(e.target)) {
                this.closePanel();
            }
        });
        
        // Tecla ESC para fechar painel
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.panel && this.panel.classList.contains('show')) {
                this.closePanel();
            }
        });
    }
    
    async loadInitialNotifications() {
        try {
            const response = await fetch('/api/notifications/unread');
            const data = await response.json();
            
            if (data.success) {
                this.notifications = data.notifications;
                this.updateUnreadCount(data.count);
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Erro ao carregar notificações iniciais:', error);
        }
    }
    
    async loadMoreNotifications() {
        try {
            const offset = this.notifications.length;
            const response = await fetch(`/api/notifications/all?offset=${offset}&per_page=20`);
            const data = await response.json();
            
            if (data.success) {
                this.notifications.push(...data.notifications);
                this.renderNotifications();
                
                // Esconder botão se não há mais notificações
                if (data.notifications.length < 20) {
                    if (this.loadMoreButton) {
                        this.loadMoreButton.style.display = 'none';
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao carregar mais notificações:', error);
        }
    }
    
    handleNotificationsSync(data) {
        this.notifications = data.notifications;
        this.updateUnreadCount(data.count);
        this.renderNotifications();
    }
    
    handleNewNotification(notification) {
        // Adicionar nova notificação ao início da lista
        this.notifications.unshift(notification);
        this.unreadCount++;
        
        this.updateUnreadCount(this.unreadCount);
        this.renderNotifications();
        
        // Mostrar notificação do navegador se suportado
        this.showBrowserNotification(notification);
        
        // Tocar som de notificação
        this.playNotificationSound();
        
        // Animar badge
        this.animateBadge();
    }
    
    handleNotificationRead(data) {
        // Marcar notificação como lida
        const notification = this.notifications.find(n => n.id === data.notification_id);
        if (notification) {
            notification.read_at = new Date().toISOString();
        }
        
        this.updateUnreadCount(data.unread_count);
        this.renderNotifications();
    }
    
    handleAllNotificationsRead(data) {
        // Marcar todas como lidas
        this.notifications.forEach(n => {
            if (!n.read_at) {
                n.read_at = new Date().toISOString();
            }
        });
        
        this.updateUnreadCount(0);
        this.renderNotifications();
        
        this.showSuccess(`${data.count} notificações marcadas como lidas`);
    }
    
    handleNotificationDismissed(data) {
        // Remover notificação da lista
        this.notifications = this.notifications.filter(n => n.id !== data.notification_id);
        this.updateUnreadCount(data.unread_count);
        this.renderNotifications();
    }
    
    handleSystemNotification(notification) {
        // Notificação do sistema (alta prioridade)
        this.showAlert(notification.data.message, notification.data.type || 'info');
    }
    
    handleNotificationsList(data) {
        this.notifications = data.notifications;
        this.updateUnreadCount(data.unread_count);
        this.renderNotifications();
    }
    
    updateUnreadCount(count) {
        this.unreadCount = count;
        
        if (this.badge) {
            if (count > 0) {
                this.badge.textContent = count > 99 ? '99+' : count;
                this.badge.style.display = 'inline-block';
                this.badge.classList.add('has-notifications');
            } else {
                this.badge.style.display = 'none';
                this.badge.classList.remove('has-notifications');
            }
        }
        
        // Atualizar título da página
        this.updatePageTitle(count);
    }
    
    updatePageTitle(count) {
        const baseTitle = 'Sistema RNC';
        document.title = count > 0 ? `(${count}) ${baseTitle}` : baseTitle;
    }
    
    renderNotifications() {
        if (!this.list) return;
        
        if (this.notifications.length === 0) {
            this.list.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>Nenhuma notificação</p>
                </div>
            `;
            return;
        }
        
        const html = this.notifications.map(notification => {
            return this.renderNotificationItem(notification);
        }).join('');
        
        this.list.innerHTML = html;
        
        // Bind eventos de clique
        this.bindNotificationEvents();
    }
    
    renderNotificationItem(notification) {
        const isUnread = !notification.read_at;
        const createdAt = new Date(notification.created_at);
        const timeAgo = this.getTimeAgo(createdAt);
        
        const icon = this.getNotificationIcon(notification.type);
        const message = this.formatNotificationMessage(notification);
        
        return `
            <div class="notification-item ${isUnread ? 'unread' : ''}" data-id="${notification.id}">
                <div class="notification-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-message">${message}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
                <div class="notification-actions">
                    ${isUnread ? '<button class="btn-mark-read" title="Marcar como lida"><i class="fas fa-check"></i></button>' : ''}
                    <button class="btn-dismiss" title="Dispensar"><i class="fas fa-times"></i></button>
                </div>
            </div>
        `;
    }
    
    bindNotificationEvents() {
        // Marcar como lida
        this.list.querySelectorAll('.btn-mark-read').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const notificationId = btn.closest('.notification-item').dataset.id;
                this.markAsRead(notificationId);
            });
        });
        
        // Dispensar
        this.list.querySelectorAll('.btn-dismiss').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const notificationId = btn.closest('.notification-item').dataset.id;
                this.dismissNotification(notificationId);
            });
        });
        
        // Clique na notificação
        this.list.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.id;
                const notification = this.notifications.find(n => n.id == notificationId);
                
                if (notification && notification.data.action_url) {
                    // Marcar como lida e navegar
                    this.markAsRead(notificationId);
                    window.location.href = notification.data.action_url;
                }
            });
        });
    }
    
    getNotificationIcon(type) {
        const icons = {
            'rnc_created': 'fas fa-plus-circle text-primary',
            'rnc_assigned': 'fas fa-user-tag text-warning',
            'rnc_updated': 'fas fa-edit text-info',
            'rnc_commented': 'fas fa-comment text-success',
            'rnc_finalized': 'fas fa-check-circle text-success',
            'system_maintenance': 'fas fa-tools text-warning',
            'user_message': 'fas fa-envelope text-info',
            'reminder': 'fas fa-clock text-secondary'
        };
        
        return icons[type] || 'fas fa-bell text-secondary';
    }
    
    formatNotificationMessage(notification) {
        const { type, data } = notification;
        
        switch (type) {
            case 'rnc_created':
                return `Nova RNC criada: <strong>${data.rnc_number}</strong> por ${data.creator_name}`;
            
            case 'rnc_assigned':
                return `RNC <strong>${data.rnc_number}</strong> foi atribuída a você por ${data.assigner_name}`;
            
            case 'rnc_updated':
                return `RNC <strong>${data.rnc_number}</strong> foi atualizada por ${data.updater_name}`;
            
            case 'rnc_commented':
                return `Novo comentário na RNC <strong>${data.rnc_number}</strong> por ${data.commenter_name}`;
            
            case 'rnc_finalized':
                return `RNC <strong>${data.rnc_number}</strong> foi finalizada por ${data.finalizer_name}`;
            
            case 'system_maintenance':
                return `<strong>Manutenção do Sistema:</strong> ${data.message}`;
            
            case 'user_message':
                return `<strong>Mensagem:</strong> ${data.message}`;
            
            case 'reminder':
                return `<strong>Lembrete:</strong> ${data.message}`;
            
            default:
                return data.message || 'Nova notificação';
        }
    }
    
    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Agora';
        if (minutes < 60) return `${minutes}m`;
        if (hours < 24) return `${hours}h`;
        if (days < 7) return `${days}d`;
        
        return date.toLocaleDateString('pt-BR');
    }
    
    markAsRead(notificationId) {
        if (this.socket && this.isConnected) {
            this.socket.emit('mark_notification_read', {
                notification_id: parseInt(notificationId)
            });
        } else {
            // Fallback para API REST
            this.markAsReadAPI(notificationId);
        }
    }
    
    async markAsReadAPI(notificationId) {
        try {
            const response = await fetch('/api/notifications/mark-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    notification_ids: [parseInt(notificationId)]
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.handleNotificationRead({
                    notification_id: parseInt(notificationId),
                    unread_count: data.unread_count
                });
            }
        } catch (error) {
            console.error('Erro ao marcar notificação como lida:', error);
        }
    }
    
    markAllAsRead() {
        if (this.socket && this.isConnected) {
            this.socket.emit('mark_all_read');
        } else {
            // Fallback para API REST
            this.markAllAsReadAPI();
        }
    }
    
    async markAllAsReadAPI() {
        try {
            const unreadIds = this.notifications
                .filter(n => !n.read_at)
                .map(n => n.id);
            
            if (unreadIds.length === 0) return;
            
            const response = await fetch('/api/notifications/mark-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    notification_ids: unreadIds
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.handleAllNotificationsRead({
                    count: unreadIds.length
                });
            }
        } catch (error) {
            console.error('Erro ao marcar todas as notificações como lidas:', error);
        }
    }
    
    dismissNotification(notificationId) {
        if (this.socket && this.isConnected) {
            this.socket.emit('dismiss_notification', {
                notification_id: parseInt(notificationId)
            });
        } else {
            // Fallback para API REST
            this.dismissNotificationAPI(notificationId);
        }
    }
    
    async dismissNotificationAPI(notificationId) {
        try {
            const response = await fetch('/api/notifications/dismiss', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    notification_ids: [parseInt(notificationId)]
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.handleNotificationDismissed({
                    notification_id: parseInt(notificationId),
                    unread_count: data.unread_count
                });
            }
        } catch (error) {
            console.error('Erro ao dispensar notificação:', error);
        }
    }
    
    togglePanel() {
        if (!this.panel) return;
        
        if (this.panel.classList.contains('show')) {
            this.closePanel();
        } else {
            this.openPanel();
        }
    }
    
    openPanel() {
        if (!this.panel) return;
        
        this.panel.classList.add('show');
        
        // Carregar notificações se necessário
        if (this.notifications.length === 0) {
            this.loadInitialNotifications();
        }
    }
    
    closePanel() {
        if (!this.panel) return;
        
        this.panel.classList.remove('show');
    }
    
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            try {
                const permission = await Notification.requestPermission();
                console.log('Permissão de notificação:', permission);
            } catch (error) {
                console.error('Erro ao solicitar permissão de notificação:', error);
            }
        }
    }
    
    showBrowserNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const title = 'Sistema RNC';
            const message = this.formatNotificationMessage(notification).replace(/<[^>]*>/g, ''); // Remove HTML
            
            const browserNotification = new Notification(title, {
                body: message,
                icon: '/static/images/logo-notification.png',
                badge: '/static/images/badge-notification.png',
                tag: `notification-${notification.id}`,
                requireInteraction: true
            });
            
            browserNotification.onclick = () => {
                window.focus();
                if (notification.data.action_url) {
                    window.location.href = notification.data.action_url;
                }
                browserNotification.close();
            };
            
            // Auto-fechar após 5 segundos
            setTimeout(() => {
                browserNotification.close();
            }, 5000);
        }
    }
    
    playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => {
                console.log('Não foi possível tocar o som de notificação:', e.message);
            });
        } catch (error) {
            console.log('Erro ao tocar som de notificação:', error);
        }
    }
    
    animateBadge() {
        if (this.badge) {
            this.badge.classList.add('pulse');
            setTimeout(() => {
                this.badge.classList.remove('pulse');
            }, 1000);
        }
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = status === 'online' ? 'Online' : 'Offline';
        }
    }
    
    showError(message) {
        this.showAlert(message, 'error');
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showAlert(message, type = 'info') {
        // Implementar sistema de alertas/toasts
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Se existir um sistema de toast, usar aqui
        if (window.showToast) {
            window.showToast(message, type);
        }
    }
    
    // Método para fechar conexão (cleanup)
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
        }
    }
}

// Inicializar sistema quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o usuário está logado
    if (document.body.classList.contains('logged-in')) {
        window.notificationSystem = new NotificationSystem();
    }
});

// Cleanup ao sair da página
window.addEventListener('beforeunload', function() {
    if (window.notificationSystem) {
        window.notificationSystem.disconnect();
    }
});