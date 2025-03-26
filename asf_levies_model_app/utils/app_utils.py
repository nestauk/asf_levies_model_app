import streamlit as st
import pandas as pd
import altair as alt

from typing import List, Dict

import asf_levies_model.getters.load_data as data

import asf_levies_model.levies as levies
import asf_levies_model.tariffs as tariffs

from asf_levies_model.levies import Levy, LevyCollection

from asf_levies_model.tariffs import ElectricityOtherPayment, GasOtherPayment

from asf_levies_model.consumers import Consumer, ConsumerCollection

from asf_levies_model.summary import create_scenario_weights_dict


def instantiate_levies(
    fileobject_annex_4,
    supply_elec: float = 96_517_461.0,  # MWh
    supply_gas: float = 266_505_188.0,  # MWh
    customers_elec: int = 29_239_936,
    customers_gas: int = 24_605_467,
) -> LevyCollection:

    denominator_values = {
        "supply_elec": supply_elec,
        "supply_gas": supply_gas,
        "customers_gas": customers_gas,
        "customers_elec": customers_elec,
    }

    # Scaling factor for estimating domestic share of FIT revenue
    total_supply_elec = (
        249_044_438  # DESNZ GB total electricity consumption - all meters (2023)
    )
    exempt_eii_supply = (
        10_529_633  # Apr-Jun2025 period, Annex 4, New FIT methodology tab
    )
    fit_scaling_factor = supply_elec / (total_supply_elec - exempt_eii_supply)

    # Scaling factor for estimating domestic share of NCC revenue
    ncc_eligible_supply = (
        119_380_310.7  # Mar-Jun2025 period, Annex 4, NCC methodology tab
    )
    ncc_scaling_factor = supply_elec / ncc_eligible_supply

    # Instantiate status quo levies with Annex 4 data
    list_levies = [
        levies.RO.from_dataframe(
            data.process_data_RO(fileobject_annex_4), denominator=supply_elec
        ),
        levies.AAHEDC.from_dataframe(
            data.process_data_AAHEDC(fileobject_annex_4), denominator=supply_elec
        ),
        levies.GGL.from_dataframe(
            data.process_data_GGL(fileobject_annex_4), denominator=customers_gas
        ),
        levies.WHD.from_dataframe(
            data.process_data_WHD(fileobject_annex_4),
            customers_gas=customers_gas,
            customers_elec=customers_elec,
        ),
        levies.ECO.from_dataframe(data.process_data_ECO(fileobject_annex_4)),
        levies.FIT.from_dataframe(
            data.process_data_FIT(fileobject_annex_4),
            scaling_factor=fit_scaling_factor,
        ),
        levies.NCC.from_dataframe(
            data.process_data_NCC(fileobject_annex_4), scaling_factor=ncc_scaling_factor
        ),
    ]

    pc = levies.LevyCollection("Policy Costs", "pc", list_levies, denominator_values)

    # Rebalance baseline levies to reflect denominators
    pc = pc.rebalance_to_denominators()

    return pc


