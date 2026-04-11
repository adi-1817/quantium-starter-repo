import pandas as pd
import os

files = os.listdir("data")

dfs = []
for file in files: 
    if file.endswith(".csv") and "processed" not in file:
        df = pd.read_csv(f"data/{file}")
        dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df["price"] = df["price"].str.replace("$", "", regex=False).astype(float)
df = df[df["product"] == "pink morsel"].copy()
df["sales"] = df["price"]*df["quantity"]

df = df[["sales", "date", "region"]]

df.to_csv("data/processed_data.csv", index = False)

