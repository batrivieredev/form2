document.addEventListener('DOMContentLoaded', () => {
    console.log('Messagerie chargée');

    const form = document.querySelector('form');
    form.addEventListener('submit', () => {
        console.log('Message envoyé');
    });
});
