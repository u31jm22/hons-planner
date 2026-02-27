import os
import urllib.request

url = "https://raw.githubusercontent.com/potassco/pddl-instances/master/ipc-2000/domains/elevator-strips-simple-typed/domain.pddl"

target_dir = os.path.join("domains", "miconic")
os.makedirs(target_dir, exist_ok=True)
target_path = os.path.join(target_dir, "domain.pddl")

print(f"Downloading {url} -> {target_path}")
urllib.request.urlretrieve(url, target_path)
print("Done.")

