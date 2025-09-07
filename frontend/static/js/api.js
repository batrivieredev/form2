class API {
    static BASE_URL = '/api/v1';
    static TOKEN_KEY = 'auth_token';

    static async request(endpoint, options = {}) {
        const token = localStorage.getItem(this.TOKEN_KEY);
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    localStorage.removeItem(this.TOKEN_KEY);
                    window.location.href = '/login';
                    return null;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth endpoints
    static async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    static async logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        window.location.href = '/login';
    }

    static async getCurrentUser() {
        return this.request('/auth/me', { method: 'GET' });
    }

    // Forms endpoints
    static async getForms() {
        return this.request('/forms', { method: 'GET' });
    }

    static async getForm(formId) {
        return this.request(`/forms/${formId}`, { method: 'GET' });
    }

    static async createForm(formData) {
        return this.request('/forms', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
    }

    static async updateForm(formId, formData) {
        return this.request(`/forms/${formId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
    }

    static async deleteForm(formId) {
        return this.request(`/forms/${formId}`, { method: 'DELETE' });
    }

    // Messages endpoints
    static async getMessages() {
        return this.request('/messages', { method: 'GET' });
    }

    static async sendMessage(messageData) {
        return this.request('/messages', {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    }

    // Tickets endpoints
    static async getTickets() {
        return this.request('/tickets', { method: 'GET' });
    }

    static async createTicket(ticketData) {
        return this.request('/tickets', {
            method: 'POST',
            body: JSON.stringify(ticketData)
        });
    }

    // Files endpoints
    static async uploadFile(formData) {
        return this.request('/files/upload', {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set correct Content-Type for FormData
        });
    }

    static async getFiles() {
        return this.request('/files', { method: 'GET' });
    }
}

// Export for use in other modules
window.API = API;
