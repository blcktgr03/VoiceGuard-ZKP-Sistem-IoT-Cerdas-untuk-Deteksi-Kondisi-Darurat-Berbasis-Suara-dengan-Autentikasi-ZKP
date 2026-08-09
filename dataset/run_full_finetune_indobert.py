from pathlib import Path

import nbformat
from nbclient import NotebookClient


# Folder proyek dihitung dari lokasi skrip agar runner dapat dipakai di komputer lain.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Notebook dan log selalu berada di folder dataset yang sama dengan skrip ini.
NOTEBOOK_PATH = PROJECT_ROOT / "dataset" / "train_bert_final_dataset.ipynb"
RUNNER_LOG_PATH = PROJECT_ROOT / "dataset" / "full_finetune_indobert_runner.log"


def write_runner_log(message: str) -> None:
    """Append one progress message so training can be monitored continuously."""
    with RUNNER_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")
        log_file.flush()


def main() -> None:
    """Execute the full fine-tuning notebook with the tf-new kernel."""
    RUNNER_LOG_PATH.write_text("", encoding="utf-8")
    write_runner_log(f"Executing notebook: {NOTEBOOK_PATH}")
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=None,
        kernel_name="tf-new",
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
    )
    client.execute()
    nbformat.write(notebook, NOTEBOOK_PATH)
    write_runner_log("Notebook execution completed.")


if __name__ == "__main__":
    main()
