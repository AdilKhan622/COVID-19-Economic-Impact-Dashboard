"""Focused checks for the new indicator integration and derived metrics."""

import unittest
from pathlib import Path

import pandas as pd

from components.data_utils import DATA_PATH
from components.counterfactual import build_growth_counterfactual
from components.impact_index import STANDARDIZED_COLUMNS, build_economic_strain_index


class DashboardDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(DATA_PATH, low_memory=False)

    def test_unique_iso3_year_keys_and_extended_years(self):
        self.assertFalse(self.data.duplicated(["country_code", "year"]).any())
        self.assertEqual(int(self.data["year"].min()), 1960)
        self.assertEqual(int(self.data["year"].max()), 2025)

    def test_us_values_match_downloaded_world_bank_indicators(self):
        usa = self.data.loc[self.data.country_code.eq("USA")].set_index("year")
        self.assertAlmostEqual(usa.loc[2020, "real_gdp_growth_pct"], -2.081375977796, places=8)
        self.assertAlmostEqual(usa.loc[2020, "unemployment_rate_pct"], 8.055, places=8)
        self.assertAlmostEqual(usa.loc[2022, "inflation_rate_pct"], 8.00279982052121, places=8)

    def test_2019_baseline_metrics_are_percentage_point_differences(self):
        usa = self.data.loc[self.data.country_code.eq("USA")].set_index("year")
        self.assertAlmostEqual(usa.loc[2020, "gdp_growth_deterioration_vs_2019_pp"], 2.58382533052225 - (-2.081375977796), places=8)
        self.assertAlmostEqual(usa.loc[2020, "unemployment_change_vs_2019_pp"], 8.055 - 3.669, places=8)
        self.assertAlmostEqual(usa.loc[2022, "inflation_change_vs_2019_pp"], 8.00279982052121 - 1.8122100752602, places=8)

    def test_missing_economic_data_is_not_filled_with_zero(self):
        before_start = self.data.loc[self.data.year.eq(1960), "real_gdp_growth_pct"]
        self.assertTrue(before_start.isna().all())
        self.assertFalse((self.data["unemployment_rate_pct"].dropna() == 0).all())

    def test_output_is_separate_from_original_master(self):
        original = Path(__file__).resolve().parents[1] / "Data_cleaning/data/processed/merged_master_annual.csv"
        master = pd.read_csv(original, low_memory=False)
        self.assertEqual(len(master), 524)
        self.assertEqual(set(master["year"].astype(int)), {2020, 2021, 2022})
        self.assertEqual(len(self.data), 11859)


class CounterfactualTests(unittest.TestCase):
    @staticmethod
    def sample():
        rows = []
        for year in range(2010, 2020):
            rows.append({"country_code": "AAA", "year": year, "real_gdp_growth_pct": 2.0 if year < 2015 else 3.0, "region": "Region A", "income_group": "Group A"})
        rows.extend([
            {"country_code": "AAA", "year": 2020, "real_gdp_growth_pct": -2.0, "region": "Region A", "income_group": "Group A"},
            {"country_code": "AAA", "year": 2021, "real_gdp_growth_pct": 4.0, "region": "Region A", "income_group": "Group A"},
            {"country_code": "BBB", "year": 2015, "real_gdp_growth_pct": 1.0, "region": "Region B", "income_group": "Group B"},
            {"country_code": "BBB", "year": 2016, "real_gdp_growth_pct": 1.0, "region": "Region B", "income_group": "Group B"},
            {"country_code": "BBB", "year": 2017, "real_gdp_growth_pct": 1.0, "region": "Region B", "income_group": "Group B"},
            {"country_code": "AGG", "year": 2019, "real_gdp_growth_pct": 3.0, "region": None, "income_group": None},
            {"country_code": "AGG", "year": 2020, "real_gdp_growth_pct": -5.0, "region": None, "income_group": None},
        ])
        return pd.DataFrame(rows)

    def test_country_historical_growth_gap_and_sensitivity(self):
        result = build_growth_counterfactual(self.sample())
        row = result.loc[result.year.eq(2020)].iloc[0]
        self.assertEqual(row.country_code, "AAA")
        self.assertAlmostEqual(row.baseline_2015_19_pct, 3.0)
        self.assertAlmostEqual(row.actual_growth_pct, -2.0)
        self.assertAlmostEqual(row.growth_gap_vs_2015_19_baseline_pp, -5.0)
        self.assertAlmostEqual(row.baseline_2010_19_pct, 2.5)
        self.assertAlmostEqual(row.growth_gap_vs_2010_19_baseline_pp, -4.5)

    def test_excludes_insufficient_baselines_and_aggregate_rows(self):
        result = build_growth_counterfactual(self.sample())
        self.assertEqual(set(result.country_code), {"AAA"})

    def test_rejects_duplicate_country_year_keys(self):
        sample = self.sample()
        sample = pd.concat([sample, sample.iloc[[-1]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate country-year"):
            build_growth_counterfactual(sample)


class EconomicStrainIndexTests(unittest.TestCase):
    @staticmethod
    def sample():
        rows = []
        for year_offset, year in enumerate((2020, 2021, 2022)):
            for country_offset, code in enumerate(("AAA", "BBB", "CCC", "DDD")):
                rows.append({
                    "country_code": code,
                    "year": year,
                    "gdp_growth_deterioration_vs_2019_pp": country_offset + year_offset,
                    "unemployment_change_vs_2019_pp": country_offset * 2 + year_offset,
                    "inflation_change_vs_2019_pp": country_offset - year_offset,
                    "region": "Region A",
                    "income_group": "Group A",
                })
        rows.append({
            "country_code": "AGG", "year": 2020,
            "gdp_growth_deterioration_vs_2019_pp": 100,
            "unemployment_change_vs_2019_pp": 100,
            "inflation_change_vs_2019_pp": 100,
            "region": None, "income_group": None,
        })
        rows.append({
            "country_code": "MISS", "year": 2020,
            "gdp_growth_deterioration_vs_2019_pp": 2,
            "unemployment_change_vs_2019_pp": None,
            "inflation_change_vs_2019_pp": 3,
            "region": "Region A", "income_group": "Group A",
        })
        return pd.DataFrame(rows)

    def test_equal_weight_standardized_complete_case_index(self):
        result = build_economic_strain_index(self.sample())
        self.assertEqual(len(result), 12)
        self.assertNotIn("AGG", set(result.country_code))
        self.assertNotIn("MISS", set(result.country_code))
        self.assertTrue((result.economic_strain_index - result[list(STANDARDIZED_COLUMNS)].mean(axis=1)).abs().lt(1e-12).all())
        for column in STANDARDIZED_COLUMNS:
            self.assertAlmostEqual(result[column].mean(), 0.0, places=12)
        self.assertTrue((result.index_sample_n == 12).all())

    def test_inflation_decline_is_not_scored_as_pressure(self):
        result = build_economic_strain_index(self.sample())
        decline = result.loc[result.inflation_change_vs_2019_pp.lt(0)]
        self.assertTrue((decline.inflation_pressure_pp == 0).all())

    def test_rejects_duplicate_country_year_keys(self):
        sample = self.sample()
        sample = pd.concat([sample, sample.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate country-year"):
            build_economic_strain_index(sample)


if __name__ == "__main__":
    unittest.main()
