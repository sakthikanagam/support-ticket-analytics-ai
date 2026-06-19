import pandas as pd


def detect_anomalies(df):

    anomalies = []

    # -----------------------------
    # Long Resolution Time
    # -----------------------------

    if "resolution_time_hrs" in df.columns:

        threshold = (
            df["resolution_time_hrs"]
            .dropna()
            .quantile(0.95)
        )

        long_resolution = df[
            df["resolution_time_hrs"]
            > threshold
        ]

        for _, row in long_resolution.iterrows():

            anomalies.append({

                "ticket_id":
                row["ticket_id"],

                "anomaly_type":
                "Long Resolution Time",

                "details":
                f"{row['resolution_time_hrs']} hrs"

            })

    # -----------------------------
    # Critical Unresolved
    # -----------------------------

    critical_unresolved = df[
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

    for _, row in critical_unresolved.iterrows():

        anomalies.append({

            "ticket_id":
            row["ticket_id"],

            "anomaly_type":
            "Critical Unresolved",

            "details":
            row["status"]

        })

    # -----------------------------
    # High Priority Older Than 24h
    # -----------------------------

    current_time = pd.Timestamp.now()

    high_priority = df[
        (
            df["priority"]
            .astype(str)
            .str.lower()
            ==
            "high"
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

    for _, row in high_priority.iterrows():

        try:

            age_hours = (
                current_time
                -
                row["created_at"]
            ).total_seconds() / 3600

            if age_hours > 24:

                anomalies.append({

                    "ticket_id":
                    row["ticket_id"],

                    "anomaly_type":
                    "High Priority Aging",

                    "details":
                    f"{round(age_hours,2)} hrs old"

                })

        except:
            pass

    # -----------------------------
    # Slow Response Time
    # -----------------------------

    if "response_time_hrs" in df.columns:

        slow_response = df[
            df["response_time_hrs"] > 8
        ]

        for _, row in slow_response.iterrows():

            anomalies.append({

                "ticket_id":
                row["ticket_id"],

                "anomaly_type":
                "Slow Response",

                "details":
                f"{row['response_time_hrs']} hrs"

            })

    return {

        "total_anomalies":
        len(anomalies),

        "anomalies":
        anomalies
    }