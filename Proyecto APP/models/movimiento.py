from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import flet as ft

CATEGORIAS_GASTO = [
    "Comida", "Transporte", "Escuela", "Entretenimiento",
    "Salud", "Ropa", "Servicios", "Otros",
]

CATEGORIAS_INGRESO = [
    "Sueldo", "Beca", "Ventas", "Regalo", "Otros",
]

ICONOS = {
    "Comida": ft.Icons.RESTAURANT,
    "Transporte": ft.Icons.DIRECTIONS_BUS,
    "Escuela": ft.Icons.SCHOOL,
    "Entretenimiento": ft.Icons.MOVIE,
    "Salud": ft.Icons.LOCAL_HOSPITAL,
    "Ropa": ft.Icons.CHECKROOM,
    "Servicios": ft.Icons.RECEIPT_LONG,
    "Sueldo": ft.Icons.PAYMENTS,
    "Beca": ft.Icons.SCHOOL,
    "Ventas": ft.Icons.STOREFRONT,
    "Regalo": ft.Icons.CARD_GIFTCARD,
    "Otros": ft.Icons.MORE_HORIZ,
}


def moneda(valor: float) -> str:
    """Formatea un número decimal como moneda con dos decimales."""
    return f"${valor:,.2f}"


@dataclass
class Movimiento:
    tipo: str  # "Gasto" o "Ingreso"
    categoria: str
    descripcion: str
    monto: float
    fecha: datetime
    id: Optional[int] = None

    @classmethod
    def from_row(cls, row: tuple) -> "Movimiento":
        """Convierte una tupla de base de datos (id, tipo, categoria, descripcion, monto, fecha) en un Movimiento."""
        fecha_obj = datetime.fromisoformat(row[5]) if isinstance(row[5], str) else row[5]
        return cls(
            id=row[0],
            tipo=row[1],
            categoria=row[2],
            descripcion=row[3] or "",
            monto=float(row[4]),
            fecha=fecha_obj,
        )
