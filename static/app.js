/* ==========================================================================
   VALENTI AI - Interactive Store v2.0
   3D Scroll Animations · Parallax · Voice Agent · Cart
   ========================================================================== */

/* ──────────────────────────────────────────────
   Global State
   ────────────────────────────────────────────── */
let products = [];
let cart = [];
let currentCategory = 'all';
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let asrMode = 'online';
let ttsMode = 'online';

const API = '';  // Same origin

/* ──────────────────────────────────────────────
   DOM Ready Initializer
   ────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
    initCustomCursor();
    initScrollProgress();
    initScrollRevealObserver();
    initHeroStats();
    loadProducts();
    initCartUI();
    initVoiceWidget();
    initEngineToggles();
    initWaveform();
});

/* ══════════════════════════════════════════════
   1. Custom Cursor
   ══════════════════════════════════════════════ */
function initCustomCursor() {
    const dot = document.getElementById('cursor-dot');
    const ring = document.getElementById('cursor-ring');
    if (!dot || !ring) return;

    document.addEventListener('mousemove', e => {
        dot.style.left = e.clientX - 4 + 'px';
        dot.style.top = e.clientY - 4 + 'px';
        ring.style.left = e.clientX + 'px';
        ring.style.top = e.clientY + 'px';
    });

    // Grow ring on interactive elements
    document.addEventListener('mouseover', e => {
        if (e.target.closest('button, a, .cat-card, .product-card, .category-list li, .mic-button')) {
            ring.classList.add('hover');
        }
    });
    document.addEventListener('mouseout', e => {
        if (e.target.closest('button, a, .cat-card, .product-card, .category-list li, .mic-button')) {
            ring.classList.remove('hover');
        }
    });
}

/* ══════════════════════════════════════════════
   2. Scroll Progress Bar
   ══════════════════════════════════════════════ */
function initScrollProgress() {
    const bar = document.getElementById('scroll-progress');
    if (!bar) return;
    window.addEventListener('scroll', () => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (window.scrollY / h * 100) + '%';
    }, { passive: true });
}

/* ══════════════════════════════════════════════
   3. Scroll Reveal (Intersection Observer)
   ══════════════════════════════════════════════ */
function initScrollRevealObserver() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Reveal all children with stagger
                const children = entry.target.querySelectorAll('.anim-reveal-child');
                children.forEach((child, i) => {
                    setTimeout(() => child.classList.add('visible'), i * 80);
                });
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });

    document.querySelectorAll('.anim-reveal').forEach(el => observer.observe(el));
}

/* ══════════════════════════════════════════════
   4. Hero Stats Counter Animation
   ══════════════════════════════════════════════ */
function initHeroStats() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const nums = entry.target.querySelectorAll('.stat-num');
                nums.forEach(el => animateCounter(el, parseInt(el.dataset.target)));
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const stats = document.querySelector('.hero-stats');
    if (stats) observer.observe(stats);
}

function animateCounter(el, target) {
    let current = 0;
    const step = Math.max(1, Math.floor(target / 30));
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = current + '+';
    }, 50);
}

/* ══════════════════════════════════════════════
   5. Products Loading & Rendering
   ══════════════════════════════════════════════ */
async function loadProducts() {
    try {
        const res = await fetch(`${API}/products`);
        products = await res.json();
        renderCategoryShowcase();
        renderProducts();
    } catch (err) {
        console.error('Failed to load products:', err);
        document.getElementById('product-grid').innerHTML =
            `<div class="loading-spinner"><i class="fa-solid fa-triangle-exclamation"></i> Could not load products. Start the server first.</div>`;
    }
}

