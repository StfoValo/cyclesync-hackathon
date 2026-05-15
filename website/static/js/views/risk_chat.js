/**
 * Risk Chat Module
 * AI-powered chatbot for the Risk Summary tab.
 * Sends user messages to the AI API and streams responses.
 */

export function initRiskChat() {
    const input = document.getElementById('risk-chat-input');
    const sendBtn = document.getElementById('risk-chat-send');
    const messagesArea = document.getElementById('risk-chat-messages');

    if (!input || !sendBtn || !messagesArea) return;

    // Send on click
    sendBtn.addEventListener('click', () => sendMessage());

    // Send on Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Suggested question chips
    document.querySelectorAll('.suggested-q').forEach(btn => {
        btn.addEventListener('click', () => {
            input.value = btn.textContent;
            sendMessage();
        });
    });

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Clear input
        input.value = '';

        // Hide suggestions after first message
        const suggestions = document.getElementById('risk-chat-suggestions');
        if (suggestions) suggestions.classList.add('hidden');

        // Add user message bubble
        appendMessage('user', message);

        // Add AI thinking indicator
        const thinkingId = 'ai-thinking-' + Date.now();
        appendThinking(thinkingId);

        // Scroll to bottom
        messagesArea.scrollTop = messagesArea.scrollHeight;

        try {
            const lang = localStorage.getItem('cyclesync_lang') || 'en';
            const response = await fetch(`/api/ai/chat?message=${encodeURIComponent(message)}&context=risk_summary&lang=${lang}`);

            if (!response.ok) throw new Error("HTTP error " + response.status);

            // Remove thinking indicator
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();

            // Stream the response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            const aiMsgId = 'ai-msg-' + Date.now();
            appendMessage('ai', '', aiMsgId);
            const contentEl = document.getElementById(aiMsgId);

            let fullText = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;

                // Format markdown-like content
                let formatted = fullText;
                formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="text-brand-400">$1</strong>');
                formatted = formatted.replace(/^\* (.*?)(?:\n|$)/gm, '<div class="flex items-start gap-2 mt-1"><span class="text-brand-500 mt-0.5">•</span><span>$1</span></div>');
                formatted = formatted.replace(/\n/g, '<br>');

                if (contentEl) contentEl.innerHTML = formatted;
                messagesArea.scrollTop = messagesArea.scrollHeight;
            }
        } catch (error) {
            console.error('Chat error:', error);
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();
            appendMessage('ai', 'Connection error. The AI service may be temporarily unavailable. Please try again.');
        }
    }

    function appendMessage(role, content, id = null) {
        const div = document.createElement('div');
        div.className = 'flex items-start gap-3';

        if (role === 'user') {
            div.innerHTML = `
            <div class="ml-auto flex items-start gap-3 max-w-[85%]">
                <div class="bg-brand-600/20 rounded-xl rounded-tr-sm px-4 py-3 border border-brand-500/20">
                    <p class="text-sm text-white leading-relaxed">${escapeHTML(content)}</p>
                </div>
                <div class="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center shrink-0 border border-slate-600 mt-0.5">
                    <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </div>
            </div>`;
        } else {
            const msgId = id ? `id="${id}"` : '';
            div.innerHTML = `
            <div class="w-7 h-7 rounded-full bg-brand-600/30 flex items-center justify-center shrink-0 border border-brand-500/30 mt-0.5">
                <svg class="w-3.5 h-3.5 text-brand-400" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l1.8 5.5H20l-4.6 3.3 1.8 5.5L12 13l-5.2 3.3 1.8-5.5L4 7.5h6.2z"/></svg>
            </div>
            <div class="bg-slate-800/60 rounded-xl rounded-tl-sm px-4 py-3 max-w-[85%] border border-white/5">
                <p ${msgId} class="text-sm text-slate-300 leading-relaxed">${content}</p>
            </div>`;
        }

        messagesArea.appendChild(div);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function appendThinking(id) {
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex items-start gap-3';
        div.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-brand-600/30 flex items-center justify-center shrink-0 border border-brand-500/30 mt-0.5">
            <svg class="w-3.5 h-3.5 text-brand-400" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l1.8 5.5H20l-4.6 3.3 1.8 5.5L12 13l-5.2 3.3 1.8-5.5L4 7.5h6.2z"/></svg>
        </div>
        <div class="bg-slate-800/60 rounded-xl rounded-tl-sm px-4 py-3 border border-white/5">
            <div class="flex items-center gap-2">
                <div class="flex gap-1">
                    <div class="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
                <span class="text-xs text-slate-500">Analyzing...</span>
            </div>
        </div>`;
        messagesArea.appendChild(div);
    }

    function escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}
