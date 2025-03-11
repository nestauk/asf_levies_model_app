import streamlit as st

from asf_levies_model_app.utils.app_utils import (
    instantiate_levies,
    get_approach_weights,
    instantiate_tariffs,
    update_electricity_tariff_policy_cost,
    update_gas_tariff_policy_cost,
    instantiate_archetype_consumers,
    calculate_unit_cost_ratio,
    get_tidy_summary,
    tidy_to_pivot_summary,
    make_archetype_bill_change_chart,
)

from asf_levies_model.summary import (
    set_common_denominators,
    create_scenario_weights_dict,
)
import asf_levies_model.levies as levies
import asf_levies_model.getters.load_data as data

st.set_page_config(
    page_title="Nesta Levies Rebalancing Model", page_icon="🏠", layout="wide"
)

st.title("Levies Rebalancing App💡")
st.markdown(
    "**from the [A Sustainable Future](https://www.nesta.org.uk/sustainable-future/) team at Nesta**"
)

# Instantiate baseline levies as LevyCollection (rebalanced to denominators)
levies = instantiate_levies()

# Create dictionary of denominators for each levy
supply_elec = 96_517_461.0
supply_gas = 266_505_188.0
customers_elec = 29_239_936
customers_gas = 24_605_467

denominators = set_common_denominators(
    levies,
    supply_elec=supply_elec,
    supply_gas=supply_gas,
    customers_elec=customers_elec,
    customers_gas=customers_gas,
)

# Show selectors for levy reform scenario in side bar
with st.sidebar:
    st.info(
        "**Test a levy reform scenario** by adjusting the settings below. *Note: You can hide or adjust the width of this sidebar.*"
    )

    # User input to choose rebalancing approach
    approach = st.radio(
        "**Select a preset approach or create your own:**",
        [
            "Current",
            "Rebalance all levies on electricity to gas",
            "Remove all levies on electricity to taxation",
            "Rebalance RO and FIT levies from electricity to gas",
            "Remove RO and FIT levies from electricity to taxation",
            "Create my own",
        ],
        index=0,
    )

    if approach == "Create my own":
        rebalancing_weights = create_scenario_weights_dict(levies)

        for levy in levies:

            # Rebalance or move to tax
            st.markdown("---")
            mode = st.radio(
                f"**{levy.name}**",
                [
                    "Rebalance between electricity and gas",
                    "Remove off bills to general taxation",
                ],
                index=0,
                key=f"{levy.short_name}_radio",
            )

            # Rebalancing weights: Fuel
            if (
                st.session_state[f"{levy.short_name}_radio"]
                == "Rebalance between electricity and gas"
            ):
                rebalancing_weights[levy.short_name]["new_tax_weight"] = 0.0
                rebalancing_weights[levy.short_name]["new_gas_weight"] = (
                    st.slider(
                        "Electricity (0) <-> Gas (100)",
                        value=(rebalancing_weights[levy.short_name]["new_gas_weight"])
                        * 100.0,
                        min_value=0.0,
                        max_value=100.0,
                        step=1.0,
                        key=f"{levy.short_name}_rebalancing_slider",
                    )
                    / 100.0
                )
                rebalancing_weights[levy.short_name]["new_electricity_weight"] = 1.0 - (
                    rebalancing_weights[levy.short_name]["new_gas_weight"]
                )

            else:
                rebalancing_weights[levy.short_name]["new_tax_weight"] = 0.0
                rebalancing_weights[levy.short_name]["new_gas_weight"] = 1.0
                rebalancing_weights[levy.short_name]["new_electricity_weight"] = 1.0

            # Rebalancing weights: Unit costs vs standing charge

            # Check for electricity levy rebalancing
            if rebalancing_weights[levy.short_name]["new_electricity_weight"] != 0.0:
                # Set initial mode based on weights
                if (
                    rebalancing_weights[levy.short_name]["new_variable_weight_elec"]
                    == 1.0
                ):
                    elec_index = 0  # Variable weight mode
                elif (
                    rebalancing_weights[levy.short_name]["new_fixed_weight_elec"] != 0.0
                ):
                    elec_index = 1  # Fixed weight mode
                else:
                    # Default to either variable or fixed based on gas weight setting
                    elec_index = (
                        0
                        if rebalancing_weights[levy.short_name][
                            "new_variable_weight_gas"
                        ]
                        else 1
                    )

                # Display the radio button for levy mode on electricity
                elec_mode = st.radio(
                    "Mode of levy on electricity:",
                    ["Unit cost", "Standing charge"],
                    index=elec_index,
                    key=f"{levy.short_name} elec mode",
                )

                # Update weights based on the selected mode
                if elec_mode == "Unit cost":
                    rebalancing_weights[levy.short_name][
                        "new_variable_weight_elec"
                    ] = 1.0
                    rebalancing_weights[levy.short_name]["new_fixed_weight_elec"] = 0.0
                else:
                    rebalancing_weights[levy.short_name][
                        "new_variable_weight_elec"
                    ] = 0.0
                    rebalancing_weights[levy.short_name]["new_fixed_weight_elec"] = 1.0

            # Check for gas levy rebalancing
            if rebalancing_weights[levy.short_name]["new_gas_weight"] != 0.0:
                # Set initial mode based on weights
                if (
                    rebalancing_weights[levy.short_name]["new_variable_weight_gas"]
                    == 1.0
                ):
                    gas_index = 0  # Variable weight mode
                elif (
                    rebalancing_weights[levy.short_name]["new_fixed_weight_gas"] != 0.0
                ):
                    gas_index = 1  # Fixed weight mode
                else:
                    # Default to either variable or fixed based on gas weight setting
                    gas_index = (
                        0
                        if rebalancing_weights[levy.short_name][
                            "new_variable_weight_elec"
                        ]
                        else 1
                    )

                # Display the radio button for levy mode on gas
                gas_mode = st.radio(
                    "Mode of levy on gas:",
                    ["Unit cost", "Standing charge"],
                    index=gas_index,
                    key=f"{levy.short_name} gas mode",
                )

                # Update weights based on the selected mode
                if gas_mode == "Unit cost":
                    rebalancing_weights[levy.short_name][
                        "new_variable_weight_gas"
                    ] = 1.0
                    rebalancing_weights[levy.short_name]["new_fixed_weight_gas"] = 0.0
                else:
                    rebalancing_weights[levy.short_name][
                        "new_variable_weight_gas"
                    ] = 0.0
                    rebalancing_weights[levy.short_name]["new_fixed_weight_gas"] = 1.0

    else:
        rebalancing_weights = get_approach_weights(levies, approach)


