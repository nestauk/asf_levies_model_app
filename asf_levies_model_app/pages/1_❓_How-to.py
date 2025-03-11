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
    "This tool allows you to **test different levy reform scenarios** and shows you the effect on "
    "(i) the **relative cost of electricity to gas** and (ii) **changes in energy bills** of different types of households in Great Britain."
)
st.markdown(
    "This tool is powered by our analytical [**Python model**](https://github.com/nestauk/asf_levies_model),"
    " developed as part of our project on [**making energy cheaper by rebalancing levies**]"
    "(https://www.nesta.org.uk/project/finding-ways-to-deliver-cheaper-electricity-by-rebalancing-levies/)."
)
st.markdown(
    "*Read more about how we developed the model and app.* (to add link to Medium blog)"
)


st.subheader("How do I use this tool?")
st.markdown(
    """
On the **🎯Run a rebalancing scenario** page, you can test a levy reform scenario by adjusting the settings in the **sidebar**.
"""
)
st.markdown(
    """ To test a levy reform scenario, you can do one of:

- **Choose a preset approach.**<br>
   *When you first open the page, it defaults to the current situation.*


- **Create your own approach by manually adjusting the configuration for each levy.**<br>
   *When you first select this option, all the settings are set to the current situation.*<br><br>
   **For each levy**, you can choose:
   - Continue to **levy on electricity and/or gas bills**, or remove off energy bills entirely and **fund through public spending**.
   - If levying on bills, you can then choose what **percentage** of the scheme amount **to raise from electricity vs. gas** bills.
   - You can also choose to **change** the levy from a **unit cost** (£/MWh) or **standing charge** (£/customer).
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
    As you change the settings, you will see their effects on the [**electricity to gas unit cost ratio**](https://www.nesta.org.uk/blog/the-electricity-to-gas-price-ratio-explained-how-a-green-ratio-would-make-bills-cheaper-and-greener/)
    and the energy bills of different [**UK energy consumer archetypes**](https://www.ofgem.gov.uk/energy-policy-and-regulation/measuring-impact-our-policy-decisions).
"""
)
st.markdown(
    "You also have the option to **view, and download**, the **underlying results data** table for the bill changes across archetypes."
)


st.subheader("Why did we build this tool?")
st.markdown(
    """
At Nesta, we're on a mission to **decarbonise home heating**. Residential buildings are a major source of UK carbon emissions because of their reliance on fossil fuels for heat.
Our team in A Sustainable Future focuses on facilitating adoption of **low-carbon heating systems to cut these emissions**.<br>

With **electricity costing nearly four times more than gas** (as of March 2025), switching from gas boilers to low-carbon technologies such as electric heat pumps is not financially appealing for many households.
One way to **make electricity more affordable** is to **adjust the levies** that are added to energy bills which fund environmental and social policy schemes.
Currently, most of these levies are added to electricity bills.<br>

We believe that **shifting levies from electricity to gas** is essential to enabling a **nationwide heating transition** away from gas and for **sustainably
lowering energy bills**.<br>
""",
    unsafe_allow_html=True,
)
