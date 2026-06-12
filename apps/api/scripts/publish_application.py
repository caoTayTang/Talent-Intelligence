import argparse

from app.queue import enqueue


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a CV screening task.")
    parser.add_argument(
        "--application_id",
        default="4db5a319-8d0d-4f32-bd08-bb0618bdddd4",
        help="Application UUID to screen",
    )
    args = parser.parse_args()

    task_id = enqueue(
        "agent.cv_screening",
        {"application_id": args.application_id},
    )

    print(f"Published agent.cv_screening task_id={task_id}")


if __name__ == "__main__":
    main()
