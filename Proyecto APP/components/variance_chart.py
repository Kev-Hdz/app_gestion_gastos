from typing import Dict, Any, List
import flet as ft
import flet.canvas as cv
from models.movimiento import moneda


def _crear_canvas_grafica(
    puntos: List[Dict[str, Any]],
    width: int = 410,
    height: int = 280,
) -> cv.Canvas:
    """Genera el lienzo gráfico amplio con escala monetaria y barras comparativas de Ingresos vs Gastos."""
    margin_left = 52
    margin_right = 20
    margin_top = 40
    margin_bottom = 38
    plot_w = max(10, width - margin_left - margin_right)
    plot_h = max(10, height - margin_top - margin_bottom)

    max_val = max(1.0, max([p["total_ingresos"] for p in puntos] + [p["total_gastos"] for p in puntos]))
    max_y = max_val * 1.25

    def to_y(val: float) -> float:
        return margin_top + plot_h - (val / max_y * plot_h)

    shapes: List[cv.Shape] = []

    # 1. Líneas de rejilla y escala monetaria en eje Y
    grid_paint = ft.Paint(color=ft.Colors.OUTLINE_VARIANT, stroke_width=0.8)
    for ratio in [0.0, 0.33, 0.66, 1.0]:
        val = max_y * ratio
        y = to_y(val)
        shapes.append(cv.Line(margin_left, y, margin_left + plot_w, y, paint=grid_paint))
        texto_val = f"${int(val):,}" if val >= 10 else f"${val:.1f}"
        shapes.append(
            cv.Text(
                margin_left - 6,
                y,
                texto_val,
                style=ft.TextStyle(size=10, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                text_align=ft.TextAlign.RIGHT,
                alignment=ft.Alignment(1, 0),
            )
        )

    n = len(puntos)
    y_base = to_y(0)

    # 2. Barras dobles por fecha (Ingresos vs Gastos)
    slot_w = plot_w / n
    bar_w = min(36, max(14, slot_w * 0.36))

    for i, p in enumerate(puntos):
        center_x = margin_left + (i + 0.5) * slot_w
        x_ingreso = center_x - bar_w - 2
        x_gasto = center_x + 2

        y_ingreso = to_y(p["total_ingresos"])
        y_gasto = to_y(p["total_gastos"])

        h_ingreso = max(2.0, y_base - y_ingreso)
        h_gasto = max(2.0, y_base - y_gasto)

        # Barra Ingresos (Verde)
        shapes.append(
            cv.Rect(
                x_ingreso,
                y_ingreso,
                bar_w,
                h_ingreso,
                border_radius=5,
                paint=ft.Paint(color=ft.Colors.GREEN_600, style=ft.PaintingStyle.FILL),
            )
        )

        # Barra Gastos (Roja)
        shapes.append(
            cv.Rect(
                x_gasto,
                y_gasto,
                bar_w,
                h_gasto,
                border_radius=5,
                paint=ft.Paint(color=ft.Colors.RED_500, style=ft.PaintingStyle.FILL),
            )
        )

        # Monto directo arriba de cada barra
        if p["total_ingresos"] > 0:
            shapes.append(
                cv.Text(
                    x_ingreso + (bar_w / 2),
                    y_ingreso - 10,
                    f"+${int(p['total_ingresos']):,}",
                    style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
                    alignment=ft.Alignment(0, 0),
                )
            )

        if p["total_gastos"] > 0:
            shapes.append(
                cv.Text(
                    x_gasto + (bar_w / 2),
                    y_gasto - 10,
                    f"-${int(p['total_gastos']):,}",
                    style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                    alignment=ft.Alignment(0, 0),
                )
            )

        # Etiqueta de fecha en eje X
        shapes.append(
            cv.Text(
                center_x,
                y_base + 14,
                p["fecha_formato"],
                style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                alignment=ft.Alignment(0, 0),
            )
        )

    return cv.Canvas(shapes=shapes, width=width, height=height)


class CardGraficaFlujo(ft.Container):
    """Componente visual interactivo y ampliado para visualizar el flujo de Ingresos vs Gastos en barras."""

    def __init__(self, datos_flujo: Dict[str, Any], periodo_texto: str = "Histórico"):
        super().__init__(
            padding=18,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )
        self.datos_flujo = datos_flujo
        self.periodo_texto = periodo_texto

        self.contenedor_canvas = ft.Container(alignment=ft.Alignment(0, 0))
        self.contenedor_insight = ft.Container()
        self.contenedor_metricas = ft.Container()

        self._construir_contenido()

    def actualizar(self, datos_flujo: Dict[str, Any], periodo_texto: str = "Histórico"):
        """Refresca los datos del gráfico y la interpretación."""
        self.datos_flujo = datos_flujo
        self.periodo_texto = periodo_texto
        self._construir_contenido()
        try:
            self.update()
        except RuntimeError:
            pass

    def _construir_contenido(self):
        puntos = self.datos_flujo.get("puntos", [])
        total_ingresos = self.datos_flujo.get("total_ingresos", 0.0)
        total_gastos = self.datos_flujo.get("total_gastos", 0.0)
        balance_neto = self.datos_flujo.get("balance_neto", 0.0)

        # 1. Leyenda visual clara
        leyenda = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=16,
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=12, height=12, border_radius=3, bgcolor=ft.Colors.GREEN_600),
                        ft.Text("Ingresos", size=12, weight=ft.FontWeight.BOLD),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=12, height=12, border_radius=3, bgcolor=ft.Colors.RED_500),
                        ft.Text("Gastos", size=12, weight=ft.FontWeight.BOLD),
                    ],
                ),
            ],
        )

        if not puntos:
            # Estado sin datos
            self.contenedor_canvas.content = ft.Container(
                padding=36,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.AUTO_GRAPH_OUTLINED, size=44, color=ft.Colors.OUTLINE),
                        ft.Text(
                            "Sin movimientos registrados en este período",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(
                            f"No hay ingresos ni gastos para graficar en {self.periodo_texto.lower()}.",
                            size=12,
                            color=ft.Colors.OUTLINE,
                        ),
                    ],
                ),
            )
            self.contenedor_insight.content = ft.Container()
            self.contenedor_metricas.content = ft.Container()
        else:
            # Gráfica Canvas amplia (410x280 px) exclusivamente en barras
            self.contenedor_canvas.content = _crear_canvas_grafica(
                puntos=puntos,
                width=410,
                height=280,
            )

            # Interpretación en lenguaje cotidiano
            if balance_neto >= 0:
                color_balance = ft.Colors.GREEN_700
                icono_balance = ft.Icons.SAVINGS_OUTLINED
                texto_balance = f"Tus ingresos superaron a tus gastos por {moneda(balance_neto)} en este período."
            else:
                color_balance = ft.Colors.RED_700
                icono_balance = ft.Icons.WARNING_AMBER_ROUNDED
                texto_balance = f"Tus gastos superaron a tus ingresos por {moneda(abs(balance_neto))} en este período."

            self.contenedor_insight.content = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(icono_balance, color=color_balance, size=18),
                                ft.Text(
                                    "Resumen de Flujo",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=color_balance,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"• Total Ingresos: {moneda(total_ingresos)} entraron en {self.periodo_texto.lower()}.",
                            size=12,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Text(
                            f"• Total Gastos: {moneda(total_gastos)} salieron en {self.periodo_texto.lower()}.",
                            size=12,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Text(
                            f"• {texto_balance}",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=color_balance,
                        ),
                    ],
                ),
            )

            # Fichas de métricas inferiores
            signo_balance = "+" if balance_neto >= 0 else "-"
            self.contenedor_metricas.content = ft.Row(
                spacing=8,
                controls=[
                    self._crear_chip(
                        titulo="Ingresos",
                        valor=f"+{moneda(total_ingresos)}",
                        subtitulo=f"{len([p for p in puntos if p['total_ingresos'] > 0])} días con cobros",
                        color_acento=ft.Colors.GREEN_700,
                        bgcolor_icono=ft.Colors.GREEN_50,
                        icono=ft.Icons.ARROW_UPWARD,
                    ),
                    self._crear_chip(
                        titulo="Gastos",
                        valor=f"-{moneda(total_gastos)}",
                        subtitulo=f"{len([p for p in puntos if p['total_gastos'] > 0])} días con pagos",
                        color_acento=ft.Colors.RED_700,
                        bgcolor_icono=ft.Colors.RED_50,
                        icono=ft.Icons.ARROW_DOWNWARD,
                    ),
                    self._crear_chip(
                        titulo="Balance Neto",
                        valor=f"{signo_balance}{moneda(abs(balance_neto))}",
                        subtitulo=self.periodo_texto,
                        color_acento=color_balance,
                        bgcolor_icono=ft.Colors.TEAL_50 if balance_neto >= 0 else ft.Colors.RED_50,
                        icono=ft.Icons.ACCOUNT_BALANCE_WALLET,
                    ),
                ],
            )

        self.content = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.AUTO_GRAPH, color=ft.Colors.TEAL_700, size=22),
                                ft.Text("Flujo Financiero (Ingresos vs Gastos)", weight=ft.FontWeight.BOLD, size=16),
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=8,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            content=ft.Text(self.periodo_texto, size=11, weight=ft.FontWeight.W_500),
                        ),
                    ],
                ),
                leyenda,
                self.contenedor_canvas,
                self.contenedor_insight,
                self.contenedor_metricas,
            ],
        )

    def _crear_chip(
        self,
        titulo: str,
        valor: str,
        subtitulo: str,
        color_acento: str,
        bgcolor_icono: str,
        icono: str,
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        padding=6,
                        border_radius=8,
                        bgcolor=bgcolor_icono,
                        content=ft.Icon(icono, color=color_acento, size=16),
                    ),
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text(titulo, size=11, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                            ft.Text(valor, size=13, weight=ft.FontWeight.BOLD, color=color_acento),
                            ft.Text(subtitulo, size=10, color=ft.Colors.OUTLINE),
                        ],
                    ),
                ],
            ),
        )


def crear_tarjeta_grafica_varianza(datos_flujo: Dict[str, Any], periodo_texto: str = "Histórico") -> CardGraficaFlujo:
    """Función de conveniencia para instanciar la tarjeta de gráfica analítica."""
    return CardGraficaFlujo(datos_flujo=datos_flujo, periodo_texto=periodo_texto)
