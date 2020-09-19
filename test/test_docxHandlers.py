import unittest
from src.acroHandlers import acroDictHandler
from src.docxHandlers import docxReader


class TestDocxMethods(unittest.TestCase):

    def setUp(self):
        self.docx_test = "doc_testing_1.docx"

        self.acros_expected = ["ACROÁ", "ACROAB", "ACROBOLD", "ACROBULLET", "ACRODOCPROP", "ACROÉ", "ACROESPAÑA",
                               "ACROFONT", "ACROFOOTER", "ACROFOOTERSECTWO", "ACROHEADER", "ACROHEADERSECTWO",
                               "ACROHEADERTB", "ACROÍ", "ACROINPAR", "ACROITALIC", "ACRONUM", "ACROÓ", "ACROONCE",
                               "ACROPN", "ACROQMARK", "ACROREPEAT", "ACROSUB", "ACROTBBREAK", "ACROTBCOMBINEDONE",
                               "ACROTBCOMBINEDTHREE", "ACROTBCOMBINEDTWO", "ACROTBLINE", "ACROTBSIMPLE", "ACROTITLE",
                               "ACROÚ", "BREAKS", "ID", "TCACROADD", "TCACROFIX", "TCACROFOOTERADD", "TCACROIN",
                               "TCACROTBADD", "TCACROTBADDNEW", "VERYLONGACRONYM"]

        self.len_acros_expected = len(self.acros_expected)

    def test_no_acronyms(self):
        acro_dict_handler = acroDictHandler.AcroDictHandler()
        docxReader.extract_acro_word("doc_no_acronyms.docx", acro_dict_handler)

        # Check if when there are no acronyms no exception is raised and nothing reported
        self.assertEqual(len(acro_dict_handler.acros_found.keys()), 0)

    def test_find_acronyms(self):
        acro_dict_handler = acroDictHandler.AcroDictHandler()
        docxReader.extract_acro_word(self.docx_test, acro_dict_handler)

        # Check all expected acronyms
        for acro_ex in self.acros_expected:
            self.assertIn(acro_ex, acro_dict_handler.acros_found.keys())

        # Check if more acros than expected are found
        self.assertEqual(len(self.acros_expected), len(acro_dict_handler.acros_found.keys()))

    def test_acro_table_acronyms(self):
        acro_dict_handler = acroDictHandler.AcroDictHandler()
        docxReader.extract_acro_word(self.docx_test, acro_dict_handler)

        # Check the ordering
        self.assertTrue(False)  # Test to be defined

    def test_sort_acronyms(self):
        acro_dict_handler = acroDictHandler.AcroDictHandler()
        docxReader.extract_acro_word(self.docx_test, acro_dict_handler)

        # Check the ordering
        self.assertTrue(False)  # Test to be defined


if __name__ == '__main__':
    unittest.main()
