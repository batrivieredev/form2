class App {
    static routes = {
        '/': { template: 'homeTemplate', title: 'Accueil' },
        '/login': { template: 'loginTemplate', title: 'Connexion' },
        '/forms': { template: 'formsTemplate', title: 'Formulaires', auth: true },
        '/forms/new': { template: 'formEditorTemplate', title: 'Nouveau Formulaire', auth: true },
        '/forms/:id': { template: 'formViewTemplate', title: 'Voir Formulaire', auth: true },
        '/forms/:id/edit': { template: 'formEditorTemplate', title: 'Éditer Formulaire', auth: true },
        '/messages': { template: 'messagesTemplate', title: 'Messages', auth: true },
        '/tickets': { template: 'ticketsTemplate', title: 'Tickets', auth: true },
        '/users': { template: 'usersTemplate', title: 'Utilisateurs', auth: true, admin: true },
        '/subsites': { template: 'subsitesTemplate', title: 'Sous-sites', auth: true, admin: true }
    };

    static async init() {
        // Initialize authentication
        const isAuthenticated = await Auth.init();

        // Set up navigation handling
        window.addEventListener('popstate', () => this.handleRoute());
        document.addEventListener('click', e => {
            if (e.target.matches('a[href]')) {
                e.preventDefault();
                const href = e.target.getAttribute('href');
                this.navigateTo(href);
            }
        });

        // Handle initial route
        await this.handleRoute();
    }

    static async handleRoute() {
        const path = window.location.pathname;
        let route = this.routes[path];

        // Handle dynamic routes
        if (!route) {
            const dynamicRoute = Object.entries(this.routes).find(([pattern]) => {
                return this.matchDynamicRoute(path, pattern);
            });

            if (dynamicRoute) {
                route = dynamicRoute[1];
            }
        }

        // Route not found
        if (!route) {
            this.showError('Page non trouvée', 404);
            return;
        }

        // Check authentication
        if (route.auth && !Auth.isAuthenticated) {
            this.navigateTo('/login');
            return;
        }

        // Check admin permission
        if (route.admin && (!Auth.currentUser || Auth.currentUser.role !== 'admin')) {
            this.showError('Accès non autorisé', 403);
            return;
        }

        try {
            // Update page title
            document.title = `${route.title} - Form`;

            // Load and render template
            const content = await Utils.loadTemplate(route.template);
            const mainContent = document.getElementById('mainContent');
            mainContent.innerHTML = '';
            mainContent.appendChild(content);

            // Initialize page-specific functionality
            await this.initializePage(path, route);

        } catch (error) {
            console.error('Error handling route:', error);
            this.showError('Une erreur est survenue');
        }
    }

    static matchDynamicRoute(path, pattern) {
        const patternParts = pattern.split('/');
        const pathParts = path.split('/');

        if (patternParts.length !== pathParts.length) return false;

        return patternParts.every((part, i) => {
            if (part.startsWith(':')) return true;
            return part === pathParts[i];
        });
    }

    static async initializePage(path, route) {
        switch (route.template) {
            case 'loginTemplate':
                this.initializeLoginPage();
                break;
            case 'formsTemplate':
                await this.initializeFormsPage();
                break;
            case 'formEditorTemplate':
                const formId = path.match(/\/forms\/(\d+)\/edit/)?.[1];
                await this.initializeFormEditor(formId);
                break;
            case 'formViewTemplate':
                const viewFormId = path.match(/\/forms\/(\d+)$/)?.[1];
                await this.initializeFormView(viewFormId);
                break;
            case 'messagesTemplate':
                await this.initializeMessagesPage();
                break;
            case 'ticketsTemplate':
                await this.initializeTicketsPage();
                break;
            // Add other page initializations as needed
        }
    }

    static initializeLoginPage() {
        const form = document.getElementById('loginForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = form.email.value;
            const password = form.password.value;

            try {
                const success = await Auth.login(email, password);
                if (success) {
                    this.navigateTo('/');
                }
            } catch (error) {
                Utils.showNotification(error.message, 'error');
            }
        });
    }

    static async initializeFormsPage() {
        try {
            const forms = await API.getForms();
            const container = document.querySelector('.forms-list');
            if (!container) return;

            container.innerHTML = forms.map(form => `
                <div class="form-card">
                    <h3>${Utils.sanitizeHTML(form.title)}</h3>
                    <p>${Utils.sanitizeHTML(form.description)}</p>
                    <div class="form-actions">
                        <a href="/forms/${form.id}" class="btn btn-view">
                            <i class="fas fa-eye"></i> Voir
                        </a>
                        ${Auth.hasPermission('edit_forms') ? `
                            <a href="/forms/${form.id}/edit" class="btn btn-edit">
                                <i class="fas fa-edit"></i> Éditer
                            </a>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            Utils.showNotification('Erreur lors du chargement des formulaires', 'error');
        }
    }

    static navigateTo(url) {
        window.history.pushState(null, '', url);
        this.handleRoute();
    }

    static showError(message, code = 500) {
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="error-container">
                <h1>${code}</h1>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="App.navigateTo('/')">
                    Retour à l'accueil
                </button>
            </div>
        `;
    }
}

// Export for use in other modules
window.App = App;
