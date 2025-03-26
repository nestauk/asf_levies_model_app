import streamlit as st

st.set_page_config(
    page_title="Nesta Levies Rebalancing Model", page_icon="🏠", layout="wide"
)

st.title("Levies Rebalancing App💡")
st.markdown(
    "**from the [A Sustainable Future](https://www.nesta.org.uk/sustainable-future/) team at Nesta**"
)


st.subheader("What is this tool?")
st.markdown(
    """
            This tool allows you to **test different levy reform scenarios** and shows you the effect on (i) the **relative cost of electricity to gas** and (ii) **changes in energy bills** of different types of households in Great Britain.
"""
)
st.markdown(
    "This tool is powered by our analytical [**Python model**](https://github.com/nestauk/asf_levies_model),"
    " developed as part of our project on [**making energy cheaper by rebalancing levies**]"
    "(https://www.nesta.org.uk/project/finding-ways-to-deliver-cheaper-electricity-by-rebalancing-levies/)."
)
st.markdown(
    "*Read more about how we developed the model and app.* (to add link to Medium blog)"
)

st.markdown("---")

st.subheader("How do I use this tool?")

st.markdown(
    """
On the **🎯 Run a rebalancing scenario** page, you can test a levy reform scenario by adjusting the settings in the **sidebar**.
(Learn more about the [schemes](https://www.ofgem.gov.uk/environmental-and-social-schemes) that each levy funds.)

#### **Option A. Choose a preset approach**
   The default setting is the current situation, but you can choose from different preset approaches.

#### **Option B. Create your own approach**
   Manually adjust the configuration for each levy. The settings will initially be set to the current situation.

For each levy, you can choose to:
- **Continue levying on electricity and/or gas bills**, or
- **Remove the levy from bills** and fund it through public spending.

If continuing to levy on bills:
- Choose what **percentage** of the levy amount to raise from **electricity vs. gas** bills.
- Choose the levy type: **Unit cost** (£/MWh) or **Standing charge** (£/customer).

##### As you make changes, you'll see:
- The **electricity to gas unit cost ratio**
  (Learn more: [Electricity to gas price ratio](https://www.nesta.org.uk/blog/the-electricity-to-gas-price-ratio-explained-how-a-green-ratio-would-make-bills-cheaper-and-greener/)).

- The **total cost** removed off bills **to be funded by general taxation**

- The **typical household bill**, using the [medium energy use](https://www.ofgem.gov.uk/information-consumers/energy-advice-households/average-gas-and-electricity-use-explained) values used for Ofgem's energy price cap

- The **change to energy bills** for different **UK energy consumer archetypes**
  (Learn more: [Ofgem archetypes](https://www.ofgem.gov.uk/energy-policy-and-regulation/measuring-impact-our-policy-decisions)).

##### Additional Features:
- **View and download** the **underlying results data** table for bill changes across archetypes.
"""
)

st.markdown("---")

st.subheader("Why did we build this tool?")
st.markdown(
    """
At Nesta, our mission is to **decarbonise home heating**. Residential buildings are a major source of UK carbon emissions due to their reliance on fossil fuels for heat. In the A Sustainable Future team, we're working to facilitate the adoption of **low-carbon heating systems** to reduce these emissions.

With **electricity nearly four times more expensive than gas** (as of March 2025), switching from gas boilers to electric heat pumps is financially challenging for many households. One way to **make electricity more affordable** is to **adjust the levies** that fund environmental and social policy schemes. Currently, most of these levies are added to electricity bills.

We believe that **shifting levies from electricity to gas** is key to enabling a nationwide **transition to low-carbon heating** while **sustainably lowering energy bills**.
"""
)
