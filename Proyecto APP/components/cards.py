import flet as ft
from models.movimiento import moneda


def crear_tarjeta_balance(balance: float) -> ft.Container:
    """Genera la tarjeta principal de balance financiero."""
    color_balance = ft.Colors.WHITE if balance >= 0 else ft.Colors.RED_100
    signo = "" if balance >= 0 else "-"
    balance_abs = abs(balance)

    return ft.Container(
        padding=22,
        border_radius=18,
        bgcolor=ft.Colors.TEAL_700,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Balance actual", color=ft.Colors.WHITE_70, size=14, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.WHITE_70, size=20),
                    ],
                ),
                ft.Text(
                    f"{signo}{moneda(balance_abs)}",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color=color_balance,
                ),
            ],
        ),
    )


def _mini_tarjeta(
    titulo: str,
    valor_texto: str,
    icono: str,
    color_icono: str,
    bgcolor_icono: str,
    color_texto: str,
) -> ft.Container:
    """Componente auxiliar para las tarjetas de resumen de flujo."""
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Container(
                    padding=8,
                    border_radius=10,
                    bgcolor=bgcolor_icono,
                    content=ft.Icon(icono, color=color_icono, size=20),
                ),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(titulo, size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                        ft.Text(valor_texto, size=15, weight=ft.FontWeight.BOLD, color=color_texto),
                    ],
                ),
            ],
        ),
    )


def crear_tarjetas_resumen(ingresos: float, gastos: float) -> ft.Row:
    """Genera la fila con las mini tarjetas comparativas de ingresos y gastos."""
    return ft.Row(
        spacing=12,
        controls=[
            _mini_tarjeta(
                titulo="Ingresos",
                valor_texto=moneda(ingresos),
                icono=ft.Icons.ARROW_UPWARD,
                color_icono=ft.Colors.GREEN_700,
                bgcolor_icono=ft.Colors.GREEN_50,
                color_texto=ft.Colors.GREEN_700,
            ),
            _mini_tarjeta(
                titulo="Gastos",
                valor_texto=moneda(gastos),
                icono=ft.Icons.ARROW_DOWNWARD,
                color_icono=ft.Colors.RED_700,
                bgcolor_icono=ft.Colors.RED_50,
                color_texto=ft.Colors.RED_700,
            ),
        ],
    )
