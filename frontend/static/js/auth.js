class Auth {
    static isAuthenticated = false;
    static currentUser = null;
    static TOKEN_KEY = 'auth_token';

    static async init() {
        const token = localStorage.getItem(this.TOKEN_KEY);
        if (token) {
            try {
                const user = await API.getCurrentUser();
                if (user) {
                    this.setCurrentUser(user);
                    return true;
                }
            } catch (error) {
                console.error('Failed to initialize auth:', error);
                this.logout();
            }
        }
        return false;
    }

    static async login(email, password) {
        try {
            const response = await API.login(email, password);
            if (response && response.token) {
                localStorage.setItem(this.TOKEN_KEY, response.token);
                this.setCurrentUser(response.user);
                return true;
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw new Error('Échec de la connexion. Veuillez vérifier vos identifiants.');
        }
        return false;
    }

    static logout() {
        this.isAuthenticated = false;
        this.currentUser = null;
        localStorage.removeItem(this.TOKEN_KEY);
        window.location.href = '/login';
    }

    static setCurrentUser(user) {
        this.currentUser = user;
        this.isAuthenticated = true;
        this.updateUI();
    }

    static updateUI() {
        const userInfo = document.getElementById('userInfo');
        if (!userInfo) return;

        if (this.isAuthenticated && this.currentUser) {
            userInfo.innerHTML = `
                <div class="user-profile">
                    <span class="user-name">${this.currentUser.name}</span>
                    <div class="user-role">${this.currentUser.role}</div>
                    <button class="btn btn-logout" onclick="Auth.logout()">
                        <i class="fas fa-sign-out-alt"></i> Déconnexion
                    </button>
                </div>
            `;
        } else {
            userInfo.innerHTML = `
                <button class="btn btn-login" onclick="window.location.href='/login'">
                    <i class="fas fa-sign-in-alt"></i> Connexion
                </button>
            `;
        }

        this.updateMenu();
    }

    static updateMenu() {
        const sidebarMenu = document.getElementById('sidebarMenu');
        if (!sidebarMenu) return;

        const menuItems = [];

        if (this.isAuthenticated) {
            // Common menu items for all authenticated users
            menuItems.push(
                { icon: 'fas fa-home', text: 'Accueil', href: '/' },
                { icon: 'fas fa-list', text: 'Formulaires', href: '/forms' }
            );

            // Role-specific menu items
            if (this.currentUser.role === 'admin') {
                menuItems.push(
                    { icon: 'fas fa-users', text: 'Utilisateurs', href: '/users' },
                    { icon: 'fas fa-building', text: 'Sous-sites', href: '/subsites' }
                );
            }

            menuItems.push(
                { icon: 'fas fa-envelope', text: 'Messages', href: '/messages' },
                { icon: 'fas fa-ticket-alt', text: 'Tickets', href: '/tickets' }
            );
        }

        // Generate menu HTML
        sidebarMenu.innerHTML = menuItems.map(item => `
            <li class="menu-item">
                <a href="${item.href}">
                    <i class="${item.icon}"></i>
                    <span>${item.text}</span>
                </a>
            </li>
        `).join('');
    }

    static hasPermission(permission) {
        if (!this.isAuthenticated || !this.currentUser) return false;

        // Admin has all permissions
        if (this.currentUser.role === 'admin') return true;

        // Check specific permissions based on role
        const rolePermissions = {
            subadmin: ['view_forms', 'edit_forms', 'view_users', 'view_messages'],
            user: ['view_forms', 'view_messages']
        };

        return rolePermissions[this.currentUser.role]?.includes(permission) || false;
    }
}

// Export for use in other modules
window.Auth = Auth;
