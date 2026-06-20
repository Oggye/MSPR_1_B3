import pandas as pd

from config import *
from business_rules import build_target
from feature_engineering import add_features


def main():

    facts = pd.read_csv(FACTS_FILE)

    countries = pd.read_csv(COUNTRIES_FILE)

    operators = pd.read_csv(OPERATORS_FILE)

    df = (
        facts
        .merge(
            countries,
            on="country_id",
            how="left"
        )
        .merge(
            operators,
            on="operator_id",
            how="left"
        )
    )

    df = add_features(df)

    df["candidate_substitution"] = (
        df.apply(build_target, axis=1)
    )

    df.to_csv(
        OUTPUT_DATASET,
        index=False
    )

    print()
    print("Dataset IA créé")
    print(df.shape)
    print()

    print(
        df["candidate_substitution"]
        .value_counts()
    )


if __name__ == "__main__":
    main()