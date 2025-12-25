import os
import json

data = {"test": "manual_data"}
print("Current working directory:", os.getcwd())
print("Evidence directory exists:", os.path.exists("evidence"))
print("Evidence v13_6 directory exists:", os.path.exists("evidence/v13_6"))
try:
    os.makedirs("evidence/v13_6", exist_ok=True)
    with open("evidence/v13_6/economic_bounds_verification.json", "w") as f:
        json.dump(data, f)
    print("File written successfully")
    print(
        "File exists after write:",
        os.path.exists("evidence/v13_6/economic_bounds_verification.json"),
    )
except Exception as e:
    print("Error writing file:", e)
    import traceback

    traceback.print_exc()
