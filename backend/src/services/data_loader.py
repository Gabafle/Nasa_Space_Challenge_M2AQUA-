from __future__ import annotations
import pandas as pd
import io
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class DataLoadError:
    field: Optional[str]
    code: str
    message: str


@dataclass
class DataLoadResult:
    ok: bool
    rows: List[Dict[str, Any]]
    errors: List[DataLoadError]
    columns: List[str]
    source_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "rows": self.rows,
            "errors": [asdict(error) for error in self.errors],
            "columns": self.columns,
            "source_name": self.source_name,
        }


class DataLoader:
    """Utility to load CSV/XLS/XLSX data with optional schema validation."""

    def __init__(
        self,
        expected_columns: Optional[Sequence[str]] = None,
        allow_extra_columns: bool = True,
    ) -> None:
        self.expected_columns = list(expected_columns) if expected_columns else None
        self.allow_extra_columns = allow_extra_columns

    def load_file(self, path: str) -> DataLoadResult:
        source_name = os.path.basename(path) if path else None
        try:
            if not path or not os.path.exists(path):
                return self._error_result("file_not_found", f"Fichier introuvable: {path}", source_name)

            ext = os.path.splitext(path)[1].lower()
            if ext == ".csv":
                dataframe = self._read_csv(path)
            elif ext in (".xls", ".xlsx"):
                dataframe = self._read_xlsx(path)
            else:
                return self._error_result("unsupported_type", f"Type non supporté: {ext}", source_name)

            return self._validate_and_pack(dataframe, source_name)
        except Exception as exc:  # pragma: no cover - runtime safety
            return self._error_result("load_failure", f"Erreur de chargement: {exc}", source_name)

    def load_bytes(self, content: bytes, filename: str) -> DataLoadResult:
        source_name = filename
        try:
            ext = os.path.splitext(filename)[1].lower()
            buffer = io.BytesIO(content)

            if ext == ".csv":
                dataframe = self._read_csv(buffer)
            elif ext in (".xls", ".xlsx"):
                dataframe = self._read_xlsx(buffer)
            else:
                return self._error_result("unsupported_type", f"Type non supporté: {ext}", source_name)

            return self._validate_and_pack(dataframe, source_name)
        except Exception as exc:  # pragma: no cover - runtime safety
            return self._error_result("load_failure", f"Erreur de chargement: {exc}", source_name)

    def _read_csv(self, source: Any):
        if pd is None:
            raise RuntimeError("pandas est requis pour lire un fichier CSV")

        try:
            return pd.read_csv(source)
        except Exception:
            return pd.read_csv(source, sep=";")

    def _read_xlsx(self, source: Any):
        if pd is None:
            raise RuntimeError("pandas est requis pour lire un fichier Excel")

        return pd.read_excel(source)

    def _validate_and_pack(self, dataframe: Any, source_name: Optional[str]) -> DataLoadResult:
        if pd is None:
            return self._error_result("internal", "pandas requis pour la validation", source_name)

        dataframe.columns = [str(column).strip() for column in list(dataframe.columns)]

        errors: List[DataLoadError] = []
        if self.expected_columns:
            missing = [col for col in self.expected_columns if col not in dataframe.columns]
            extra = [col for col in dataframe.columns if col not in self.expected_columns]

            if missing:
                errors.append(
                    DataLoadError(None, "missing_columns", f"Colonnes manquantes: {', '.join(missing)}")
                )

            if not self.allow_extra_columns and extra:
                errors.append(
                    DataLoadError(None, "extra_columns", f"Colonnes supplémentaires: {', '.join(extra)}")
                )

        dataframe = dataframe.dropna(how="all")
        rows: List[Dict[str, Any]] = dataframe.to_dict(orient="records")

        return DataLoadResult(
            ok=len(errors) == 0,
            rows=rows,
            errors=errors,
            columns=list(dataframe.columns),
            source_name=source_name,
        )

    def _error_result(self, code: str, message: str, source_name: Optional[str]) -> DataLoadResult:
        return DataLoadResult(
            ok=False,
            rows=[],
            errors=[DataLoadError(None, code, message)],
            columns=[],
            source_name=source_name,
        )

