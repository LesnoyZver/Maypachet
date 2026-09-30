// Общее поведение, используемое на нескольких страницах:
// меню аккаунта в шапке и открытие/закрытие модальных окон.
// Логика, специфичная для конкретной страницы (таблица техники,
// формы входа/регистрации), находится в самом HTML-файле каждой страницы.

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("account-trigger")) initAccountMenu();
    initModalGenerics();
    initLogoLink();
});

function initLogoLink() {
    const logo = document.querySelector(".logo-block");
    if (!logo) return;
    logo.style.cursor = "pointer";
    logo.addEventListener("click", () => {
        // equipment-table-body есть только на главной странице — по нему и определяем,
        // где мы находимся, а не по URL (не зависит от того, как страница смонтирована на бэкенде).
        if (document.getElementById("equipment-table-body")) {
            location.reload();
        } else {
            window.location.href = "equipment.html";
        }
    });
}

function initAccountMenu() {
    const trigger = document.getElementById("account-trigger");
    const menu = document.getElementById("account-menu");
    if (!trigger || !menu) return;

    trigger.addEventListener("click", (e) => {
        e.stopPropagation();
        // closeAllActionsMenus определена только на equipment.html — если её нет,
        // на этой странице просто нечего закрывать, кроме самого меню аккаунта.
        if (typeof closeAllActionsMenus === "function") closeAllActionsMenus();
        menu.classList.toggle("open");
    });

    document.addEventListener("click", () => menu.classList.remove("open"));

    menu.querySelectorAll(".actions-menu-item").forEach((item) => {
        item.addEventListener("click", (e) => {
            e.stopPropagation();
            menu.classList.remove("open");
            const action = item.dataset.action;
            if (action === "settings") {
                window.location.href = "profile.html";
            } else if (action === "logout") {
                fetch("/auth/logout", { method: "POST" }).finally(() => {
                    window.location.href = "login.html";
                });
            }
        });
    });
}

function initModalGenerics() {
    document.querySelectorAll("[data-close]").forEach((b) => {
        b.addEventListener("click", () => closeModal(b.dataset.close));
    });
    document.querySelectorAll(".modal-overlay").forEach((overlay) => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) closeModal(overlay.id);
        });
    });
}

function openModal(id) { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }
