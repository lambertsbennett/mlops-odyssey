import pandas as pd
import json

def main():
    with open('/results.json', 'r') as f:
        response_data = json.load(f)

    df = pd.json_normalize(response_data)
    df = df.dropna()
    daily_median = df.groupby(by=["date.utc", "parameter"]).median()

    daily_median.to_parquet(f"/data.parquet")

if __name__ == '__main__':
    main()
