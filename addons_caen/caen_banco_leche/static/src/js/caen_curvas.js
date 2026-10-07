/** @odoo-module */

// grafico de curvas de crecimiento del bebe
// dibujo las lineas de referencia (intergrowth u oms) y los puntos del bebe
// con chartjs que ya trae odoo en el bundle web.chartjs_lib

import { Component, onWillStart, onWillUnmount, useEffect, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";
import { rpc } from "@web/core/network/rpc";

class CaenCurvas extends Component {
    static template = "caen_banco_leche.CaenCurvas";

    setup() {
        this.canvasRef = useRef("canvas");
        this.state = useState({ medida: "peso", datos: null, error: null });
        this.chart = null;
        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            const pid = this.props.action.params?.patient_id;
            if (!pid) {
                this.state.error = "sin paciente";
                return;
            }
            try {
                this.state.datos = await rpc(`/caen/curvas/${pid}`);
                if (this.state.datos?.error) {
                    this.state.error = this.state.datos.error;
                }
            } catch (e) {
                this.state.error = "no pude cargar los datos";
            }
        });
        // dibujo despues de cada render porque antes el canvas no existe
        useEffect(() => this.dibuja());
        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }

    get medidas() {
        // las tres pestanas del grafico con su unidad
        return [
            { id: "peso", nombre: "Peso (g)" },
            { id: "talla", nombre: "Talla (cm)" },
            { id: "pc", nombre: "Perímetro cefálico (cm)" },
        ];
    }

    cambia(medida) {
        // cambio de pestana y redibujo
        this.state.medida = medida;
        this.dibuja();
    }

    dibuja() {
        const d = this.state.datos;
        if (!d || !this.canvasRef.el) {
            return;
        }
        if (this.chart) {
            this.chart.destroy();
        }
        const med = this.state.medida;
        const esPma = d.prematuro;
        // colores de cada linea, la del medio mas fuerte
        const colores = {
            P3: "#9e9e9e", P25: "#90caf9", P50: "#1e88e5",
            P75: "#90caf9", P97: "#9e9e9e",
        };
        // convierto cada linea de referencia a un dataset de chartjs
        const sets = d.refs[med].map((l) => ({
            label: l.nombre,
            data: l.puntos.map((p) => ({ x: p[0], y: p[1] })),
            borderColor: colores[l.nombre] || "#9e9e9e",
            borderWidth: l.nombre === "P50" ? 2 : 1,
            borderDash: l.nombre === "P50" ? [] : [5, 4],
            pointRadius: 0,
            fill: false,
            tension: 0.2,
        }));
        // convierto los puntos del bebe, guardo z y fecha para el tooltip
        const pts = (d.puntos[med] || []).map((p) => ({
            x: esPma ? p.pma : p.dias,
            y: p.valor,
            z: p.z,
            fecha: p.fecha,
        }));
        // agrego al bebe como ultima serie en rojo y con puntos grandes
        sets.push({
            label: d.paciente,
            data: pts,
            borderColor: "#e53935",
            backgroundColor: "#e53935",
            borderWidth: 2,
            pointRadius: 5,
            fill: false,
            tension: 0,
        });
        // creo el grafico en el canvas
        this.chart = new Chart(this.canvasRef.el, {
            type: "line",
            data: { datasets: sets },
            options: {
                responsive: true,
                parsing: false,
                plugins: {
                    // titulo con nombre del bebe y que estandar usa
                    title: {
                        display: true,
                        text: `${d.paciente} - ${med} (${esPma ? "intergrowth prematuro" : "oms"})`,
                    },
                    // al pasar el mouse muestro valor, z y fecha en los puntos del bebe
                    tooltip: {
                        callbacks: {
                            label: (c) =>
                                c.dataset.label === d.paciente && c.raw.z != null
                                    ? ` ${c.raw.y} (z ${c.raw.z}, ${c.raw.fecha})`
                                    : ` ${c.dataset.label}: ${c.raw.y}`,
                        },
                    },
                },
                scales: {
                    x: { type: "linear", title: { display: true, text: d.eje } },
                    y: { title: { display: true, text: med } },
                },
            },
        });
    }
}

// registro mi accion para abrirla con el tag caen_curvas desde el boton
registry.category("actions").add("caen_curvas", CaenCurvas);