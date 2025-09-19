// JS pour le dashboard super admin (ex: alert au clic)
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', () => {
            console.log('Lien cliqué : ' + link.textContent);
        });
    });
});
