from pathlib import Path

from prefect import Flow, flatten, unmapped

from leaf_focus.download.crawl.prefect_task import PrefectTask as DownloadCrawlTask
from leaf_focus.ocr.prepare.prefect_task import PrefectTask as OcrPrepareTask
from leaf_focus.ocr.recognise.prefect_task import PrefectTask as OcrRecogniseTask
from leaf_focus.pdf.identify.prefect_task import PrefectTask as PdfIdentifyTask
from leaf_focus.pdf.images.prefect_task import PrefectTask as PdfImagesTask
from leaf_focus.pdf.info.prefect_task import PrefectTask as PdfInfoTask
from leaf_focus.pdf.text.prefect_task import PrefectTask as PdfTextTask


class Construct:
    def build(
        self,
        feed_dir: Path,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        threshold: int,
    ):
        """Build the Prefect flow."""
        with Flow("leaf-focus") as flow:

            download_task = DownloadCrawlTask()
            download_items = download_task(feed_dir)

            pdf_identify_task = PdfIdentifyTask(base_dir)
            pdf_identify_items = pdf_identify_task.map(download_items)

            pdf_info_task = PdfInfoTask(base_dir, pdf_info_exe)
            pdf_info_task.map(pdf_identify_items)

            pdf_text_task = PdfTextTask(base_dir, pdf_text_exe)
            pdf_text_task.map(pdf_identify_items)

            pdf_images_task = PdfImagesTask(base_dir, pdf_image_exe)
            pdf_image_items = pdf_images_task.map(pdf_identify_items)

            ocr_prepare_task = OcrPrepareTask(base_dir)
            ocr_prepare_items = ocr_prepare_task.map(
                input_item=flatten(pdf_image_items), threshold=unmapped(threshold)
            )

            ocr_recognise_task = OcrRecogniseTask(base_dir)
            ocr_recognise_task.map(
                input_item=flatten(ocr_prepare_items), threshold=unmapped(threshold)
            )
        return flow

    def visualise(
        self,
        feed_dir: Path,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        threshold: int,
        visualise_path: Path,
    ):
        """Visualise the Prefect flow."""
        flow = self.build(
            feed_dir, base_dir, pdf_info_exe, pdf_text_exe, pdf_image_exe, threshold
        )
        flow.visualize(
            filename=str(visualise_path), format=visualise_path.suffix.strip(".")
        )

    def run(
        self,
        feed_dir: Path,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        threshold: int,
    ):
        """Run the Prefect flow."""
        flow = self.build(
            feed_dir, base_dir, pdf_info_exe, pdf_text_exe, pdf_image_exe, threshold
        )
        flow.run()
