"""Validate the exact partitions used by the production training pipeline."""

from prepare_features import build_combined_dataset, normalized_sender_groups, split_development_data


def main() -> None:
    dataset = build_combined_dataset()
    partitions = split_development_data(dataset)
    groups = normalized_sender_groups(dataset)
    group_sets = {name: set(groups.loc[frame.index]) for name, frame in partitions.items()}
    names = list(partitions)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            assert not (group_sets[left] & group_sets[right]), f"sender overlap: {left}/{right}"
            assert not (
                set(partitions[left]["body"]) & set(partitions[right]["body"])
            ), f"body overlap: {left}/{right}"
    print("No sender or exact-body leakage across production partitions.")


if __name__ == "__main__":
    main()
