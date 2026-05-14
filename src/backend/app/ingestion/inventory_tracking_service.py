from pathlib import Path
import pandas as pd


class InventoryTrackingService:
    def __init__(self, previous_inventory_path: str | Path):
        self.previous_inventory_path = Path(previous_inventory_path)

    def compare(self, current_inventory_df: pd.DataFrame) -> dict:
        if not self.previous_inventory_path.exists():
            return {
                "new_files": current_inventory_df,
                "modified_files": pd.DataFrame(),
                "deleted_files": pd.DataFrame(),
                "unchanged_files": pd.DataFrame(),
            }

        previous_df = pd.read_csv(self.previous_inventory_path)

        key_cols = ["relative_path"]
        compare_cols = ["file_size_bytes", "modified_time"]

        previous_indexed = previous_df.set_index(key_cols)
        current_indexed = current_inventory_df.set_index(key_cols)

        new_paths = current_indexed.index.difference(previous_indexed.index)
        deleted_paths = previous_indexed.index.difference(current_indexed.index)
        common_paths = current_indexed.index.intersection(previous_indexed.index)

        modified_mask = (
            current_indexed.loc[common_paths, compare_cols] !=
            previous_indexed.loc[common_paths, compare_cols]
        ).any(axis=1)

        modified_paths = common_paths[modified_mask]
        unchanged_paths = common_paths[~modified_mask]

        return {
            "new_files": current_indexed.loc[new_paths].reset_index(),
            "modified_files": current_indexed.loc[modified_paths].reset_index(),
            "deleted_files": previous_indexed.loc[deleted_paths].reset_index(),
            "unchanged_files": current_indexed.loc[unchanged_paths].reset_index(),
        }