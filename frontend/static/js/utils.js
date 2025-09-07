class Utils {
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="message">${message}</span>
            <button class="close" onclick="this.parentElement.remove()">×</button>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    static formatDate(date) {
        return new Date(date).toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static validateForm(formData, rules) {
        const errors = {};

        for (const [field, value] of formData.entries()) {
            if (rules[field]) {
                const fieldRules = rules[field];

                if (fieldRules.required && !value) {
                    errors[field] = 'Ce champ est requis';
                    continue;
                }

                if (fieldRules.minLength && value.length < fieldRules.minLength) {
                    errors[field] = `Minimum ${fieldRules.minLength} caractères requis`;
                }

                if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
                    errors[field] = `Maximum ${fieldRules.maxLength} caractères autorisés`;
                }

                if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
                    errors[field] = fieldRules.message || 'Format invalide';
                }
            }
        }

        return Object.keys(errors).length === 0 ? null : errors;
    }

    static async loadTemplate(templateId) {
        const template = document.getElementById(templateId);
        if (!template) {
            throw new Error(`Template "${templateId}" not found`);
        }
        return template.content.cloneNode(true);
    }

    static renderForm(formData) {
        const form = document.createElement('form');
        form.className = 'dynamic-form';

        for (const field of formData.fields) {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';

            const label = document.createElement('label');
            label.className = 'form-label';
            label.setAttribute('for', field.id);
            label.textContent = field.label;

            let input;
            switch (field.type) {
                case 'textarea':
                    input = document.createElement('textarea');
                    break;
                case 'select':
                    input = document.createElement('select');
                    field.options.forEach(option => {
                        const opt = document.createElement('option');
                        opt.value = option.value;
                        opt.textContent = option.label;
                        input.appendChild(opt);
                    });
                    break;
                case 'file':
                    input = document.createElement('input');
                    input.type = 'file';
                    input.accept = field.accept || '';
                    input.multiple = field.multiple || false;
                    break;
                default:
                    input = document.createElement('input');
                    input.type = field.type;
            }

            input.className = 'form-control';
            input.id = field.id;
            input.name = field.id;
            input.required = field.required || false;

            if (field.placeholder) {
                input.placeholder = field.placeholder;
            }

            formGroup.appendChild(label);
            formGroup.appendChild(input);
            form.appendChild(formGroup);
        }

        return form;
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static async downloadFile(url, filename) {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();
        } catch (error) {
            console.error('Download failed:', error);
            this.showNotification('Échec du téléchargement du fichier', 'error');
        }
    }

    static sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
}

// Export for use in other modules
window.Utils = Utils;
