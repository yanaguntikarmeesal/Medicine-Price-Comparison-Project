

import streamlit as st
import serpapi
import pandas as pd
import matplotlib.pyplot as plt
import re


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    layout="centered",
    page_title="Price Compare",
    page_icon="🔎",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# SERPAPI SEARCH FUNCTION
# ---------------------------------------------------------
def compare(name):
    params = {
        "engine": "google_shopping",
        "q": name,
        "api_key": "705ebaf1fd028041438ab33b03274174c27508e21b3f8bba98770014ef1fcc9e",
        "gl": "in"
    }

    search = serpapi.GoogleSearch(params)
    results = search.get_dict()

    return results.get("shopping_results", [])


# ---------------------------------------------------------
# PRICE CONVERSION FUNCTION
# ---------------------------------------------------------
def get_price(price):
    """
    Convert prices such as:
    ₹49
    ₹1,299
    $99.99

    into float values.
    """

    if not price:
        return None

    # Keep only numbers and decimal point
    price_clean = re.sub(r"[^\d.]", "", str(price))

    try:
        return float(price_clean)
    except ValueError:
        return None


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
col1, col2 = st.columns(2)

try:
    col1.image("e_pharmacy.png", width=200)
except:
    col1.write("💊")

col2.header("E-Pharmacy Price Comparison System")


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("Enter Name of Medicine")

medicine_name = st.sidebar.text_input(
    "Enter Medicine Name 👇"
)

number = st.sidebar.number_input(
    "Enter Number of Options 👇",
    min_value=1,
    max_value=20,
    value=5,
    step=1
)


# ---------------------------------------------------------
# SEARCH BUTTON
# ---------------------------------------------------------
if st.sidebar.button("Show Comparison"):

    if not medicine_name.strip():
        st.warning("Please enter a medicine name.")

    else:

        with st.spinner("Searching for medicine prices..."):

            try:
                shopping_results = compare(medicine_name)

            except Exception as e:
                st.error("Unable to connect to SerpApi.")
                st.error(f"Error: {e}")
                st.stop()


        # -------------------------------------------------
        # CHECK RESULTS
        # -------------------------------------------------
        if not shopping_results:

            st.error(
                "No shopping results found. "
                "Try another medicine name."
            )
            st.stop()


        # Only use the number of results that actually exist
        total_options = min(
            int(number),
            len(shopping_results)
        )


        # -------------------------------------------------
        # DATA LISTS
        # -------------------------------------------------
        medicine_names = []
        medicine_prices = []
        companies = []


        # -------------------------------------------------
        # DISPLAY OPTIONS
        # -------------------------------------------------
        st.header("💊 Medicine Price Comparison")

        for i in range(total_options):

            item = shopping_results[i]

            title = item.get(
                "title",
                "Medicine name not available"
            )

            source = item.get(
                "source",
                "Company not available"
            )

            price_text = item.get(
                "price",
                "Price not available"
            )

            link = item.get(
                "link",
                ""
            )

            price_value = get_price(price_text)


            # ---------------------------------------------
            # OPTION TITLE
            # ---------------------------------------------
            st.subheader(f"Option {i + 1}")


            c1, c2 = st.columns(2)

            c1.write("**Company**")
            c2.write(source)

            c1.write("**Medicine Name**")
            c2.write(title[:60])

            c1.write("**Price**")
            c2.write(price_text)


            # ---------------------------------------------
            # BUY LINK
            # ---------------------------------------------
            c1.write("**Buy Link**")

            if link:
                c2.markdown(
                    f"[🛒 Buy Now]({link})"
                )
            else:
                c2.write("Link not available")


            # ---------------------------------------------
            # SAVE DATA FOR CHART
            # ---------------------------------------------
            if price_value is not None:

                medicine_names.append(source)
                medicine_prices.append(price_value)
                companies.append(title[:30])


            st.divider()


        # -------------------------------------------------
        # CHECK PRICE DATA
        # -------------------------------------------------
        if not medicine_prices:

            st.warning(
                "Prices could not be extracted from the "
                "shopping results."
            )
            st.stop()


        # -------------------------------------------------
        # FIND LOWEST PRICE
        # -------------------------------------------------
        lowest_price_index = medicine_prices.index(
            min(medicine_prices)
        )

        best_price = medicine_prices[lowest_price_index]
        best_company = medicine_names[lowest_price_index]


        # -------------------------------------------------
        # BEST OPTION
        # -------------------------------------------------
        st.header("🏆 Best Option")

        c1, c2 = st.columns(2)

        c1.write("**Company**")
        c2.write(best_company)

        c1.write("**Price**")
        c2.write(f"₹{best_price:,.2f}")


        # Find original shopping result
        best_result = None

        for item in shopping_results[:total_options]:

            source = item.get("source", "")

            price_value = get_price(
                item.get("price")
            )

            if (
                source == best_company
                and price_value == best_price
            ):
                best_result = item
                break


        if best_result:

            best_link = best_result.get("link", "")

            c1.write("**Buy Link**")

            if best_link:
                c2.markdown(
                    f"[🛒 Buy at Best Price]({best_link})"
                )


        # -------------------------------------------------
        # BAR CHART
        # -------------------------------------------------
        st.header("📊 Price Comparison Chart")

        chart_df = pd.DataFrame({
            "Company": medicine_names,
            "Price": medicine_prices
        })

        chart_df = chart_df.set_index("Company")

        st.bar_chart(chart_df)


        # -------------------------------------------------
        # PIE CHART
        # -------------------------------------------------
        st.header("🥧 Price Distribution")

        fig, ax = plt.subplots()

        ax.pie(
            medicine_prices,
            labels=medicine_names,
            autopct="%1.1f%%",
            shadow=True,
            startangle=90
        )

        ax.axis("equal")

        st.pyplot(fig)


        # -------------------------------------------------
        # DATA TABLE
        # -------------------------------------------------
        st.header("📋 Price Details")

        display_df = pd.DataFrame({
            "Company": medicine_names,
            "Price": medicine_prices
        })

        st.dataframe(
            display_df,
            use_container_width=True
        )

# 

# 1. Install the required packages
# python -m pip install streamlit google-search-results pandas matplotlib

# 3. Run the application
# python -m streamlit run pro.py