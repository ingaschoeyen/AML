from pathlib import Path
import pandas as pd


class CSVRepository:
    def save_dataframe(self, df: pd.DataFrame, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    def load_dataframe(self, path: str | Path) -> pd.DataFrame:
        path = Path(path)

        if not path.exists():
            return pd.DataFrame()

        return pd.read_csv(path)

    def save_inventory(self, df: pd.DataFrame, path: str | Path) -> None:
        self.save_dataframe(df, path)

    def load_inventory(self, path: str | Path) -> pd.DataFrame:
        return self.load_dataframe(path)

    def save_extraction(self, df: pd.DataFrame, path: str | Path) -> None:
        self.save_dataframe(df, path)

    def load_extraction(self, path: str | Path) -> pd.DataFrame:
        return self.load_dataframe(path)