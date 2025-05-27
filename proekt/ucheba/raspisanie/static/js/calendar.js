document.addEventListener("DOMContentLoaded", function() {
    // Найти все календари на странице
    document.querySelectorAll('.calendar').forEach(function(calendarTable) {
        let today = new Date();
        let currentMonth = today.getMonth();
        let currentYear = today.getFullYear();

        // Проверяем, есть ли контейнер для заголовка и кнопок
        let container = calendarTable.closest('.calendar-container') || calendarTable.parentElement;
        let header = container.querySelector('.calendar-header');
        let monthYearDisplay, prevMonthBtn, nextMonthBtn;

        // Если нет шапки — создаём её
        if (!header) {
            header = document.createElement('div');
            header.className = 'calendar-header';
            prevMonthBtn = document.createElement('button');
            prevMonthBtn.className = 'prev-month';
            prevMonthBtn.textContent = '←';
            monthYearDisplay = document.createElement('h2');
            monthYearDisplay.className = 'month-year';
            nextMonthBtn = document.createElement('button');
            nextMonthBtn.className = 'next-month';
            nextMonthBtn.textContent = '→';
            header.appendChild(prevMonthBtn);
            header.appendChild(monthYearDisplay);
            header.appendChild(nextMonthBtn);
            container.insertBefore(header, calendarTable);
        } else {
            monthYearDisplay = header.querySelector('.month-year');
            prevMonthBtn = header.querySelector('.prev-month');
            nextMonthBtn = header.querySelector('.next-month');
        }

        const daysOfWeek = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
        const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

        function pad(n) { return n < 10 ? '0' + n : n; }

        function updateCalendar() {
            // Очищаем календарь
            calendarTable.tBodies[0].innerHTML = "";

            // Добавляем заголовки дней недели
            const headerRow = document.createElement("tr");
            daysOfWeek.forEach(day => {
                const th = document.createElement("th");
                th.textContent = day;
                headerRow.appendChild(th);
            });
            calendarTable.tBodies[0].appendChild(headerRow);

            // Обновляем отображение месяца и года
            if (monthYearDisplay) {
                monthYearDisplay.textContent = `${months[currentMonth]} ${currentYear}`;
            }

            // Получаем первый день месяца и количество дней в месяце
            const firstDay = new Date(currentYear, currentMonth, 1);
            const lastDay = new Date(currentYear, currentMonth + 1, 0);
            const daysInMonth = lastDay.getDate();
            const startingDay = firstDay.getDay() || 7; // Преобразуем воскресенье (0) в 7

            let day = 1;
            let row = document.createElement("tr");

            // Добавляем пустые ячейки до первого дня месяца
            for (let i = 1; i < startingDay; i++) {
                row.appendChild(document.createElement("td"));
            }

            // Добавляем дни месяца
            for (let i = startingDay; i <= 7; i++) {
                if (day <= daysInMonth) {
                    const cell = createDayCell(day);
                    row.appendChild(cell);
                    day++;
                }
            }
            calendarTable.tBodies[0].appendChild(row);

            // Добавляем оставшиеся дни
            while (day <= daysInMonth) {
                row = document.createElement("tr");
                for (let i = 1; i <= 7 && day <= daysInMonth; i++) {
                    const cell = createDayCell(day);
                    row.appendChild(cell);
                    day++;
                }
                calendarTable.tBodies[0].appendChild(row);
            }
        }

        function createDayCell(day) {
            const cell = document.createElement("td");
            cell.textContent = day;
            cell.style.cursor = 'pointer';
            const date = new Date(currentYear, currentMonth, day);
            const dateStr = `${currentYear}-${pad(currentMonth + 1)}-${pad(day)}`;
            if (day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
                cell.classList.add("today");
            }
            cell.addEventListener('click', function() {
                window.location.href = `/schedule/table/?date=${dateStr}`;
            });
            return cell;
        }

        // Обработчики кнопок переключения месяцев
        if (prevMonthBtn) {
            prevMonthBtn.onclick = function() {
                if (currentMonth === 0) {
                    currentMonth = 11;
                    currentYear--;
                } else {
                    currentMonth--;
                }
                updateCalendar();
            };
        }
        if (nextMonthBtn) {
            nextMonthBtn.onclick = function() {
                if (currentMonth === 11) {
                    currentMonth = 0;
                    currentYear++;
                } else {
                    currentMonth++;
                }
                updateCalendar();
            };
        }

        // Инициализация календаря
        updateCalendar();
    });
});
