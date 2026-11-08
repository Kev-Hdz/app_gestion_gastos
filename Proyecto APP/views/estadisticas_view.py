from typing import Callable, Optional
import flet as ft
from database.db_manager import DBManager
from models.movimiento import ICONOS, moneda
from components.variance_chart import crear_tarjeta_grafica_varianza


class EstadisticasView(ft.Column):
    """Vista analítica con gráfica de varianza y picos (Gastos vs Comida) y desglose por categoría."""

    def __init__(
        self,
        db: DBManager,
        on_cambiar_periodo: Optional[Callable[[Optional[int]], None]] = None,
    ):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.on_cambiar_periodo = on_cambiar_periodo
        self.periodo_dias: Optional[int] = None

        self.selector_periodo = ft.SegmentedButton(
            selected=["todos"],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value="todos", label=ft.Text("Todos")),
                ft.Segment(value="15", label=ft.Text("15 días")),
                ft.Segment(value="30", label=ft.Text("30 días")),
            ],
            on_change=self._al_cambiar_segmento,
        )

        self.contenedor_tarjeta_total = ft.Container()
        self.contenedor_grafica_varianza = ft.Container()
        self.columna_categorias = ft.Column(spacing=14)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Estadísticas de Gastos", size=24, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.INSIGHTS, color=ft.Colors.TEAL_700),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.selector_periodo],
            ),
            self.contenedor_tarjeta_total,
            self.contenedor_grafica_varianza,
            ft.Text("Desglose por Categoría", size=18, weight=ft.FontWeight.W_600),
            self.columna_categorias,
        ]
        self.actualizar_datos()

    def _al_cambiar_segmento(self, e):
        """Manejador al cambiar la selección en el SegmentedButton."""
        val = self.selector_periodo.selected[0] if self.selector_periodo.selected else "todos"
        if val == "15":
            self.periodo_dias = 15
        elif val == "30":
            self.periodo_dias = 30
        else:
            self.periodo_dias = None

        if self.on_cambiar_periodo:
            self.on_cambiar_periodo(self.periodo_dias)
        else:
            self.actualizar_datos(self.periodo_dias)

    def establecer_periodo(self, dias: Optional[int]):
        """Sincroniza el selector visual con un período específico."""
        self.periodo_dias = dias
        if dias == 15:
            self.selector_periodo.selected = ["15"]
        elif dias == 30:
            self.selector_periodo.selected = ["30"]
        else:
            self.selector_periodo.selected = ["todos"]

    def actualizar_datos(self, dias: Optional[int] = None):
        """Calcula y refresca las métricas de gasto, la gráfica de picos y el desglose."""
        if dias is not None:
            self.establecer_periodo(dias)
        else:
            dias = self.periodo_dias

        resumen = self.db.obtener_resumen(dias=dias)
        total_gastos = resumen["gastos"]
        categorias = self.db.obtener_gastos_por_categoria(dias=dias)
        datos_flujo = self.db.obtener_datos_grafica_ingresos_gastos(dias=dias)

        if dias == 15:
            periodo_txt = "Últimos 15 días"
        elif dias == 30:
            periodo_txt = "Últimos 30 días"
        else:
            periodo_txt = "Histórico Total"

        # Tarjeta resumen de gastos para el período
        self.contenedor_tarjeta_total.content = ft.Container(
            padding=18,
            border_radius=14,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(f"Gasto Total ({periodo_txt})", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(moneda(total_gastos), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=12,
                        bgcolor=ft.Colors.RED_50,
                        content=ft.Icon(ft.Icons.PIE_CHART_OUTLINE, color=ft.Colors.RED_700, size=24),
                    ),
                ],
            ),
        )

        # Sección gráfica de flujo general (Ingresos vs Gastos)
        self.contenedor_grafica_varianza.content = crear_tarjeta_grafica_varianza(
            datos_flujo=datos_flujo,
            periodo_texto=periodo_txt,
        )

        # Desglose de categorías
        if categorias and total_gastos > 0:
            filas = []
            for item in categorias:
                cat = item["categoria"]
                total = item["total"]
                pct = item["porcentaje"]
                cant = item["cantidad"]
                icono = ICONOS.get(cat, ft.Icons.MORE_HORIZ)

                fila_cat = ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                padding=6,
                                                border_radius=8,
                                                bgcolor=ft.Colors.TEAL_50,
                                                content=ft.Icon(icono, color=ft.Colors.TEAL_700, size=18),
                                            ),
                                            ft.Column(
                                                spacing=0,
                                                controls=[
                                                    ft.Text(cat, weight=ft.FontWeight.W_600, size=14),
                                                    ft.Text(
                                                        f"{cant} {'gasto' if cant == 1 else 'gastos'}",
                                                        size=11,
                                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        spacing=0,
                                        controls=[
                                            ft.Text(moneda(total), weight=ft.FontWeight.BOLD, size=14),
                                            ft.Text(
                                                f"{pct:.1f}%",
                                                size=11,
                                                color=ft.Colors.TEAL_700,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.ProgressBar(
                                value=pct / 100.0,
                                color=ft.Colors.TEAL_700,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            ),
                        ],
                    ),
                )
                filas.append(fila_cat)

            self.columna_categorias.controls = filas
        else:
            self.columna_categorias.controls = [
                ft.Container(
                    padding=32,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INSIGHTS_OUTLINED, size=40, color=ft.Colors.OUTLINE),
                            ft.Text(
                                f"Sin datos de gastos ({periodo_txt.lower()})",
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Registra movimientos de tipo 'Gasto' para visualizar el análisis.",
                                size=12,
                                color=ft.Colors.OUTLINE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            ]

        try:
            self.update()
        except RuntimeError:
            pass
