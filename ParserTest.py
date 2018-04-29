import unittest

from Parser import Parser


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser("")

    def test_parse_rational_number(self):
        parser = Parser("")
        result = parser.parse("3.55555 5 7.9")
        self.assertSetEqual({"3.56", '5', '7.90'}, set(result.keys()))

    def test_parse_big_numbers(self):
        result = self.parser.parse("1,345")
        self.assertSetEqual({"1345"}, set(result.keys()))

    def test_parse_number(self):
        result = self.parser.parse("14")
        self.assertSetEqual({"14"}, set(result.keys()))

    def test_parse_present(self):
        result = self.parser.parse("6%")
        self.assertSetEqual({"6 percent"}, set(result.keys()))

    def test_parse_present_in_sentence(self):
        result = self.parser.parse("is under 75 percent of the average")
        result2 = self.parser.parse("is under 75 percentage of the average")
        self.assertSetEqual({"is", "under", "75 percent", "of", "the", "average"}, set(result.keys()))
        self.assertSetEqual({"is", "under", "75 percent", "of", "the", "average"}, set(result2.keys()))

    def test_parse_present_with_float(self):
        result = self.parser.parse("average 12,550.666 percent")
        self.assertSetEqual({"average", "12550.67 percent"}, set(result.keys()))

    def test_parse_date(self):
        result = self.parser.parse("the 12th MAY 1991 last")
        self.assertSetEqual({"the", "12/05/1991", "last"}, set(result.keys()))

    def test_parse_date_type_2(self):
        result = self.parser.parse("16 FEB 1991 7")
        self.assertSetEqual({"16/02/1991", "7"}, set(result.keys()))

    def test_parse_date_type_3(self):
        result = self.parser.parse("13 May 91")
        self.assertSetEqual({"13/05/1991"}, set(result.keys()))

    def test_parse_date_type_4(self):
        result = self.parser.parse("Feb 12, 1990 hello")
        self.assertSetEqual({"12/02/1990", "hello"}, set(result.keys()))

    def test_parse_date_type_5(self):
        result = self.parser.parse("12th Jan 1991")
        self.assertSetEqual({"12/01/1991"}, set(result.keys()))

    def test_parse_date_type_6(self):
        result = self.parser.parse("30 September 2006")
        self.assertSetEqual({"30/09/2006"}, set(result.keys()))

    def test_parse_date_type_7(self):
        result = self.parser.parse("21 DEC 09")
        self.assertSetEqual({"21/12/2009"}, set(result.keys()))

    def test_parse_date_type_8(self):
        result = self.parser.parse("JUNE 15, 2000")
        self.assertSetEqual({"15/06/2000"}, set(result.keys()))

    def test_parse_date_type_9(self):
        result = self.parser.parse("01 Aug 1880")
        self.assertSetEqual({"01/08/1880"}, set(result.keys()))

    def test_parse_date_type_10(self):
        result = self.parser.parse("08th July 2017")
        self.assertSetEqual({"08/07/2017"}, set(result.keys()))

    def test_parse_date_type_11(self):
        result = self.parser.parse("04 MAY go to")
        self.assertSetEqual({"04/05", "go", "to"}, set(result.keys()))

    def test_parse_date_type_12(self):
        result = self.parser.parse("June 4")
        self.assertSetEqual({"04/06"}, set(result.keys()))

    def test_parse_date_type_13(self):
        result = self.parser.parse("May 1994")
        self.assertSetEqual({"05/1994"}, set(result.keys()))

    def test_parse_date_normal_month_year(self):
        result = self.parser.parse("05/1994")
        self.assertSetEqual({"05/1994"}, set(result.keys()))

    def test_parse_date_normal_day_month(self):
        result = self.parser.parse("14/05")
        self.assertSetEqual({"14/05"}, set(result.keys()))

    def test_parse_date_normal_day_month_year(self):
        result = self.parser.parse("12/05/1991")
        self.assertSetEqual({"12/05/1991"}, set(result.keys()))

    def test_parse_date_month_day(self):
        result = self.parser.parse("sep 07")
        self.assertSetEqual({"07/09"}, set(result.keys()))

    def test_parse_text_with_upper_case_words(self):
        text = "Jiang Zemin Wow today the Chinese Army to Strengthen"
        result = self.parser.parse(text)
        expected = {"jiang zemin", "jiang", "zemin", "today", "wow", "the", "chinese army", "chinese", "army", "to",
                    "strengthen"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dates(self):
        text = "3 mission 5 NBA of 12 September 2006 and JULY 22 win 33-44 test-case"
        result = self.parser.parse(text)
        expected = {"3", "mission", "nba", "5", "of", "12/09/2006", "and", "22/07", "win", "33", "44",
                    "test case", "test", "case"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dates_2(self):
        text = "long gilt future moved down  1/16 to trade around 103 1/32 ."
        result = self.parser.parse(text)
        expected = {"long", "gilt", "future", "moved", "down", "1/16", "to", "trade", "around", "103", "1/32"}
        self.assertSetEqual(set(result.keys()), expected)


    def test_parse_text(self):
        text = '''Jiang Zemin 5.79 today the Chinese Army 4 to strengthen its
    own building mission of 12 September 2006 and JULY 22
    after May 11 1999 at the 4 SEP and JUNE 2005'''
        result = self.parser.parse(text)
        expected = {"jiang zemin", "jiang", "zemin", "5.79", "today", "the", "chinese army", "chinese", "army", "4",
                    "to", "strengthen", "its", "own", "building", "mission", "of", "12/09/2006", "and", "22/07",
                    "after", "11/05/1999", "at", "the", "04/09", "and", "06/2005"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dollar(self):
        text = "hello to all of you i am $20 min away"
        result = self.parser.parse(text)
        expected = {"hello", "to", "all", "of", "you", "i", "am", "20 dollar", "min", "away"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dollar_2(self):
        text = "reserves were valued at U.S.$664.44 million"
        result = self.parser.parse(text)
        expected = {"reserves", "were", "valued", "at", "664.44 dollar", "million"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dollar_3(self):
        text = "Soviet Union (Kc19.8 billion, $660 million)"
        result = self.parser.parse(text)
        expected = {'million', 'soviet', 'soviet union', 'union', 'kc19.8', 'billion', '660 dollar'}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dash(self):
        text = "Soviet Union ($1,000/ton) followed by $2.67 billion"
        result = self.parser.parse(text)
        expected = {"soviet", "union", "soviet union", "1000 dollar", "ton", "followed", "by", "2.67 dollar", "billion"}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_million_billion_dollar(self):
        text = "$5.67m Union ^ $12b and $45m and $8.45bn"
        result = self.parser.parse(text)
        expected = {'8.45 dollar', 'million', 'union', '12 dollar', '45 dollar', 'and', 'billion', '5.67 dollar'}
        self.assertSetEqual(set(result.keys()), expected)

    def test_parse_text_with_dash_2(self):
        text = "3000-text $400-  $600-me"
        result = self.parser.parse(text)
        expected = {'3000', 'text', '400 dollar', 'me', '600 dollar'}
        self.assertSetEqual(set(result.keys()), expected)


if __name__ == '__main__':
    unittest.main()
