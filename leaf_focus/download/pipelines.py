# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import subprocess
from pathlib import Path

from itemadapter import ItemAdapter


class LeafFocusRunProgramPipelineItem:
    def _run_program(self, commands: list[str]):
        result = subprocess.run(commands, capture_output=True, check=True)
        return result

    def _find_executable(self, env_var: str):
        env_var_str = os.getenv(env_var)
        if not env_var_str:
            raise ValueError(f"Could not find '{env_var}': '{env_var_str}'.")

        env_var_path = Path(env_var_str).resolve()
        if not env_var_path.exists():
            raise ValueError(f"Could not find '{env_var}': '{env_var_path}'.")

        return env_var_path


class LeafFocusPdfTextPipelineItem(LeafFocusRunProgramPipelineItem):
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        cache_file = Path(adapter.get("path")).resolve()
        if cache_file:
            pdf_to_text_path = self._find_executable("PDF_TO_TEXT_PATH")
            text_file = cache_file.parent / "response_body_text"
            if not text_file.exists():
                commands = [
                    str(pdf_to_text_path),
                    "-layout",
                    "-enc",
                    "UTF-8",
                    "-eol",
                    "dos",
                    str(cache_file),
                    str(text_file),
                ]
                result = self._run_program(commands)
                if result.returncode != 0:
                    raise ValueError(f"Command failed: {repr(result)}")
        return item


class LeafFocusPdfImagePipelineItem(LeafFocusRunProgramPipelineItem):
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        cache_file = Path(adapter.get("path")).resolve()
        if cache_file:
            pdf_to_image_path = self._find_executable("PDF_TO_IMAGE_PATH")
            image_prefix = cache_file.parent / "response_body_image"
            image_files = list(cache_file.parent.glob("response_body_image*"))
            if len(image_files) < 1:
                commands = [
                    str(pdf_to_image_path),
                    "-gray",
                    str(cache_file),
                    str(image_prefix),
                ]
                result = self._run_program(commands)
                if result.returncode != 0:
                    raise ValueError(f"Command failed: {repr(result)}")
        return item
