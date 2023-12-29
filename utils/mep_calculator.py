from cocos_query.extract_data import CocosDataExtractor
from iolApi.extract_data import IolDataExtractor
import pandas as pd


class MepCalculator:

    def __init__(self, selected_data_extractor_name, asset_type="cedear"):
        switch_dict = {
            "IOL": IolDataExtractor,
            "Yahoo": "",
            "Cocos": CocosDataExtractor,
        }

        selected_data_extractor = switch_dict.get(selected_data_extractor_name)

        self.data_extractor_instance = selected_data_extractor()
        self.data_extractor_instance.run()
        self.queried_data = self.data_extractor_instance.clean_df
        self.asset_type = asset_type

        self.merged_df = None

    def join_with_asset_data(self):
        """Join with cedear data to get the ratio, the currency and the base symbol"""
        cedear_ratios = pd.read_excel("../data/cedear_ratios_reloaded.xlsx", sheet_name=self.asset_type)
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
            cedear_cross_joined["base_symbol_x"] == cedear_cross_joined["base_symbol_y"]]
        cedear_cross_joined["conversion"] = (
                cedear_cross_joined["symbol_x"] + " " + cedear_cross_joined["settlementPeriod_x"].astype(str) + "h - "
                + cedear_cross_joined["symbol_y"] + " " + cedear_cross_joined["settlementPeriod_y"].astype(str) + "h")

        self.merged_df = cedear_cross_joined

    def calculate_mep(self):
        """Calculate ratio between outside price vs local"""
        self.merged_df.loc[:, 'x/y mid'] = self.merged_df['open_x'] / self.merged_df['open_y']
        self.merged_df.loc[:, "x/y ask"] = self.merged_df["ask_x"] / self.merged_df["bid_y"]
        self.merged_df.loc[:, "x/y bid"] = self.merged_df["bid_x"] / self.merged_df["ask_y"]

    def run(self):
        self.join_with_asset_data()
        self.cross_join_df()
        self.calculate_mep()


if __name__ == "__main__":
    comb = MepCalculator(selected_data_extractor_name="IOL", asset_type="cedear")
    comb.run()
    data_df = comb.merged_df
