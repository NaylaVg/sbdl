/** @odoo-module */

// servicio que rellena la caja de perfil del sidebar
// y el header superior con fecha/hora y nombre de usuario

import { registry } from "@web/core/registry";

const caenProfileService = {
    dependencies: ["orm"],
    start(env, { orm }) {

        // rellena el perfil del sidebar
        const fillProfile = async () => {
            const box = document.getElementById("caen-profile-box");
            if (!box || box.dataset.filled) return;

            const info = await orm.call("res.users", "caen_profile_info", []);
            box.querySelector(".caen-sidebar-profile-name").textContent = "Hola, " + (info.name || "");
            box.querySelector(".caen-sidebar-profile-img").src =
                "/web/image/res.users/" + info.id + "/avatar_128";
            box.dataset.filled = "1";

            // tambien rellena el nombre en el header
            const headerName = document.getElementById("caen-username");
            if (headerName) headerName.textContent = info.name || "";
        };

        // rellena fecha/hora en español
        const meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ];
        const dias = [
            "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"
        ];

        const updateDatetime = () => {
            const el = document.getElementById("caen-datetime");
            if (!el) return;
            const now = new Date();
            const dia = dias[now.getDay()];
            const mes = meses[now.getMonth()];
            const anio = now.getFullYear();
            const horas = String(now.getHours()).padStart(2, "0");
            const mins = String(now.getMinutes()).padStart(2, "0");
            el.textContent = dia + ", " + now.getDate() + " de " + mes + " de " + anio + " — Hora " + horas + ":" + mins;
        };

        const interval = setInterval(() => {
            fillProfile();
            updateDatetime();
            if (document.getElementById("caen-profile-box")?.dataset.filled) {
                clearInterval(interval);
            }
        }, 500);

        updateDatetime();
        setInterval(updateDatetime, 60000);

        setTimeout(() => clearInterval(interval), 15000);
    },
};

registry.category("services").add("caen_profile", caenProfileService);