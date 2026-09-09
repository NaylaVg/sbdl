
//  vigila el cambio de rol en la pestana Permisos CAEN, cuando el jefe cambia el rol, el onchange en Python
// actualiza las casillas de permisos en tiempo real 

import { registry } from "@web/core/registry";

const caenRoleService = {
    dependencies: ["action"],
    start(env, { action }) {
        const attach = () => {
            // busca todos los radios del campo caen_role
            document.querySelectorAll(
                'input[type="radio"][name="caen_role"]'
            ).forEach((r) => {
                // evita agregar listener duplicados
                if (!r.dataset.caenWatcher) {
                    r.dataset.caenWatcher = "1";
                    r.addEventListener("change", () => {
                        // espera 200ms a que el onchange de Python se ejecute
                        setTimeout(() => {
                            // busca el boton guardar y lo clickea
                            const save = document.querySelector('.o_save_button, .o_form_button_save');
                            if (save) save.click();
                            // despues de 600ms recarga la pagina
                            setTimeout(() => {
                                action.doAction(
                                    { type: "ir.actions.client", tag: "soft_reload" },
                                    { clearBreadcrumbs: false }
                                );
                            }, 600);
                        }, 200);
                    });
                }
            });
        };

        // observa cambios en el DOM para detectar cuando se carga la pestaña de permisos y agregar los listeners a los radios
        const obs = new MutationObserver(attach);
        obs.observe(document.body, { childList: true, subtree: true });
        attach();
    },
};

// registra el servicio para que se ejecute al cargar el backend
registry.category("services").add("caen_role_watcher", caenRoleService);