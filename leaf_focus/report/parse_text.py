import logging

import contextualSpellCheck

from leaf_focus.ocr.found_text import FoundText


class ParseText:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

        import spacy

        # self._nlp_gpu = spacy.prefer_gpu()
        self._nlp = spacy.load("en_core_web_lg")
        contextualSpellCheck.add_to_pipe(self._nlp)
        print(self._nlp.pipe_names)

    def start(
        self,
        text_info: dict,
        text_extracted: list[str],
        text_found: list[list[FoundText]],
    ):
        # TODO: figure out a robust way to turn the semi-structured text from the two sources into
        #       a structured csv file. Maybe pyparsing might be more useful than SpaCy?
        doc = self._nlp("This is a sentence.")
        for token in doc:
            print(token.text, token.has_vector, token.vector_norm, token.is_oov)

        # Doc Extension
        print(doc._.contextual_spellCheck)
        print(doc._.performed_spellCheck)
        print(doc._.suggestions_spellCheck)
        print(doc._.outcome_spellCheck)
        print(doc._.score_spellCheck)

        a = 1

    def _find_text(self, text: str, to_find: list[str]):
        if text in to_find:
            return True, "whole"
        if any([text.startswith(t) for t in to_find]):
            return True, "start"
        if any([text.endswith(t) for t in to_find]):
            return True, "end"
        if any([text in t for t in to_find]):
            return True, "contains"
        return False, None

    def _extract(self, lines: list[list[FoundText]]):
        # TODO
        find_text = [
            ("self", "", ["self"]),
            ("spouse", "", ["spouse"]),
            ("children", "", ["dependent", "children"]),
            ("last_name", "", ["surname", "please print"]),
            ("first_name", self._match_first_name, ["other names"]),
            ("electorate", "", ["electoral division", "electoral division state"]),
            (
                "companies",
                "",
                [
                    "shareholdings in public and private companies",
                    "the name of the company",
                ],
            ),
        ]
        for line_index, line_item in enumerate(lines):
            text = " ".join([i.text for i in line_item]).lower()

            for name, func, match in find_text:
                is_match, where_match = self._find_text(text, match)
                if not is_match:
                    continue

    def _match_first_name(
        self,
        lines: list[list[FoundText]],
        line_index: int,
        line_item: list[FoundText],
        text: str,
        where_match: str,
    ):
        # TODO
        a = 1
