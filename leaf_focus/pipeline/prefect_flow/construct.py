from pathlib import Path

from prefect import Flow, flatten, unmapped, Parameter
from prefect.executors import DaskExecutor

from leaf_focus.download.crawl.prefect_task import DownloadCrawlTask
from leaf_focus.ocr.prepare.prefect_task import OcrPrepareTask
from leaf_focus.pdf.identify.prefect_task import PdfIdentifyTask
from leaf_focus.pdf.images.prefect_task import PdfImagesLoadTask
from leaf_focus.pdf.images.prefect_task import PdfImagesTask
from leaf_focus.pdf.info.prefect_task import PdfInfoTask
from leaf_focus.pdf.text.prefect_task import PdfTextTask


class Construct:
    def build_full(
        self,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
    ):
        """Build the full Prefect flow."""

        with Flow("leaf-focus") as flow:
            feed_dir = Parameter("feed_dir")
            threshold = Parameter("threshold")

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
            ocr_prepare_task.map(
                input_item=flatten(pdf_image_items),
                threshold=unmapped(threshold),
            )

            # NOTE: Cannot run OCR as part of the Prefect flow.
            # ocr_recognise_task = OcrRecogniseTask(base_dir)
            # ocr_recognise_task.map(
            #     input_item=flatten(ocr_prepare_items),
            #     threshold=unmapped(threshold),
            #     ocr_wrapper=ocr_resource,
            # )

        return flow

    def build_pdf(
        self,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
    ):
        """Build the pdf Prefect flow."""

        with Flow("leaf-focus") as flow:
            feed_dir = Parameter("feed_dir")

            download_task = DownloadCrawlTask()
            download_items = download_task(feed_dir)

            pdf_identify_task = PdfIdentifyTask(base_dir)
            pdf_identify_items = pdf_identify_task.map(download_items)

            pdf_info_task = PdfInfoTask(base_dir, pdf_info_exe)
            pdf_info_task.map(pdf_identify_items)

            pdf_text_task = PdfTextTask(base_dir, pdf_text_exe)
            pdf_text_task.map(pdf_identify_items)

            pdf_images_task = PdfImagesTask(base_dir, pdf_image_exe)
            pdf_images_task.map(pdf_identify_items)

        return flow

    def build_ocr(self, base_dir: Path):
        """Build the ocr Prefect flow."""

        with Flow("leaf-focus") as flow:
            threshold = Parameter("threshold")

            pcf_image_task = PdfImagesLoadTask(base_dir)
            pdf_image_items = pcf_image_task()

            ocr_prepare_task = OcrPrepareTask(base_dir)
            ocr_prepare_task.map(
                input_item=pdf_image_items,
                threshold=unmapped(threshold),
            )

            # NOTE: Cannot run OCR as part of the Prefect flow.
            # ocr_recognise_task = OcrRecogniseTask(base_dir)
            # ocr_recognise_task.map(
            #     input_item=ocr_prepare_items,
            #     threshold=unmapped(threshold),
            #     ocr_wrapper=ocr_resource,
            # )

        return flow

    def visualise(
        self,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        visualise_path: Path,
    ):
        """Visualise the Prefect flow."""
        flow = self.build_full(base_dir, pdf_info_exe, pdf_text_exe, pdf_image_exe)
        flow.visualize(
            filename=str(visualise_path.with_suffix("")),
            format=visualise_path.suffix.strip("."),
        )

    def run_full(
        self,
        feed_dir: Path,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        threshold: int,
        serial: bool = False,
    ):
        """Run the Prefect flow."""
        flow = self.build_full(base_dir, pdf_info_exe, pdf_text_exe, pdf_image_exe)

        if not serial:
            dask_executor = DaskExecutor()
            flow.run(executor=dask_executor, feed_dir=feed_dir, threshold=threshold)
        else:
            flow.run(feed_dir=feed_dir)

    def run_pdf(
        self,
        feed_dir: Path,
        base_dir: Path,
        pdf_info_exe: Path,
        pdf_text_exe: Path,
        pdf_image_exe: Path,
        serial: bool = False,
    ):
        """Run the pdf Prefect flow."""
        flow = self.build_pdf(base_dir, pdf_info_exe, pdf_text_exe, pdf_image_exe)

        if not serial:
            dask_executor = DaskExecutor()
            flow.run(executor=dask_executor, feed_dir=feed_dir)
        else:
            flow.run(feed_dir=feed_dir)

    def run_ocr(
        self,
        base_dir: Path,
        threshold: int,
        serial: bool = False,
    ):
        """Run the ocr Prefect flow."""
        flow = self.build_ocr(
            base_dir,
        )
        if not serial:
            dask_executor = DaskExecutor()
            flow.run(executor=dask_executor, threshold=threshold)
        else:
            flow.run()
