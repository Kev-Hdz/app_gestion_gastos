import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from models.movimiento import Movimiento


class DBManager:
    """Gestor de base de datos SQLite para la aplicación de finanzas personales."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # En dispositivos móviles (Android/iOS), Flet expone FLET_APP_STORAGE_DATA
            storage_data = os.getenv("FLET_APP_STORAGE_DATA")
            if storage_data:
                data_dir = storage_data
            else:
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
        dias: Optional[int] = None,
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

        if dias is not None and dias > 0:
            fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d 00:00:00")
            query += " AND datetime(fecha) >= datetime(?)"
            params.append(fecha_limite)

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

    def obtener_resumen(self, dias: Optional[int] = None) -> Dict[str, Any]:
        """Calcula el total de ingresos, gastos y balance neto actual, con filtro de días opcional."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            filtro_fecha = ""
            params: List[Any] = []
            if dias is not None and dias > 0:
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d 00:00:00")
                filtro_fecha = " AND datetime(fecha) >= datetime(?)"
                params = [fecha_limite]

            cursor.execute(f"SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Ingreso'{filtro_fecha}", params)
            ingresos = float(cursor.fetchone()[0])

            cursor.execute(f"SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Gasto'{filtro_fecha}", params)
            gastos = float(cursor.fetchone()[0])

            cursor.execute(f"SELECT COUNT(*) FROM movimientos WHERE 1=1{filtro_fecha}", params)
            total_items = cursor.fetchone()[0]

            return {
                "ingresos": ingresos,
                "gastos": gastos,
                "balance": ingresos - gastos,
                "total_items": total_items,
                "dias": dias,
            }

    def obtener_gastos_por_categoria(self, dias: Optional[int] = None) -> List[Dict[str, Any]]:
        """Calcula el gasto total y porcentaje por cada categoría registrada en el período."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            filtro_fecha = ""
            params: List[Any] = []
            if dias is not None and dias > 0:
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d 00:00:00")
                filtro_fecha = " AND datetime(fecha) >= datetime(?)"
                params = [fecha_limite]

            cursor.execute(f"SELECT COALESCE(SUM(monto), 0) FROM movimientos WHERE tipo = 'Gasto'{filtro_fecha}", params)
            gran_total = float(cursor.fetchone()[0])

            if gran_total == 0:
                return []

            cursor.execute(
                f"""
                SELECT categoria, SUM(monto) as total, COUNT(*) as cantidad
                FROM movimientos
                WHERE tipo = 'Gasto'{filtro_fecha}
                GROUP BY categoria
                ORDER BY total DESC
                """,
                params,
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

    def obtener_datos_varianza_gastos_comida(self, dias: Optional[int] = None) -> Dict[str, Any]:
        """
        Recupera los totales diarios de Gastos y Comida para calcular
        la variación cronológica y la detección de picos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            filtro_fecha = ""
            params: List[Any] = []
            if dias is not None and dias > 0:
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d 00:00:00")
                filtro_fecha = " AND datetime(fecha) >= datetime(?)"
                params = [fecha_limite]

            cursor.execute(
                f"""
                SELECT 
                    date(fecha) as dia,
                    SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END) as total_gastos,
                    SUM(CASE WHEN tipo = 'Gasto' AND categoria = 'Comida' THEN monto ELSE 0 END) as total_comida
                FROM movimientos
                WHERE tipo = 'Gasto'{filtro_fecha}
                GROUP BY date(fecha)
                ORDER BY date(fecha) ASC
                """,
                params,
            )
            filas = cursor.fetchall()

        puntos = []
        pico_gastos = {"monto": 0.0, "fecha": "", "fecha_formato": ""}
        pico_comida = {"monto": 0.0, "fecha": "", "fecha_formato": ""}
        suma_gastos = 0.0
        suma_comida = 0.0

        for dia_str, gastos, comida in filas:
            gastos = float(gastos or 0)
            comida = float(comida or 0)
            suma_gastos += gastos
            suma_comida += comida
            varianza_dia = abs(gastos - comida)

            try:
                fecha_dt = datetime.strptime(dia_str, "%Y-%m-%d")
                fecha_formato = fecha_dt.strftime("%d/%m")
            except ValueError:
                fecha_formato = dia_str

            if gastos > pico_gastos["monto"]:
                pico_gastos = {"monto": gastos, "fecha": dia_str, "fecha_formato": fecha_formato}

            if comida > pico_comida["monto"]:
                pico_comida = {"monto": comida, "fecha": dia_str, "fecha_formato": fecha_formato}

            puntos.append({
                "dia": dia_str,
                "fecha_formato": fecha_formato,
                "total_gastos": gastos,
                "total_comida": comida,
                "varianza": varianza_dia,
            })

        total_dias = len(puntos)
        promedio_gastos = (suma_gastos / total_dias) if total_dias > 0 else 0.0
        promedio_comida = (suma_comida / total_dias) if total_dias > 0 else 0.0
        varianza_promedio = abs(promedio_gastos - promedio_comida)

        return {
            "puntos": puntos,
            "pico_gastos": pico_gastos,
            "pico_comida": pico_comida,
            "promedio_gastos": promedio_gastos,
            "promedio_comida": promedio_comida,
            "varianza_promedio": varianza_promedio,
            "total_dias": total_dias,
        }

    def obtener_datos_grafica_ingresos_gastos(self, dias: Optional[int] = None) -> Dict[str, Any]:
        """
        Recupera los totales diarios de Ingresos y Gastos para generar
        la gráfica comparativa de flujo financiero.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            filtro_fecha = ""
            params: List[Any] = []
            if dias is not None and dias > 0:
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d 00:00:00")
                filtro_fecha = " AND datetime(fecha) >= datetime(?)"
                params = [fecha_limite]

            cursor.execute(
                f"""
                SELECT 
                    date(fecha) as dia,
                    SUM(CASE WHEN tipo = 'Ingreso' THEN monto ELSE 0 END) as total_ingresos,
                    SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END) as total_gastos
                FROM movimientos
                WHERE 1=1{filtro_fecha}
                GROUP BY date(fecha)
                ORDER BY date(fecha) ASC
                """,
                params,
            )
            filas = cursor.fetchall()

        puntos = []
        suma_ingresos = 0.0
        suma_gastos = 0.0

        for dia_str, ingresos, gastos in filas:
            ingresos = float(ingresos or 0)
            gastos = float(gastos or 0)
            suma_ingresos += ingresos
            suma_gastos += gastos

            try:
                fecha_dt = datetime.strptime(dia_str, "%Y-%m-%d")
                fecha_formato = fecha_dt.strftime("%d/%m")
            except ValueError:
                fecha_formato = dia_str

            puntos.append({
                "dia": dia_str,
                "fecha_formato": fecha_formato,
                "total_ingresos": ingresos,
                "total_gastos": gastos,
                "balance_dia": ingresos - gastos,
            })

        total_dias = len(puntos)
        promedio_ingresos = (suma_ingresos / total_dias) if total_dias > 0 else 0.0
        promedio_gastos = (suma_gastos / total_dias) if total_dias > 0 else 0.0

        return {
            "puntos": puntos,
            "total_ingresos": suma_ingresos,
            "total_gastos": suma_gastos,
            "balance_neto": suma_ingresos - suma_gastos,
            "promedio_ingresos": promedio_ingresos,
            "promedio_gastos": promedio_gastos,
            "total_dias": total_dias,
        }
