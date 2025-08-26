#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts.generate_architecture_report import list_repo_files, write_ai_study_pack, ROOT

def main() -> None:
    files = list_repo_files(ROOT)
    write_ai_study_pack(files)
    print("AI study pack generated in docs/ia estudar.")

if __name__ == "__main__":
    main()
