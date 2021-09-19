import importlib.resources
from pathlib import Path


class BaseTest:
    package = "tests.resources"

    known = {
        ".docx": "cadc459a6b0afc424466502da05df9ecbc335cc85eeac0d23c86c8f222423b1b",
        ".pdf": "5a80a3132bc3d21d095317c93f48f4970e0d4448db0be374ee541b5e0efc4fe1",
        ".png": "885f9e3876f3a76c69b3689064970a90608eeddced0d38c7dd432437c1496381",
        ".txt": "8902c1f31b6f150ed9862dd57dacb5c2107fb08c578f6c573514fe5c299c17d5",
    }

    def example1_path(self, suffix: str):
        name = self.example1_name(suffix)
        with importlib.resources.path(self.package, name) as p:
            return p

    def example1_name(self, suffix: str):
        return str(Path("example1").with_suffix(suffix))

    def example1_hash(self, suffix: str):
        return self.known[suffix]

    def example1_hash_2(self, suffix: str):
        return self.example1_hash(suffix)[0:2]

    def example1_hash_15(self, suffix: str):
        return self.example1_hash(suffix)[0:15]

    def example1_hash_dir(self, suffix: str):
        return Path(self.example1_hash_2(suffix)) / self.example1_hash_15(suffix)
