
import pandas as pd
import numpy as np


def sanitize_data(data):

    if isinstance(data, dict):
        return {
            k: sanitize_data(v)
            for k, v in data.items()
        }

    if isinstance(data, list):
        return [
            sanitize_data(x)
            for x in data
        ]

    if isinstance(data, pd.Timestamp):
        return str(data)

    if pd.isna(data):
        return None

    if data == np.inf or data == -np.inf:
        return None

    return data


def clean_df(df):

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return df


def execute_query(df, plan):

    operation = plan.get(
        "operation",
        ""
    )

    print("=" * 50)
    print("ACTION =", operation)
    print("=" * 50)

    df = clean_df(df)

    try:

        # FILTER
        if operation == "filter":

            column = plan.get("column")
            value = plan.get("value")

            result = df[
                df[column]
                .astype(str)
                .str.lower()
                ==
                str(value).lower()
            ]

            return sanitize_data(
                result.head(100)
                .to_dict(orient="records")
            )

        # COUNT
        elif operation == "count":

            column = plan.get("column")
            value = plan.get("value")

            count = len(
                df[
                    df[column]
                    .astype(str)
                    .str.lower()
                    ==
                    str(value).lower()
                ]
            )

            return {
                "count": int(count)
            }

        # LOWEST RATING
        elif operation == "lowest_rating_agent":

            ratings = (
                df.groupby("agent_id")[
                    "customer_rating"
                ].mean()
            )

            return {
                "agent_id":
                str(ratings.idxmin()),
                "average_rating":
                round(float(ratings.min()), 2)
            }

        # HIGHEST RATING
        elif operation == "highest_rating_agent":

            ratings = (
                df.groupby("agent_id")[
                    "customer_rating"
                ].mean()
            )

            return {
                "agent_id":
                str(ratings.idxmax()),
                "average_rating":
                round(float(ratings.max()), 2)
            }

        # MOST RESOLVED
        elif operation == "highest_resolution_agent":

            resolved = df[
                df["status"]
                .astype(str)
                .str.lower()
                ==
                "resolved"
            ]

            result = (
                resolved.groupby("agent_id")
                .size()
                .reset_index(
                    name="resolved_count"
                )
            )

            top = result.loc[
                result[
                    "resolved_count"
                ].idxmax()
            ]

            return {
                "agent_id":
                str(top["agent_id"]),
                "resolved_count":
                int(top["resolved_count"])
            }

        # AVERAGE RATING
        elif operation == "average_rating":

            category = plan.get(
                "category"
            )

            filtered = df[
                df["category"]
                .astype(str)
                .str.lower()
                ==
                category.lower()
            ]

            avg = filtered[
                "customer_rating"
            ].mean()

            if pd.isna(avg):
                avg = 0

            return {
                "category":
                category,
                "average_rating":
                round(float(avg), 2)
            }

        # AGENT SUMMARY
        elif operation == "agent_performance_summary":

            summary = (
                df.groupby("agent_id")
                .agg(
                    total_tickets=(
                        "ticket_id",
                        "count"
                    ),
                    average_rating=(
                        "customer_rating",
                        "mean"
                    )
                )
                .reset_index()
            )

            summary[
                "average_rating"
            ] = (
                summary[
                    "average_rating"
                ]
                .fillna(0)
                .round(2)
            )

            return sanitize_data(
                summary.to_dict(
                    orient="records"
                )
            )

        # CRITICAL UNRESOLVED
        elif operation == "critical_unresolved":

            result = df[
                (
                    df["priority"]
                    .astype(str)
                    .str.lower()
                    ==
                    "critical"
                )
                &
                (
                    df["status"]
                    .astype(str)
                    .str.lower()
                    !=
                    "resolved"
                )
            ]

            return sanitize_data(
                result.to_dict(
                    orient="records"
                )
            )

        # LONG RESOLUTION
        elif operation == "long_resolution_tickets":

            hours = plan.get(
                "hours",
                12
            )

            result = df[
                df[
                    "resolution_time_hrs"
                ] > hours
            ]

            return sanitize_data(
                result.to_dict(
                    orient="records"
                )
            )
        
        elif operation == "lowest_category_rating":

            result = (
                df.groupby("category")["customer_rating"]
                .mean()
            )

            return {
                "category": str(result.idxmin()),
                "average_rating": round(float(result.min()), 2)
            }


        elif operation == "highest_category_rating":

            result = (
                df.groupby("category")["customer_rating"]
                .mean()
            )

            return {
                "category": str(result.idxmax()),
                "average_rating": round(float(result.max()), 2)
            }


        elif operation == "top_customer_issues":

            result = (
                df["issue_summary"]
                .value_counts()
                .head(10)
                .reset_index()
            )

            result.columns = [
                "issue",
                "count"
            ]

            return sanitize_data(
                result.to_dict(
                    orient="records"
                )
            )


        elif operation == "open_ticket_percentage":

            total = len(df)

            open_count = len(
                df[
                    df["status"]
                    .astype(str)
                    .str.lower()
                    == "open"
                ]
            )

            return {
                "percentage":
                round(
                    (open_count / total) * 100,
                    2
                )
            }


        elif operation == "resolved_ticket_percentage":

            total = len(df)

            resolved_count = len(
                df[
                    df["status"]
                    .astype(str)
                    .str.lower()
                    == "resolved"
                ]
            )

            return {
                "percentage":
                round(
                    (resolved_count / total) * 100,
                    2
                )
            }


        elif operation == "most_ticket_category":

            result = (
                df["category"]
                .value_counts()
            )

            return {
                "category":
                str(result.idxmax()),

                "ticket_count":
                int(result.max())
            }



        # AVG RESOLUTION
        elif operation == "average_resolution_time":

            avg = df[
                "resolution_time_hrs"
            ].mean()

            if pd.isna(avg):
                avg = 0

            return {
                "average_resolution_time":
                round(float(avg), 2)
            }

        # ANOMALIES
        elif operation == "anomaly_detection":

            anomalies = []

            threshold = (
                df[
                    "resolution_time_hrs"
                ]
                .dropna()
                .quantile(0.95)
            )

            long_res = df[
                df[
                    "resolution_time_hrs"
                ] > threshold
            ]

            for _, row in long_res.iterrows():

                anomalies.append({
                    "ticket_id":
                    str(row["ticket_id"]),
                    "reason":
                    "Long Resolution Time"
                })

            critical = df[
                (
                    df["priority"]
                    .astype(str)
                    .str.lower()
                    ==
                    "critical"
                )
                &
                (
                    df["status"]
                    .astype(str)
                    .str.lower()
                    !=
                    "resolved"
                )
            ]

            for _, row in critical.iterrows():

                anomalies.append({
                    "ticket_id":
                    str(row["ticket_id"]),
                    "reason":
                    "Critical Unresolved"
                })

            return {
                "total_anomalies":
                len(anomalies),
                "anomalies":
                anomalies
            }

        else:

            return {
                "message":
                f"Operation '{operation}' not supported"
            }

    except Exception as e:

        return {
            "error": str(e)
        }

