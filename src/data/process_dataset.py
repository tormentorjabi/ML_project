import pandas as pd


def process(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    num_cols = df.select_dtypes(include='number').columns
    min_vals = df[num_cols].min()
    max_vals = df[num_cols].max()
    df[num_cols] = (df[num_cols] - min_vals) / (max_vals - min_vals)

    df.to_csv(output_path, index=False)
