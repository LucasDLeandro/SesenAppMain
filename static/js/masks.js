/**
 * masks.js
 * Aplicação global de máscaras utilizando a biblioteca IMask.
 * 
 * Este arquivo procura por inputs com as classes:
 * - .mask-telefone
 * - .mask-cpf
 * - .mask-portaria
 * E aplica a máscara correspondente.
 */

function cleanTelefoneForMask(val) {
    if (!val) return val;
    val = val.replace(/\D/g, ''); // só dígitos
    if (val.startsWith('55') && val.length >= 12) {
        val = val.substring(2);
    }
    return val;
}

function aplicarMascarasGlobais() {
    document.querySelectorAll('.mask-telefone:not(.imask-aplicado)').forEach(input => {
        // Remove 55 do backend se houver antes de aplicar a máscara
        input.value = cleanTelefoneForMask(input.value);
        IMask(input, { mask: '(00) 0 0000-0000' });
        input.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-cpf:not(.imask-aplicado)').forEach(input => {
        IMask(input, { mask: '000.000.000-00' });
        input.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-cnpj:not(.imask-aplicado)').forEach(input => {
        IMask(input, { mask: '00.000.000/0000-00' });
        input.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-cep:not(.imask-aplicado)').forEach(input => {
        IMask(input, { mask: '00000-000' });
        input.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-rg:not(.imask-aplicado)').forEach(input => {
        // RGs vary by state. The best approach for RG is a flexible mask, but usually it's just numbers.
        // We'll allow up to 14 numbers. If user pastes with dots/dashes, we strip them.
        IMask(input, { 
            mask: /^[0-9A-Za-z]{1,14}$/,
            prepare: function (str) {
                return str.replace(/[\.\-]/g, ''); // strip dots and dashes on input
            }
        });
        input.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-portaria:not(.imask-aplicado)').forEach(input => {
        IMask(input, {
            mask: 'Portaria num',
            blocks: {
                num: { mask: Number, min: 1, max: 999999 }
            }
        });
        input.classList.add('imask-aplicado');
    });

    // Formatação em textos estáticos (apenas visualização)
    const pipeTelefone = IMask.createPipe({ mask: '(00) 0 0000-0000' });
    document.querySelectorAll('.format-telefone:not(.imask-aplicado)').forEach(el => {
        let val = el.innerText || el.textContent;
        if (val) {
            val = cleanTelefoneForMask(val);
            el.innerText = pipeTelefone(val);
        }
        el.classList.add('imask-aplicado');
    });

    const pipeCpf = IMask.createPipe({ mask: '000.000.000-00' });
    document.querySelectorAll('.format-cpf:not(.imask-aplicado)').forEach(el => {
        let val = el.innerText || el.textContent;
        if (val) {
            el.innerText = pipeCpf(val.replace(/\D/g, ''));
        }
        el.classList.add('imask-aplicado');
    });

    document.querySelectorAll('.mask-moeda:not(.imask-aplicado)').forEach(input => {
        IMask(input, {
            mask: Number,
            scale: 2,
            signed: false,
            thousandsSeparator: '.',
            padFractionalZeros: true,
            normalizeZeros: true,
            radix: ',',
            mapToRadix: ['.']
        });
        input.classList.add('imask-aplicado');
    });
    document.querySelectorAll('.format-text:not(.format-aplicado)').forEach(input => {
        input.addEventListener('blur', function() {
            let val = this.value.trim();
            if(val) {
                const preposicoes = ["de", "da", "do", "das", "dos", "e"];
                val = val.toLowerCase().split(" ").map((word, index, arr) => {
                    if(!word) return "";
                    if (index > 0 && preposicoes.includes(word)) return word;
                    return word.charAt(0).toUpperCase() + word.slice(1);
                }).join(" ");
                this.value = val;
            }
        });
        input.classList.add('format-aplicado');
    });

    document.querySelectorAll('.uppercase-text:not(.format-aplicado)').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
        input.classList.add('format-aplicado');
    });
}

document.addEventListener("DOMContentLoaded", () => {
    aplicarMascarasGlobais();
});

// Chamar quando o body sofrer mutações (ex: modais abertos via htmx/fetch)
const observer = new MutationObserver(mutations => {
    aplicarMascarasGlobais();
});
observer.observe(document.body, { childList: true, subtree: true });
