import pandas as pd


def load_data():

    try:

        df = pd.read_csv(
            "data/support_tickets.csv"
        )

        # Remove extra spaces
        df.columns = [
            col.strip()
            for col in df.columns
        ]

        # Rename columns from dataset
        rename_map = {
            "resp_time_hrs":
                "response_time_hrs",

            "resol_time_hrs":
                "resolution_time_hrs",

            "cust_rating":
                "customer_rating"
        }

        df.rename(
            columns=rename_map,
            inplace=True
        )

        # Datetime conversion
        if "created_at" in df.columns:

            df["created_at"] = pd.to_datetime(
                df["created_at"],
                errors="coerce"
            )

        # Numeric conversions
        numeric_cols = [
            "response_time_hrs",
            "resolution_time_hrs",
            "customer_rating"
        ]

        for col in numeric_cols:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        # Fill text columns
        text_cols = [
            "category",
            "priority",
            "status",
            "agent_id",
            "issue_summary"
        ]

        for col in text_cols:

            if col in df.columns:

                df[col] = (
                    df[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        print("=" * 50)
        print(
            f"Dataset Loaded Successfully"
        )
        print(
            f"Rows: {len(df)}"
        )
        print(
            f"Columns: {len(df.columns)}"
        )
        print("=" * 50)

        return df

    except Exception as e:

        print(
            "Data Loading Error:",
            str(e)
        )

        raise Exception(
            f"Failed to load dataset: {str(e)}"
        )