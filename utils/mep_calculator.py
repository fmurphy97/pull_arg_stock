from cocos_query.extract_data import CocosDataExtractor
from iolApi.extract_data import IolDataExtractor
from yahoo.extract_data import YahooDataExtractor
from pathlib import Path
import pandas as pd


class MepCalculator:
    switch_dict = {
        "IOL": IolDataExtractor,
        "Yahoo": YahooDataExtractor,
        "Cocos": CocosDataExtractor,
    }

    def __init__(self, selected_data_extractor_name, asset_type="cedear"):
        selected_data_extractor = MepCalculator.switch_dict.get(selected_data_extractor_name)

        self.data_extractor_instance = selected_data_extractor()
        self.data_extractor_instance.run()
        self.queried_data = self.data_extractor_instance.clean_df
        self.asset_type = asset_type

        self.merged_df = None

    def join_with_asset_data(self):
        """Join with cedear data to get the ratio, the currency and the base symbol"""
        ratios_data_path = Path(__file__).parent.parent.joinpath("data", "cedear_ratios_reloaded.xlsx")
        cedear_ratios = pd.read_excel(ratios_data_path, sheet_name=self.asset_type)
        df_merged = pd.merge(self.queried_data, cedear_ratios, on="symbol", how="left")
        self.merged_df = df_merged

    def cross_join_df(self):
        """Split into ARS vs other currency"""
        df = self.merged_df.copy()
        df_local_ars = df[(df["exchange"] == "BUE") & (df["currency"] == "ARS")]

        df = self.merged_df.copy()
        df_local_other = df[(df["exchange"] == "BUE") & (df["type"] == "dolar")]

        # Cross join the ARS vs other currency
        cedear_cross_joined = pd.merge(df_local_ars, df_local_other, how="cross")
        cedear_cross_joined = cedear_cross_joined[
            cedear_cross_joined["base_symbol_x"] == cedear_cross_joined["base_symbol_y"]
            ]
        self.merged_df = cedear_cross_joined

    def calculate_mep(self):
        """Calculate ratio between outside price vs local"""
        self.merged_df.loc[:, 'x/y mid'] = self.merged_df['open_x'] / self.merged_df['open_y']
        self.merged_df.loc[:, "x/y ask"] = self.merged_df["ask_x"] / self.merged_df["bid_y"]
        self.merged_df.loc[:, "x/y bid"] = self.merged_df["bid_x"] / self.merged_df["ask_y"]

        self.merged_df["vol_value_x"] = self.merged_df["volume_x"] * self.merged_df["open_x"]
        self.merged_df["vol_value_y"] = self.merged_df["volume_y"] * self.merged_df["open_y"]
        self.merged_df["spread_x"] = ((self.merged_df["ask_x"] - self.merged_df["bid_x"]).abs() * 2 /
                                      (self.merged_df["ask_x"] + self.merged_df["bid_x"]))
        self.merged_df["spread_y"] = ((self.merged_df["ask_y"] - self.merged_df["bid_y"]).abs() * 2 /
                                      (self.merged_df["ask_y"] + self.merged_df["bid_y"]))
        self.merged_df["max_spread"] = self.merged_df[['spread_x', 'spread_y']].max(axis=1)

    def export_to_csv(self):
        export_path = Path(__file__).parent.parent.joinpath("data", "df_mep.csv")
        self.merged_df.to_csv(export_path, index=False)

    def outlier_removal(self):
        """Removes any outliers"""
        pass

    def data_validation(self):
        """Check that ask > bid"""
        pass

    def run(self, export_results=True):
        self.join_with_asset_data()
        self.cross_join_df()
        self.calculate_mep()

        if export_results:
            self.export_to_csv()


if __name__ == "__main__":
    comb = MepCalculator(selected_data_extractor_name="IOL", asset_type="cedear")
    comb.run()
    data_df = comb.merged_df
