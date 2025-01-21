document.addEventListener('DOMContentLoaded', function() {
    const animationContainer = document.getElementById('animation-container');
    const speedControl = document.getElementById('speed-control');
    const userImageUpload = document.getElementById('user-image-upload');
    const startAnimationButton = document.getElementById('start-animation');
    const resetAnimationButton = document.getElementById('reset-animation');

    let animationSpeed = 5;
    let currentStep = 1;
    let userImage = null;

    // Обработчик изменения скорости
    speedControl.addEventListener('input', function() {
        animationSpeed = parseInt(this.value);
    });

    // Обработчик загрузки изображения
    userImageUpload.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file && file.type === 'image/jpeg' && file.size <= 300 * 1024) {
            const reader = new FileReader();
            reader.onload = function(e) {
                userImage = createImageElement(e.target.result);
                makeDraggable(userImage);
                makeResizable(userImage);
            };
            reader.readAsDataURL(file);
        } else {
            alert('Пожалуйста, загрузите изображение в формате JPG размером не более 300 KB.');
        }
    });

    // Создание элемента изображения
    function createImageElement(src) {
        const img = document.createElement('img');
        img.src = src;
        img.style.width = '100px';
        img.classList.add('draggable');
        animationContainer.appendChild(img);
        return img;
    }

    // Перетаскивание
    function makeDraggable(element) {
        let isDragging = false;
        let offsetX, offsetY;

        element.addEventListener('mousedown', function(e) {
            isDragging = true;
            offsetX = e.clientX - element.getBoundingClientRect().left;
            offsetY = e.clientY - element.getBoundingClientRect().top;
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                element.style.left = `${e.clientX - offsetX}px`;
                element.style.top = `${e.clientY - offsetY}px`;
            }
        });

        document.addEventListener('mouseup', function() {
            isDragging = false;
        });
    }

    // Изменение размера
    function makeDraggable(element) {
    console.log("Элемент подготовлен для перетаскивания:", element);
    let isDragging = false;
    let offsetX, offsetY;

    element.addEventListener('mousedown', function(e) {
        console.log("Начато перетаскивание");
        isDragging = true;
        offsetX = e.clientX - element.getBoundingClientRect().left;
        offsetY = e.clientY - element.getBoundingClientRect().top;
    });

    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            console.log("Перетаскивание...");
            element.style.left = `${e.clientX - offsetX}px`;
            element.style.top = `${e.clientY - offsetY}px`;
        }
    });

    document.addEventListener('mouseup', function() {
        console.log("Перетаскивание завершено");
        isDragging = false;
    });
}

    // Запуск анимации
    function startAnimation() {
        animateSteps();
    }

    // Сброс анимации
    function resetAnimation() {
        currentStep = 1;
        resetSteps();
    }

    // Логика этапов
function animateSteps() {
    console.log("Текущий этап:", currentStep);
    const steps = document.querySelectorAll('.animation-step');
    steps.forEach((step, index) => {
        if (index + 1 === currentStep) {
            console.log("Отображаем этап:", index + 1);
            step.style.display = 'block';
        } else {
            step.style.display = 'none';
        }
    });

    if (currentStep < 4) {
        currentStep++;
        setTimeout(animateSteps, 1000 / animationSpeed);
    } else {
        console.log("Анимация завершена");
    }
}

    // Сброс этапов
    function resetSteps() {
        const steps = document.querySelectorAll('.animation-step');
        steps.forEach(step => step.style.display = 'none');
        steps[0].style.display = 'block';
    }

    // Обработчики кнопок
    startAnimationButton.addEventListener('click', startAnimation);
    resetAnimationButton.addEventListener('click', resetAnimation);
});
const clubImages = [
    '{% static "images/club1.png" %}',
    '{% static "images/club2.png" %}',
    '{% static "images/club3.png" %}',
];

clubImages.forEach((src, index) => {
    const clubImage = createImageElement(src);
    makeDraggable(clubImage);
    makeResizable(clubImage);
});
console.log("Скрипт animation.js загружен!");


//ПРОВЕРКА
startAnimationButton.addEventListener('click', function() {
    console.log("Нажата кнопка 'Начать анимацию'");
    startAnimation();
});

resetAnimationButton.addEventListener('click', function() {
    console.log("Нажата кнопка 'Сбросить'");
    resetAnimation();
});
