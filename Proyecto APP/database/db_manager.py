import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from models.movimiento import Movimiento


class DBManager:
    """Gestor de base de datos SQLite para la aplicación de finanzas personales."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Por defecto guarda en el directorio data/ relativo a este archivo
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "gastos.db")
        else:
            self.db_path = db_path

        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión con soporte multihilo para eventos de Flet."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        """Crea la tabla si no existe y siembra registros iniciales de ejemplo si está vacía."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    descripcion TEXT,
                    monto REAL NOT NULL,
                    fecha TEXT NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM movimientos")
            total = cursor.fetchone()[0]

            if total == 0:
                # Datos iniciales para que la aplicación no aparezca completamente vacía al primer uso
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.executemany(
                    """
                    INSERT INTO movimientos (tipo, categoria, descripcion, monto, fecha)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        ("Ingreso", "Beca", "Beca mensual", 1500.0, ahora),
                        ("Gasto", "Comida", "Comida en la uni", 85.0, ahora),
                    ],
                )
            conn.commit()

    def agregar(self, mov: Movimiento) -> int:
        """Inserta un nuevo movimiento en la base de datos y retorna su nuevo ID."""
        fecha_str = mov.fecha.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO movimientos (tipo, categoria, descripcion, monto, fecha)
                VALUES (?, ?, ?, ?, ?)
                """,
                (mov.tipo, mov.categoria, mov.descripcion, mov.monto, fecha_str),
            )
            conn.commit()
            mov.id = cursor.lastrowid
            return mov.id

    def obtener_todos(
        self,
        busqueda: Optional[str] = None,
        tipo: Optional[str] = None,
        categoria: Optional[str] = None,
        limite: Optional[int] = None,
    ) -> List[Movimiento]:
        """Recupera los movimientos aplicando filtros opcionales ordenados por fecha descendente."""
        query = "SELECT id, tipo, categoria, descripcion, monto, fecha FROM movimientos WHERE 1=1"
        params: List[Any] = []

        if busqueda:
            query += " AND (descripcion LIKE ? OR categoria LIKE ?)"
            patron = f"%{busqueda.strip()}%"
            params.extend([patron, patron])

        if tipo and tipo != "Todos":
            query += " AND tipo = ?"
            params.append(tipo)

        if categoria and categoria != "Todas":
            query += " AND categoria = ?"
            params.append(categoria)

        query += " ORDER BY datetime(fecha) DESC, id DESC"

        if limite is not None and limite > 0:
            query += " LIMIT ?"
            params.append(limite)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            filas = cursor.fetchall()
            return [Movimiento.from_row(fila) for fila in filas]

    def obtener_por_id(self, mov_id: int) -> Optional[Movimiento]:
        """Obtiene un movimiento específico por su identificador primario."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, tipo, categoria, descripcion, monto, fecha FROM movimientos WHERE id = ?",
                (mov_id,),
            )
            fila = cursor.fetchone()
            return Movimiento.from_row(fila) if fila else None

    def actualizar(self, mov: Movimiento) -> bool:
        """Actualiza un movimiento existente en la base de datos."""
        if mov.id is None:
            return False
        fecha_str = mov.fecha.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE movimientos
                SET tipo = ?, categoria = ?, descripcion = ?, monto = ?, fecha = ?
                WHERE id = ?
                """,
                (mov.tipo, mov.categoria, mov.descripcion, mov.monto, fecha_str, mov.id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def eliminar(self, mov_id: int) -> bool:
        """Elimina un movimiento por su ID único."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movimientos WHERE id = ?", (mov_id,))
            conn.commit()
            return cursor.rowcount > 0

    def obtener_resumen(self) -> Dict[str, float]:
        """Calcula el total de ingresos, gastos y balance neto actual."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Ingreso'")
            ingresos = float(cursor.fetchone()[0])

            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Gasto'")
            gastos = float(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM movimientos")
            total_items = cursor.fetchone()[0]

            return {
                "ingresos": ingresos,
                "gastos": gastos,
                "balance": ingresos - gastos,
                "total_items": total_items,
            }

    def obtener_gastos_por_categoria(self) -> List[Dict[str, Any]]:
        """Calcula el gasto total y porcentaje por cada categoría registrada."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Gasto'")
            gran_total = float(cursor.fetchone()[0])

            if gran_total == 0:
                return []

            cursor.execute(
                """
                SELECT categoria, SUM(monto) as total, COUNT(*) as cantidad
                FROM movimientos
                WHERE tipo = 'Gasto'
                GROUP BY categoria
                ORDER BY total DESC
                """
            )
            filas = cursor.fetchall()
            resultado = []
            for cat, total, cant in filas:
                pct = (total / gran_total) * 100
                resultado.append({
                    "categoria": cat,
                    "total": float(total),
                    "porcentaje": pct,
                    "cantidad": cant,
                })
            return resultado
