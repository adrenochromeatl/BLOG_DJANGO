// Основной JavaScript для блога
document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('form[method="post"] button[type="submit"]');
    deleteButtons.forEach(button => {
        if (button.textContent.includes('Удалить')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Вы уверены, что хотите выполнить это действие?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Плавная прокрутка
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Автоматическое скрытие alert сообщений
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});