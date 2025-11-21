import argparse
from .data.download_from_s3 import download_file
from .data.process_dataset import process
from .data.upload_to_s3 import upload_file

RAW_LOCAL = "data/raw/taxi_trip_pricing.csv"
PROCESSED_LOCAL = "data/processed/taxi_trip_pricing_processed.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", default="raw")
    parser.add_argument("--input-key", default="taxi_trip_pricing.csv")
    parser.add_argument(
        "--output-key",
        default="taxi_trip_pricing_processed.csv"
    )
    args = parser.parse_args()

    download_file(args.bucket, args.input_key, RAW_LOCAL)
    process(RAW_LOCAL, PROCESSED_LOCAL)
    upload_file(args.bucket, args.output_key, PROCESSED_LOCAL)


if __name__ == "__main__":
    main()