def get_approach_weights(levies: List, approach_name: str) -> Dict:

    # "Current"
    baseline_weights = create_scenario_weights_dict(levies)

    # "Rebalance all levies on electricity to gas"
    all_gas_weights = create_scenario_weights_dict(levies)
    for levy in [levy for levy in levies if levy.electricity_weight > 0]:
        all_gas_weights[levy.short_name] = {
            "new_electricity_weight": 0.0,
            "new_gas_weight": 1.0,
            "new_tax_weight": 0.0,
            "new_variable_weight_elec": 0.0,
            "new_fixed_weight_elec": 0.0,
            "new_variable_weight_gas": levy.electricity_variable_weight,
            "new_fixed_weight_gas": levy.electricity_fixed_weight,
        }

    # "Rebalance RO and FIT levies from electricity to gas"
    rebalance_ro_fit_weights = create_scenario_weights_dict(levies)
    for levy in [levy for levy in levies if levy.short_name in ["ro", "fit"]]:
        rebalance_ro_fit_weights[levy.short_name] = {
            "new_electricity_weight": 0.0,
            "new_gas_weight": 1.0,
            "new_tax_weight": 0.0,
            "new_variable_weight_elec": 0.0,
            "new_fixed_weight_elec": 0.0,
            "new_variable_weight_gas": levy.electricity_variable_weight,
            "new_fixed_weight_gas": levy.electricity_fixed_weight,
        }

    # "Remove all levies on electricity to taxation"
    sq_electricity_removal_weights = create_scenario_weights_dict(levies)
    for levy in [levy.short_name for levy in levies if levy.electricity_weight > 0]:
        sq_electricity_removal_weights[levy]["new_tax_weight"] = (
            sq_electricity_removal_weights[levy]["new_electricity_weight"]
        )

        for weight_type in [
            "new_electricity_weight",
            "new_variable_weight_elec",
            "new_fixed_weight_elec",
        ]:
            sq_electricity_removal_weights[levy][weight_type] = 0.0

    # "Remove RO and FIT levies from electricity to taxation"
    remove_ro_fit_weights = create_scenario_weights_dict(levies)
    for levy in ["ro", "fit"]:
        remove_ro_fit_weights[levy]["new_tax_weight"] = remove_ro_fit_weights[levy][
            "new_electricity_weight"
        ]

        for weight_type in [
            "new_electricity_weight",
            "new_variable_weight_elec",
            "new_fixed_weight_elec",
        ]:
            remove_ro_fit_weights[levy][weight_type] = 0.0

    # Create lookup dictionary for weights of each approach
    approach_weights = {
        "Current": baseline_weights,
        "Rebalance all levies on electricity to gas": all_gas_weights,
        "Rebalance RO and FIT levies from electricity to gas": rebalance_ro_fit_weights,
        "Remove all levies on electricity to taxation": sq_electricity_removal_weights,
        "Remove RO and FIT levies from electricity to taxation": remove_ro_fit_weights,
    }

    if approach_name not in approach_weights.keys():
        raise ValueError("Rebalancing approach name not recognised.")

    return approach_weights[approach_name]


def instantiate_tariffs(
    fileobject_annex_9, payment_method: str = "Other Payment"
) -> Dict:

    # Load tariff tables from Annex 9
    # Other payment
    elec_other_payment_nil = data.process_tariff_elec_other_payment_nil(
        fileobject_annex_9
    )
    elec_other_payment_typical = data.process_tariff_elec_other_payment_typical(
        fileobject_annex_9
    )
    gas_other_payment_nil = data.process_tariff_gas_other_payment_nil(
        fileobject_annex_9
    )
    gas_other_payment_typical = data.process_tariff_gas_other_payment_typical(
        fileobject_annex_9
    )
    # Prepayment meter
    elec_ppm_nil = data.process_tariff_elec_ppm_nil(fileobject_annex_9)
    elec_ppm_typical = data.process_tariff_elec_ppm_typical(fileobject_annex_9)
    gas_ppm_nil = data.process_tariff_gas_ppm_nil(fileobject_annex_9)
    gas_ppm_typical = data.process_tariff_gas_ppm_typical(fileobject_annex_9)
    # Standard Credit
    elec_standard_credit_nil = data.process_tariff_elec_standard_credit_nil(
        fileobject_annex_9
    )
    elec_standard_credit_typical = data.process_tariff_elec_standard_credit_typical(
        fileobject_annex_9
    )
    gas_standard_credit_nil = data.process_tariff_gas_standard_credit_nil(
        fileobject_annex_9
    )
    gas_standard_credit_typical = data.process_tariff_gas_standard_credit_typical(
        fileobject_annex_9
    )

    # Instantiate Tariff objects
    if payment_method == "Other Payment":
        electricity_tariff = ElectricityOtherPayment.from_dataframe(
            elec_other_payment_nil, elec_other_payment_typical
        )
        gas_tariff = GasOtherPayment.from_dataframe(
            gas_other_payment_nil, gas_other_payment_typical
        )
    elif payment_method == "PPM":
        electricity_tariff = ElectricityOtherPayment.from_dataframe(
            elec_ppm_nil, elec_ppm_typical
        )
        gas_tariff = GasOtherPayment.from_dataframe(gas_ppm_nil, gas_ppm_typical)
    elif payment_method == "Standard Credit":
        electricity_tariff = ElectricityOtherPayment.from_dataframe(
            elec_standard_credit_nil, elec_standard_credit_typical
        )
        gas_tariff = GasOtherPayment.from_dataframe(
            gas_standard_credit_nil, gas_standard_credit_typical
        )
    else:
        raise ValueError("Payment method not recognised.")

    return {"electricity": electricity_tariff, "gas": gas_tariff}


