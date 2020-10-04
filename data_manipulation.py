# Import libraries
import logging.config
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Initialize log
logger = logging.getLogger(__name__)


class DataManipulation:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def active_profiles(self, dataframe, date_col="updated_time", active_days=30):
        """"
            Returns the active profile for the given dataframe based on the active days
            Inputs:
                dataframe   : dataframe of a table (pandas dataframe)
                date_col    : columns to apply active days (str)
                                default value is "updated_time"
                active_days : no. of active days from current date (int)
                                default value is 30
            Outputs:
                active_profile_df : dataframe of active profile (pandas dataframe)
        """
        active_datetime = datetime.today() - timedelta(active_days)
        self.logger(f'Active profiles from the date - {active_datetime}')
        active_profile_df = dataframe[dataframe[date_col] >= active_datetime]

        return active_profile_df

    def certificate_trend(
        self, certificate_df, compl_col="certificate_completion_date", active_days=730
    ):

        active_datetime = datetime.today() - timedelta(active_days)
        cert_trend_df = certificate_df[certificate_df[compl_col]
                                       >= active_datetime]

        return cert_trend_df

    def work_aggregation(
        self,
        dataframe,
        work_start_date="start_date",
        work_end_date="end_date",
        emp_type_col="employeement_type",
    ):
        """
            Aggregate candidate work information, returns the aggregated dataframe
            Inputs:
                dataframe       : active profile dataframe (pandas dataframe)
                work_start_date : start date of work column (str)
                                    default value is "start_date"
                work_end_date   : end date of work column (str)
                                    default value is "end_date"
                emp_type_col    : type of employment column (str)
                                    default value is "employeement_type"
            Outputs:
                work_agg_df : dataframe of work aggregated value (pandas dataframe)
        """

        dataframe.loc[:, "exp_date_diff"] = (
            dataframe[work_end_date].values - dataframe[work_start_date].values
        )
        dataframe.loc[:, "exp_days"] = dataframe["exp_date_diff"] // np.timedelta64(
            1, "D"
        )
        dataframe.loc[:, "exp_years"] = dataframe["exp_date_diff"] // np.timedelta64(
            1, "Y"
        )

        dataframe.loc[:, "contract_2y"] = ~(
            (dataframe[emp_type_col] == "Contracting") & (
                dataframe["exp_years"] <= 2)
        )

        work_agg_df = (
            dataframe.groupby("emp_id")
            .agg(
                total_exp=("exp_years", "sum"),
                total_switch=("work_exp_id", "count"),
                switch_rel=("contract_2y", "sum"),
                no_of_domain=("domain", "nunique"),
            )
            .astype({"switch_rel": "int"})
            .reset_index()
        )

        return work_agg_df

    def category_ratio(self, dataframe, category_col):
        """
            Calculate category ratio, returns the ratio dataframe
            Inputs:
                dataframe       : dataframe of a table (pandas dataframe)
                category_col    : category column name (str)
            Output:
                category_ratio_df : dataframe of a categorical value ratio (pandas dataframe)

        """
        category_ratio_df = (
            (dataframe[category_col].value_counts(normalize=True) * 100)
            .astype("int")
            .to_frame()
            .reset_index()
            .rename(
                columns={"index": category_col,
                         category_col: f"{category_col}_ratio"}
            )
        )

        return category_ratio_df
