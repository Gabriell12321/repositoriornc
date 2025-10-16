// 🎮⛏️ SISTEMA DE SONS MINECRAFT - Todos os sons recriados do jogo!
// Sistema completo de sons baseado no Minecraft para feedback de ações

const SoundSystem = {
    context: null,
    enabled: true,
    volume: 0.35,

    // Inicializar contexto de áudio
    init() {
        if (!this.context) {
            this.context = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.context;
    },

    // Criar nota Minecraft (onda quadrada para som pixelado/8-bit)
    createMinecraftNote(frequency, duration, volume = 0.3) {
        const ctx = this.init();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        
        // Onda quadrada = som 8-bit/retro característico do Minecraft
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
        
        // Envelope ADSR característico do Minecraft
        gainNode.gain.setValueAtTime(0, ctx.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume * this.volume, ctx.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
        
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + duration);
    },

    // 🔔 Notificação / XP Orb - Som de experiência coletada (E5 → B5 → C#6)
    notification() {
        if (!this.enabled) return;
        try {
            // Som icônico de XP do Minecraft (o mais reconhecível!)
            this.createMinecraftNote(659.25, 0.15, 0.35);        // E5 - primeira nota
            setTimeout(() => this.createMinecraftNote(987.77, 0.15, 0.3), 80);  // B5 - segunda nota
            setTimeout(() => this.createMinecraftNote(1108.73, 0.2, 0.25), 150); // C#6 - nota final
            
            console.log('🎮⛏️ Som Minecraft: XP Orb coletado!');
        } catch (e) {
            console.error('Erro ao tocar XP:', e);
        }
    },

    // Alias para compatibilidade
    playNotification() {
        this.notification();
    },

    // ✅ Sucesso / Level Up - Som de subir de nível (F#4 → A4 → D5)
    success() {
        if (!this.enabled) return;
        try {
            // Som de Level Up do Minecraft
            this.createMinecraftNote(369.99, 0.12, 0.3);         // F#4
            setTimeout(() => this.createMinecraftNote(440, 0.12, 0.3), 100);      // A4
            setTimeout(() => this.createMinecraftNote(587.33, 0.18, 0.35), 200);  // D5
            
            console.log('🎮⛏️ Som Minecraft: Level Up!');
        } catch (e) {
            console.error('Erro ao tocar level up:', e);
        }
    },

    // ❌ Erro / Damage - Som de dano recebido (C3 → G2)
    error() {
        if (!this.enabled) return;
        try {
            // Som de dano/erro do Minecraft (grave e impactante)
            this.createMinecraftNote(130.81, 0.15, 0.4);   // C3
            setTimeout(() => this.createMinecraftNote(98, 0.2, 0.45), 100);  // G2 (mais grave)
            
            console.log('🎮⛏️ Som Minecraft: Dano recebido!');
        } catch (e) {
            console.error('Erro ao tocar dano:', e);
        }
    },

    // 📨 Envio / Pop - Som de item coletado (F#5 → A5)
    send() {
        if (!this.enabled) return;
        try {
            // Som de "pop" quando pega item do chão
            this.createMinecraftNote(739.99, 0.08, 0.3);   // F#5
            setTimeout(() => this.createMinecraftNote(880, 0.06, 0.25), 60);  // A5
            
            console.log('🎮⛏️ Som Minecraft: Pop! Item coletado');
        } catch (e) {
            console.error('Erro ao tocar pop:', e);
        }
    },

    // 🎯 Clique / Button Click - Som de botão de madeira (C4)
    click() {
        if (!this.enabled) return;
        try {
            // Som de clique em botão/UI do Minecraft
            this.createMinecraftNote(261.63, 0.04, 0.25);  // C4 (curto e seco)
            
            console.log('🎮⛏️ Som Minecraft: Click!');
        } catch (e) {
            console.error('Erro ao tocar click:', e);
        }
    },

    // ⚠️ Aviso / Anvil Land - Som de bigorna caindo (B2 duplo)
    warning() {
        if (!this.enabled) return;
        try {
            // Som de bigorna (alerta pesado)
            this.createMinecraftNote(123.47, 0.12, 0.35);  // B2
            setTimeout(() => this.createMinecraftNote(123.47, 0.12, 0.35), 180); // B2 novamente
            
            console.log('🎮⛏️ Som Minecraft: Anvil! ⚠️');
        } catch (e) {
            console.error('Erro ao tocar anvil:', e);
        }
    },

    // Alias para compatibilidade
    playWarning() {
        this.warning();
    },

    // 🎉 Conquista / Achievement - Som de conquista desbloqueada (C5 → E5 → G5 → C6)
    achievement() {
        if (!this.enabled) return;
        try {
            // Som completo de achievement do Minecraft
            this.createMinecraftNote(523.25, 0.1, 0.3);    // C5
            setTimeout(() => this.createMinecraftNote(659.25, 0.1, 0.3), 80);    // E5
            setTimeout(() => this.createMinecraftNote(783.99, 0.1, 0.3), 160);   // G5
            setTimeout(() => this.createMinecraftNote(1046.5, 0.25, 0.35), 240); // C6
            
            console.log('🎮⛏️ Som Minecraft: Achievement Get! 🏆');
        } catch (e) {
            console.error('Erro ao tocar achievement:', e);
        }
    },

    // 📥 Chegada / Ender Pearl - Som de teletransporte (F5 → C5)
    incoming() {
        if (!this.enabled) return;
        try {
            // Som de Ender Pearl chegando/teletransporte
            this.createMinecraftNote(698.46, 0.1, 0.3);    // F5
            setTimeout(() => this.createMinecraftNote(523.25, 0.12, 0.28), 80);  // C5
            
            console.log('🎮⛏️ Som Minecraft: Ender Pearl teleport!');
        } catch (e) {
            console.error('Erro ao tocar ender pearl:', e);
        }
    },

    // 🪨 Bloco Quebrado / Break - Som de bloco sendo minerado (D4 curto)
    breakBlock() {
        if (!this.enabled) return;
        try {
            // Som de bloco quebrando
            this.createMinecraftNote(293.66, 0.08, 0.35);  // D4
            setTimeout(() => this.createMinecraftNote(220, 0.06, 0.3), 60);  // A3
            
            console.log('🎮⛏️ Som Minecraft: Bloco quebrado!');
        } catch (e) {
            console.error('Erro ao tocar break:', e);
        }
    },

    // 🔨 Bloco Colocado / Place - Som de bloco sendo colocado (G4)
    placeBlock() {
        if (!this.enabled) return;
        try {
            // Som de bloco sendo colocado
            this.createMinecraftNote(392, 0.05, 0.3);  // G4
            
            console.log('🎮⛏️ Som Minecraft: Bloco colocado!');
        } catch (e) {
            console.error('Erro ao tocar place:', e);
        }
    },

    // 🎵 Noteblock - Tocar nota específica (para músicas customizadas)
    playNoteblock(note, octave = 4) {
        const notes = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        };
        
        if (notes[note]) {
            const frequency = notes[note] * Math.pow(2, octave - 4);
            this.createMinecraftNote(frequency, 0.3, 0.3);
            console.log(`🎵 Noteblock: ${note}${octave} (${frequency.toFixed(2)}Hz)`);
        }
    },

    // 🔕 Silenciar/Desabilitar todos os sons
    toggle() {
        this.enabled = !this.enabled;
        console.log(this.enabled ? '🎮 Sons Minecraft ativados! ⛏️' : '🔇 Sons desativados');
        
        // Feedback sonoro do toggle
        if (this.enabled) {
            setTimeout(() => this.playNoteblock('E', 5), 50);
        }
        
        return this.enabled;
    },

    // 🔊 Ajustar volume global (0.0 a 1.0)
    setVolume(vol) {
        this.volume = Math.max(0, Math.min(1, vol));
        console.log(`🔊 Volume Minecraft: ${Math.round(this.volume * 100)}%`);
        
        // Feedback sonoro
        this.playNoteblock('C', 5);
    },

    // Aliases para compatibilidade com código existente
    playSuccess() {
        this.success();
    }
};

// Função global para compatibilidade
function playNotificationSound() {
    if (window.SoundSystem) {
        window.SoundSystem.notification();
    }
}

// Expor globalmente
window.SoundSystem = SoundSystem;

console.log('🎮⛏️ Sistema de Sons Minecraft carregado! Digite SoundSystem para ver métodos disponíveis.');