# Rebalance levies based on chosen approach
rebalanced_levies = levies.rebalance_levies(
    rebalancing_weights,
    scenario_name="Rebalanced",
)

# Instantiate baseline tariffs
baseline_tariffs = instantiate_tariffs(payment_method="Other Payment")
baseline_electricity_tariff = update_electricity_tariff_policy_cost(
    baseline_tariffs["electricity"], levies
)
baseline_gas_tariff = update_gas_tariff_policy_cost(baseline_tariffs["gas"], levies)

# Instantiate rebalanced tariffs
rebalanced_tariffs = instantiate_tariffs(payment_method="Other Payment")
rebalanced_electricity_tariff = update_electricity_tariff_policy_cost(
    rebalanced_tariffs["electricity"], rebalanced_levies
)
rebalanced_gas_tariff = update_gas_tariff_policy_cost(
    rebalanced_tariffs["gas"], rebalanced_levies
)

# Create a list of Consumers (average Ofgem archetypes only, n=24) for baseline and rebalanced scenario
baseline_consumers = instantiate_archetype_consumers(
    baseline_gas_tariff, baseline_electricity_tariff
)
rebalanced_consumers = instantiate_archetype_consumers(
    rebalanced_gas_tariff, rebalanced_electricity_tariff
)

# Result: Unit cost ratio
baseline_ratio = calculate_unit_cost_ratio(
    baseline_electricity_tariff, baseline_gas_tariff
)
rebalanced_ratio = calculate_unit_cost_ratio(
    rebalanced_electricity_tariff, rebalanced_gas_tariff
)

# Result: Cost to taxpayers
cost_to_tax = sum(
    rebalancing_weights[levy.short_name]["new_tax_weight"] * levy.revenue
    for levy in rebalanced_levies
)

col1, col2, col3 = st.columns(3)
with col2:
    st.warning(
        f"**Electricity-to-gas ratio: {rebalanced_ratio:.2f}** *(Current: {baseline_ratio:.2f})*"
    )
with col3:
    st.error(
        f"**Additional cost to taxpayers: £{cost_to_tax/1_000_000_000:.2f} billion per year**"
    )


# Result: Distribution impacts dot chart
baseline_summary_table = tidy_to_pivot_summary(
    get_tidy_summary(baseline_consumers, "Baseline")
)
rebalanced_summary_table = tidy_to_pivot_summary(
    get_tidy_summary(rebalanced_consumers, "Rebalanced")
)
# Add bill change column
rebalanced_summary_table["bill_change"] = (
    rebalanced_summary_table["combined_fuel_bill"]
    - baseline_summary_table["combined_fuel_bill"]
)

# Add archetype sizes

archetype_sizes = data.ofgem_archetypes_data()[
    ["AnnualConsumptionProfile", "ArchetypeSize"]
]
archetype_sizes = archetype_sizes.rename(
    columns={
        "AnnualConsumptionProfile": "Name",
    }
)
rebalanced_summary_table = rebalanced_summary_table.merge(
    archetype_sizes, on="Name", how="left"
)

st.markdown(
    f"<p style='color:black; font-size: 20px;'><b>Distributional impacts: Effect on energy bills</b></p>",
    unsafe_allow_html=True,
)

chart = make_archetype_bill_change_chart(rebalanced_summary_table, chart_width=1000)
st.altair_chart(chart)

# Option to view results table
if st.button("View distributional impacts results table"):
    # Show link to distributional effects summary dataframe for download
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(rebalanced_summary_table)

    st.download_button(
        "Download table",
        csv,
        "rebalanced_scenario_distributional_effect.csv",
        "text/csv",
        key="download-csv",
    )

    st.write(rebalanced_summary_table)