def update_electricity_tariff_policy_cost(tariff, levies):
    tariff.pc_nil = sum([levy.calculate_levy(0, 0, True, False) for levy in levies])
    tariff.pc = sum([levy.calculate_levy(1, 0, False, False) for levy in levies])
    return tariff


def update_gas_tariff_policy_cost(tariff, levies):
    tariff.pc_nil = sum([levy.calculate_levy(0, 0, False, True) for levy in levies])
    tariff.pc = sum([levy.calculate_levy(0, 1, False, False) for levy in levies])
    return tariff


def instantiate_archetype_consumers(
    ofgem_archetypes_df: pd.DataFrame,
    gas_tariff: tariffs.Tariff,
    electricity_tariff: tariffs.Tariff,
):

    # Create list of Consumers (Average Ofgem archetypes only, n=24)
    consumers = [
        Consumer.consumer_from_dataframe(
            df=ofgem_archetypes_df,
            row=row,
            name_col="AnnualConsumptionProfile",
            archetype_col="AnnualConsumptionProfile",
            net_annual_income_col="NetAnnualHouseholdIncome",
            main_heating_fuel_col="ArchetypeHeatingFuel",
            gas_consumption_col="GaskWh",
            electricity_consumption_col="ElectricitySingleRatekWh",
            gas_tariff=gas_tariff,
            electricity_tariff=electricity_tariff,
            unit_converter=1_000,
        )
        for row in range(1, 25)
    ]

    return consumers


def instantiate_archetype_consumers_with_eligibility(
    ofgem_archetypes_df: pd.DataFrame,
    gas_tariff: tariffs.Tariff,
    electricity_tariff: tariffs.Tariff,
):

    # Create list of eligible Consumers (Average Ofgem archetypes only, n=24)
    eligible_consumers = [
        Consumer(
            name=ofgem_archetypes_df.loc[row, "AnnualConsumptionProfile"],
            archetype=ofgem_archetypes_df.loc[row, "AnnualConsumptionProfile"],
            net_annual_income=ofgem_archetypes_df.loc[row, "NetAnnualHouseholdIncome"],
            net_income_decile=ofgem_archetypes_df.loc[row, "NetIncomeDecile"],
            main_heating_fuel=ofgem_archetypes_df.loc[row, "ArchetypeHeatingFuel"],
            gas_consumption=ofgem_archetypes_df.loc[row, "GaskWh"] / 1_000,
            electricity_consumption=ofgem_archetypes_df.loc[
                row, "ElectricitySingleRatekWh"
            ]
            / 1_000,
            gas_tariff=gas_tariff,
            electricity_tariff=electricity_tariff,
            scheme_eligible=True,
        )
        for row in range(1, 25)
    ]

    # Create list of ineligible Consumers (Average Ofgem archetypes only, n=24)
    ineligible_consumers = [
        Consumer(
            name=ofgem_archetypes_df.loc[row, "AnnualConsumptionProfile"],
            archetype=ofgem_archetypes_df.loc[row, "AnnualConsumptionProfile"],
            net_annual_income=ofgem_archetypes_df.loc[row, "NetAnnualHouseholdIncome"],
            net_income_decile=ofgem_archetypes_df.loc[row, "NetIncomeDecile"],
            main_heating_fuel=ofgem_archetypes_df.loc[row, "ArchetypeHeatingFuel"],
            gas_consumption=ofgem_archetypes_df.loc[row, "GaskWh"] / 1_000,
            electricity_consumption=ofgem_archetypes_df.loc[
                row, "ElectricitySingleRatekWh"
            ]
            / 1_000,
            gas_tariff=gas_tariff,
            electricity_tariff=electricity_tariff,
            scheme_eligible=True,
        )
        for row in range(1, 25)
    ]
    return eligible_consumers, ineligible_consumers


