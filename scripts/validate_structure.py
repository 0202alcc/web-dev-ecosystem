#!/usr/bin/env uv run python
import os
import sys


def check_feature_structure(base_path):
    errors = []
    # Walk through features directory
    # Expect structure: features/{feature}/{variant}

    if not os.path.exists(base_path):
        return ["Features directory not found"]

    for feature in os.listdir(base_path):
        feature_path = os.path.join(base_path, feature)
        if not os.path.isdir(feature_path):
            continue

        for variant in os.listdir(feature_path):
            variant_path = os.path.join(feature_path, variant)
            if not os.path.isdir(variant_path):
                continue

            # Now we are in a subproject (e.g., features/webpush/flask)
            relative_path = f"{feature}/{variant}"

            # Check 1: README.md exists and has TO DO
            readme_path = os.path.join(variant_path, "README.md")
            if not os.path.exists(readme_path):
                errors.append(f"MISSING: {relative_path}/README.md")
            else:
                with open(readme_path, "r") as f:
                    content = f.read()
                    if "TO DO:" not in content and "TODO:" not in content:
                        errors.append(
                            f"INVALID: {relative_path}/README.md missing 'TO DO:' section"
                        )

            # Check 2: AGENTS.md exists
            agents_path = os.path.join(variant_path, "AGENTS.md")
            if not os.path.exists(agents_path):
                errors.append(f"MISSING: {relative_path}/AGENTS.md")

            # Check 3: docs/ folder exists
            docs_path = os.path.join(variant_path, "docs")
            if not os.path.isdir(docs_path):
                errors.append(f"MISSING: {relative_path}/docs/ directory")

    return errors


if __name__ == "__main__":
    print("Validating subproject structure...")
    structure_errors = check_feature_structure("features")

    if structure_errors:
        print("\n❌ Structure Validation Failed:")
        for error in structure_errors:
            print(f" - {error}")
        sys.exit(1)
    else:
        print("\n✅ All subprojects compliant.")
        sys.exit(0)