/* Category Showcase - 3D Tilt Cards */
function renderCategoryShowcase() {
    const container = document.getElementById('category-showcase');
    if (!container) return;

    const categories = [...new Set(products.map(p => p.category))];
    // Map of category -> icon + description
    const catMeta = {
        shirt: { icon: 'fa-shirt', desc: 'Premium Cotton' },
        watch: { icon: 'fa-clock', desc: 'Luxury Timepieces' },
        pant: { icon: 'fa-person', desc: 'Tailored Fit' },
        shoes: { icon: 'fa-shoe-prints', desc: 'Street to Formal' },
        jacket: { icon: 'fa-vest-patches', desc: 'Outerwear' },
        bag: { icon: 'fa-briefcase', desc: 'Carry in Style' },
        hat: { icon: 'fa-hat-cowboy', desc: 'Top It Off' },
        sunglasses: { icon: 'fa-glasses', desc: 'UV Protection' },
        belt: { icon: 'fa-grip-lines', desc: 'Statement Pieces' },
        socks: { icon: 'fa-socks', desc: 'Comfort First' },
    };

    container.innerHTML = categories.map(cat => {
        const first = products.find(p => p.category === cat);
        const count = products.filter(p => p.category === cat).length;
        const meta = catMeta[cat] || { icon: 'fa-tag', desc: cat };
        const imgSrc = first?.image || `https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&auto=format`;
        return `
            <div class="cat-card" data-category="${cat}" onclick="filterByCategory('${cat}')">
                <img src="${imgSrc}" alt="${cat}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&auto=format'">
                <div class="cat-card-overlay">
                    <div class="cat-card-title">${cat}</div>
                    <div class="cat-card-count">${count} items · ${meta.desc}</div>
                </div>
            </div>
        `;
    }).join('');

    // 3D tilt effect on mouse move
    container.querySelectorAll('.cat-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(600px) rotateY(${x * 12}deg) rotateX(${-y * 12}deg) scale(1.03)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

/* Product Grid Rendering with Scroll Reveal */
function renderProducts(filter = 'all') {
    const grid = document.getElementById('product-grid');
    const filtered = filter === 'all' ? products : products.filter(p => p.category === filter);

    grid.innerHTML = filtered.map((p, i) => `
        <div class="product-card" id="product-${p.id}" style="transition-delay: ${Math.min(i * 0.04, 0.6)}s">
            <div class="product-img-container">
                <img src="${p.image}" alt="${p.name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&auto=format'">
                <span class="product-tag">${p.category}</span>
            </div>
            <div class="product-info">
                <h3 class="product-title">${p.name}</h3>
                <p class="product-desc">${p.description || ''}</p>
                <div class="product-meta">
                    <span class="product-price">$${Number(p.price).toFixed(2)}</span>
                    <button class="btn-add-cart" onclick="addToCart('${p.id}')" title="Add to cart">
                        <i class="fa-solid fa-plus"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Observe each product card for scroll reveal
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05, rootMargin: '0px 0px -30px 0px' });

    grid.querySelectorAll('.product-card').forEach(card => observer.observe(card));
}

/* Filter by category (from sidebar or showcase clicks) */
function filterByCategory(cat) {
    currentCategory = cat;
    renderProducts(cat);

    // Update sidebar active state
    document.querySelectorAll('.category-list li').forEach(li => {
        li.classList.toggle('active', li.dataset.category === cat);
    });

    // Smooth scroll to catalog
    document.getElementById('catalog').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function scrollToCatalog() {
    document.getElementById('catalog').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ══════════════════════════════════════════════
   6. Shopping Cart Logic
   ══════════════════════════════════════════════ */
function initCartUI() {
    const toggleBtn = document.getElementById('cart-toggle');
    const closeBtn = document.getElementById('close-cart');
    const overlay = document.getElementById('cart-overlay');
    const sidebar = document.getElementById('cart-sidebar');

    toggleBtn?.addEventListener('click', () => {
        sidebar.classList.add('open');
        overlay.classList.add('active');
    });
    closeBtn?.addEventListener('click', closeCart);
    overlay?.addEventListener('click', closeCart);

    // Sidebar category clicks
    document.querySelectorAll('.category-list li').forEach(li => {
        li.addEventListener('click', () => filterByCategory(li.dataset.category));
    });
}

function closeCart() {
    document.getElementById('cart-sidebar').classList.remove('open');
    document.getElementById('cart-overlay').classList.remove('active');
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    updateCartUI();

    // Visual feedback on button
    const card = document.getElementById(`product-${productId}`);
    if (card) {
        card.style.boxShadow = '0 0 20px rgba(157,78,221,0.5)';
        setTimeout(() => card.style.boxShadow = '', 600);
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartUI();
}

function updateQty(productId, delta) {
    const item = cart.find(c => c.id === productId);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity < 1) item.quantity = 1;
    updateCartUI();
}

function updateCartUI() {
    const container = document.getElementById('cart-items-container');
    const countEl = document.getElementById('cart-count');
    const totalEl = document.getElementById('cart-total');

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

    countEl.textContent = totalItems;
    totalEl.textContent = `$${totalPrice.toFixed(2)}`;

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <i class="fa-solid fa-bag-shopping"></i>
                <p>Your cart is empty.</p>
                <p class="hint">Ask the AI: "Add the Lunar Prestige Watch to my cart"</p>
            </div>`;
        return;
    }

    container.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img class="cart-item-img" src="${item.image}" alt="${item.name}" onerror="this.src='https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&auto=format'">
            <div class="cart-item-info">
                <div class="cart-item-title">${item.name}</div>
                <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
            </div>
            <div class="cart-item-qty">
                <button class="qty-btn" onclick="updateQty('${item.id}', -1)">−</button>
                <span>${item.quantity}</span>
                <button class="qty-btn" onclick="updateQty('${item.id}', 1)">+</button>
            </div>
            <button class="cart-item-remove" onclick="removeFromCart('${item.id}')"><i class="fa-solid fa-trash"></i></button>
        </div>
    `).join('');
}

/* ══════════════════════════════════════════════
   7. Voice Widget & Recording
   ══════════════════════════════════════════════ */
function initVoiceWidget() {
    const micBtn = document.getElementById('mic-btn');
    micBtn?.addEventListener('click', toggleRecording);
}

function toggleWidget() {
    document.querySelector('.voice-assistant-widget')?.classList.toggle('minimized');
}

function activateVoiceAssistant() {
    const widget = document.querySelector('.voice-assistant-widget');
    if (widget?.classList.contains('minimized')) {
        widget.classList.remove('minimized');
    }
    widget?.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = handleRecordingComplete;
        mediaRecorder.start();
        isRecording = true;

        const micBtn = document.getElementById('mic-btn');
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
        updateStatus('listening', 'Listening...');
        addChatMessage('user-state', '🎤 Listening...');
    } catch (err) {
        console.error('Microphone error:', err);
        addChatMessage('bot', 'Microphone access denied. Please allow microphone permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(t => t.stop());
    }
    isRecording = false;
    const micBtn = document.getElementById('mic-btn');
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    updateStatus('thinking', 'Processing...');
}

async function handleRecordingComplete() {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', blob, 'recording.webm');
    formData.append('asr_mode', asrMode);
    formData.append('tts_mode', ttsMode);

    try {
        const res = await fetch(`${API}/voice`, { method: 'POST', body: formData });
        const data = await res.json();

        // Show transcription
        if (data.transcription) addChatMessage('user', data.transcription);
        // Show agent response
        if (data.response) addChatMessage('bot', data.response);

        // Play TTS audio
        if (data.audio_url) {
            const audio = document.getElementById('agent-voice');
            audio.src = `${API}${data.audio_url}`;
            audio.play().catch(e => console.warn('Audio playback blocked:', e));
        }

        // Handle cart actions
        if (data.cart_action) handleCartAction(data.cart_action);

        updateStatus('idle', 'Idle. Click to speak.');
    } catch (err) {
        console.error('Voice API error:', err);
        addChatMessage('bot', 'Sorry, I had trouble processing that. Is the backend server running?');
        updateStatus('idle', 'Error. Try again.');
    }
}

function handleCartAction(action) {
    if (action.type === 'add') {
        const match = products.find(p =>
            p.name.toLowerCase().includes(action.product?.toLowerCase() || '')
        );
        if (match) {
            addToCart(match.id);
            addChatMessage('bot', `✅ Added "${match.name}" to your cart.`);
        }
    } else if (action.type === 'remove') {
        const match = cart.find(c =>
            c.name.toLowerCase().includes(action.product?.toLowerCase() || '')
        );
        if (match) {
            removeFromCart(match.id);
            addChatMessage('bot', `🗑️ Removed "${match.name}" from your cart.`);
        }
    }
}

function updateStatus(state, text) {
    const indicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const voiceStatus = document.getElementById('voice-status');

    if (indicator) {
        indicator.className = 'status-indicator ' + state;
    }
    if (statusText) statusText.textContent = text;
    if (voiceStatus) voiceStatus.textContent = text;
}

function addChatMessage(type, text) {
    const container = document.getElementById('chat-history');
    // Remove temp state messages
    if (type === 'user-state') {
        const existing = container.querySelector('.state-msg');
        if (existing) existing.remove();
        const div = document.createElement('div');
        div.className = 'chat-message bot state-msg';
        div.innerHTML = `<p>${text}</p>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        return;
    }

    // Remove state msg
    container.querySelector('.state-msg')?.remove();

    const div = document.createElement('div');
    div.className = `chat-message ${type}`;
    div.innerHTML = `<p>${text}</p>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

/* ══════════════════════════════════════════════
   8. Engine Mode Toggles (Online / Offline)
   ══════════════════════════════════════════════ */
function initEngineToggles() {
    // ASR toggle
    const asrToggle = document.getElementById('asr-mode-toggle');
    asrToggle?.querySelectorAll('.switch-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            asrToggle.querySelectorAll('.switch-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            asrMode = btn.dataset.value;
        });
    });

    // TTS toggle
    const ttsToggle = document.getElementById('tts-mode-toggle');
    ttsToggle?.querySelectorAll('.switch-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            ttsToggle.querySelectorAll('.switch-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            ttsMode = btn.dataset.value;
        });
    });
}

/* ══════════════════════════════════════════════
   9. Waveform Visualizer
   ══════════════════════════════════════════════ */
function initWaveform() {
    const canvas = document.getElementById('waveform-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = canvas.offsetWidth * 2;
        canvas.height = canvas.offsetHeight * 2;
    }
    resize();
    window.addEventListener('resize', resize);

    let phase = 0;
    function drawIdle() {
        const w = canvas.width, h = canvas.height;
        ctx.clearRect(0, 0, w, h);

        // Draw subtle ambient waveform
        const barCount = 60;
        const barWidth = w / barCount;
        for (let i = 0; i < barCount; i++) {
            const amp = Math.sin(phase + i * 0.15) * 0.25 + 0.3;
            const barH = amp * h * 0.6;
            const x = i * barWidth;

            const gradient = ctx.createLinearGradient(x, h / 2 - barH / 2, x, h / 2 + barH / 2);
            gradient.addColorStop(0, 'rgba(157, 78, 221, 0.5)');
            gradient.addColorStop(1, 'rgba(255, 0, 127, 0.2)');
            ctx.fillStyle = gradient;
            ctx.fillRect(x + 1, h / 2 - barH / 2, barWidth - 2, barH);
        }
        phase += 0.03;
        requestAnimationFrame(drawIdle);
    }
    drawIdle();
}

/* ══════════════════════════════════════════════
   10. Global Helper Exports
   ══════════════════════════════════════════════ */
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.updateQty = updateQty;
window.filterByCategory = filterByCategory;
window.scrollToCatalog = scrollToCatalog;
window.toggleWidget = toggleWidget;
window.activateVoiceAssistant = activateVoiceAssistant;