def calculate_unit_cost_ratio(electricity_tariff, gas_tariff):
    return electricity_tariff.calculate_variable_consumption(
        1
    ) / gas_tariff.calculate_variable_consumption(1)


def instantiate_new_levy(
    new_levy_name,
    new_levy_revenue,
    new_levy_fuel,
    new_levy_type,
    supply_elec,
    customers_elec,
    supply_gas,
    customers_gas,
):

    electricity_fixed_weight = (
        1
        if (new_levy_fuel == "Electricity") & (new_levy_type == "Standing charge")
        else 0
    )
    electricity_variable_weight = (
        1 if (new_levy_fuel == "Electricity") & (new_levy_type == "Consumption") else 0
    )
    gas_variable_weight = (
        1 if (new_levy_fuel == "Gas") & (new_levy_type == "Consumption") else 0
    )
    gas_fixed_weight = (
        1 if (new_levy_fuel == "Gas") & (new_levy_type == "Standing charge") else 0
    )

    new_levy = Levy(
        name=new_levy_name,
        short_name=new_levy_name,
        electricity_weight=1 if new_levy_fuel == "Electricity" else 0,
        gas_weight=1 if new_levy_fuel == "Gas" else 0,
        tax_weight=0,
        electricity_variable_weight=electricity_variable_weight,
        electricity_fixed_weight=electricity_fixed_weight,
        gas_variable_weight=gas_variable_weight,
        gas_fixed_weight=gas_fixed_weight,
        electricity_variable_rate=(new_levy_revenue / supply_elec)
        * electricity_variable_weight,
        electricity_fixed_rate=(new_levy_revenue / customers_elec)
        * electricity_fixed_weight,
        gas_variable_rate=(new_levy_revenue / supply_gas) * gas_variable_weight,
        gas_fixed_rate=(new_levy_revenue / customers_gas) * gas_fixed_weight,
        general_taxation=0,
        revenue=new_levy_revenue,
        price_cap_period="LATEST",
    )

    return new_levy


def get_tidy_summary(consumers, scenario_name):
    tidy_summary = pd.concat([consumer.get_tidy_summary() for consumer in consumers])
    tidy_summary["Scenario"] = scenario_name
    return tidy_summary


def tidy_to_pivot_summary(tidy_summary):
    pivot_summary_table = tidy_summary.pivot_table(
        index=["Name", "Scenario"], columns="Attribute", values="Value", aggfunc="first"
    ).reset_index()
    pivot_summary_table = pivot_summary_table[
        [
            "Name",
            "Scenario",
            "main_heating_fuel",
            "electricity_bill",
            "gas_bill",
            "combined_fuel_bill",
            "fuel_poverty_gap",
        ]
    ].sort_values(by=["Scenario", "Name"])
    return pivot_summary_table


def make_archetype_bill_change_chart(rebalanced_summary_table, chart_width=1000):

    # Fuel colours
    cmap_2 = {
        "Electricity": "#15A38C",
        "Electricity/Other": "#d8d2ca",
        "Gas": "#0000ff",
        "Other": "#F6B0C0",
    }

    chart = alt.Chart(rebalanced_summary_table)
    # Dots
    points = chart.mark_point(opacity=1, filled=True).encode(
        x=alt.X(
            "bill_change:Q",
            axis=alt.Axis(grid=True),
            title="Bill change with respect to bill under status quo levies and social support (£)",
            scale=alt.Scale(domain=[-850, 450]),
        ),
        y=alt.Y(
            "Name:N",
            axis=alt.Axis(grid=True, labelLimit=500),
            sort=None,
            title="Energy consumer archetype (Lowest (A) to highest (J) income)",
        ),
        size=alt.Size("ArchetypeSize:Q", title="No. of households"),
        color=alt.Color(
            "main_heating_fuel:N",
            scale=alt.Scale(domain=list(cmap_2.keys()), range=list(cmap_2.values())),
            title="Main heating fuel",
        ),
    )
    # x=0 base line
    rule = chart.mark_rule(strokeDash=[2, 2]).encode(x=alt.datum(0))
    # Layer dots and line
    chart = alt.layer(points, rule).properties(width=chart_width)
    chart = chart.configure_axis(
        labelColor="black", titleColor="black"
    ).configure_legend(labelColor="black", titleColor="black")

    return chart
