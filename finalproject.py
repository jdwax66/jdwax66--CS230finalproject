import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# [ST4] Custom page design and sidebar
st.set_page_config(page_title="Skyscraper Insights", layout="wide", initial_sidebar_state="expanded")

# [PY3] Load dataset (with try/except)
try:
    df = pd.read_csv('skyscrapers.csv')
except FileNotFoundError:
    print("File not found.")

# [DA1] Filter out buildings with height = 0 or no city value
df = df[(df['statistics.height'] > 0) & (df['location.city'].notna())]

# Convert city to string to avoid Streamlit errors
df['location.city'] = df['location.city'].astype(str)

# Renamed coordinate columns to ensure Streamlit map works correctly
df = df.rename(columns={'location.latitude': 'latitude', 'location.longitude': 'longitude'})

# [PY2] Function to get 5 tallest skyscrapers in selected city
def get_tallest_skyscrapers(city, top_n=5):
    if city == 'ALL CITIES':  # [DA3] find top 5 tallest skyscrapers in a given city
        city_df = df.head(top_n)
    else:
        city_df = df[df['location.city'] == city].head(top_n)
    skyscraper_count = len(city_df)
    return city_df, skyscraper_count

# [DA2] Sort by height (tallest to shortest)
df = df.sort_values(by='statistics.height', ascending=False)

# [DA4] Filter to only include completed skyscrapers
completed_df = df[df['status.completed.is completed'] == True]

# Replace buildings with completion year=0 with "Unknown" (if height!=0)
completed_df['status.completed.year'] = completed_df['status.completed.year'].replace(0, "Unknown")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Completed Skyscrapers", "Tallest Skyscrapers", "Map of Skyscrapers"])

# [PY4] List comprehension to create a sorted list of unique city names for display
city_options = ['ALL CITIES'] + sorted({city for city in df['location.city']})

default_index = city_options.index('Chicago') if 'Chicago' in city_options else 0

# [ST1] Dropdown menu for cities (on sidebar)
city = st.sidebar.selectbox("Select a City", city_options, index=default_index)

# [ST2] Text box in the sidebar to input skyscraper name and find which city it's located in
skyscraper_name_input = st.sidebar.text_input("Enter a skyscraper name:")
standardized_name = skyscraper_name_input.strip().lower()

# See if inputted skyscraper name is in the dataset
if standardized_name:
    matching_skyscrapers = df[df['name'].str.lower() == standardized_name]
    if not matching_skyscrapers.empty:
        city_of_skyscraper = matching_skyscrapers.iloc[0]['location.city']
        st.sidebar.write(f"The skyscraper '{skyscraper_name_input}' is located in {city_of_skyscraper}.")
    else:
        st.sidebar.write(f"Sorry, no skyscraper named '{skyscraper_name_input}' found.")
else:  # When input is blank
    st.sidebar.write("Enter a skyscraper name to find its city.")


# PAGE ONE
if page == "Completed Skyscrapers":
    st.title(f"Completed Skyscrapers in {city}" if city != "ALL CITIES" else "Completed Skyscrapers")

    # Hyperlink
    st.markdown("[Click here to view the bar chart](#bar-chart)")

    # Filter data based on selected city
    if city == "ALL CITIES":
        filtered_df = completed_df
    else:
        filtered_df = completed_df[completed_df['location.city'] == city]

    # Rename column headers
    display_df = filtered_df[['name', 'statistics.height', 'status.completed.year']].rename(
        columns={'name': 'Name',
                 'statistics.height': 'Height',
                 'status.completed.year': 'Completion Year'
                 })

    # [DA1] Use lambda function to round height to 2 decimal places & remove trailing 0's
    display_df['Height'] = display_df['Height'].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    # Reset index column (to not show original row numbers)
    display_df.reset_index(drop=True, inplace=True)

    # [VIZ1] Table of skyscraper names, heights, and completion years for selected city
    st.table(display_df)

    # [VIZ2] Bar chart for average skyscraper height by completion year
    st.markdown('<a id="bar-chart"></a>', unsafe_allow_html=True)  # Hyperlink destination
    avg_height = filtered_df.groupby('status.completed.year')['statistics.height'].mean()
    fig, ax = plt.subplots()
    avg_height.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title(f"Average Skyscraper Height by Completion Year in {city if city != 'ALL CITIES' else 'All Cities'}")
    ax.set_xlabel('Completion Year')
    ax.set_ylabel('Average Height (m)')
    ax.set_xticks(range(0, len(avg_height), 25))  # Only label every 25 years
    st.pyplot(fig)

# PAGE TWO
elif page == "Tallest Skyscrapers":
    st.title(f"Tallest Skyscrapers in {city}" if city != "ALL CITIES" else "Tallest Skyscrapers")
    st.subheader("Top 5 Tallest Skyscrapers")

    # [PY1] First call to get_tallest_skyscrapers with default top_n=5
    top_skyscrapers_default, skyscraper_count_default = get_tallest_skyscrapers(city)
    st.write(f"Top {skyscraper_count_default} skyscrapers in {city}:")

    top_skyscrapers_default['status.completed.year'] = top_skyscrapers_default['status.completed.year'].replace(0, "Unknown")

    # Rename column headers
    display_top_skyscrapers = top_skyscrapers_default[['name', 'statistics.height', 'status.completed.year']].rename(
        columns={
            'name': 'Name',
            'statistics.height': 'Height',
            'status.completed.year': 'Completion Year'
        })

    # [DA1] Use lambda function to round height to 2 decimal places & remove trailing 0's
    display_top_skyscrapers['Height'] = display_top_skyscrapers['Height'].apply(
        lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    # Reset index column (to not show original row numbers)
    display_top_skyscrapers.reset_index(drop=True, inplace=True)

    # Table of top 5 tallest skyscraper names, heights, and completion years for selected city
    st.table(display_top_skyscrapers)

    # [VIZ3] Horizontal bar chart for tallest skyscrapers
    fig2, ax2 = plt.subplots()
    ax2.barh(top_skyscrapers_default['name'], top_skyscrapers_default['statistics.height'], color='lightcoral')
    ax2.set_title(
        f"Top {len(top_skyscrapers_default)} Tallest Skyscrapers in {city if city != 'ALL CITIES' else 'All Cities'}")
    ax2.set_xlabel('Height (m)')
    ax2.set_ylabel('Building Name')
    st.pyplot(fig2)


    # [PY1] Second call to get_tallest_skyscrapers with a non-default top_n=20
    st.subheader("Top 20 Tallest Skyscrapers")
    top_20_skyscrapers, skyscraper_count_20 = get_tallest_skyscrapers(city, top_n=20)
    st.write(f"Top {skyscraper_count_default} skyscrapers in {city}:")

    top_20_skyscrapers['status.completed.year'] = top_20_skyscrapers['status.completed.year'].replace(0, "Unknown")

    # Rename column headers
    display_top_20_skyscrapers = top_20_skyscrapers[['name', 'statistics.height', 'status.completed.year']].rename(
        columns={
            'name': 'Name',
            'statistics.height': 'Height',
            'status.completed.year': 'Completion Year'
        })

    # [DA1] Use lambda function to round height to 2 decimal places & remove trailing 0's
    display_top_20_skyscrapers['Height'] = display_top_20_skyscrapers['Height'].apply(
        lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    # Reset index column (to not show original row numbers)
    display_top_20_skyscrapers.reset_index(drop=True, inplace=True)

    # Table of top 20 tallest skyscraper names, heights, and completion years for selected city
    st.table(display_top_20_skyscrapers)

    # [VIZ4] Horizontal bar chart for top 3 tallest skyscrapers
    fig3, ax3 = plt.subplots()
    ax3.barh(top_20_skyscrapers['name'], top_20_skyscrapers['statistics.height'], color='lightgreen')
    ax3.set_title(f"Top 20 Tallest Skyscrapers in {city if city != 'ALL CITIES' else 'All Cities'}")
    ax3.set_xlabel('Height (m)')
    ax3.set_ylabel('Building Name')
    st.pyplot(fig3)

# PAGE THREE
elif page == "Map of Skyscrapers":
    st.title(f"Map of Skyscrapers in {city}" if city != "ALL CITIES" else "Map of Skyscrapers")

    # [ST3] Slider to filter skyscrapers by height with default range (300-600)
    height_range = st.slider("Select Height Range (meters)", 0, 2000, (300, 600), 100)

    # [DA5] Filter data based on city and height range for map
    if city == "ALL CITIES":
        map_filtered_df = df[(df['statistics.height'] >= height_range[0]) &
                             (df['statistics.height'] <= height_range[1])]
    else:
        map_filtered_df = df[(df['location.city'] == city) &
                             (df['statistics.height'] >= height_range[0]) &
                             (df['statistics.height'] <= height_range[1])]

    # [MAP] Map of skyscrapers for selected height range and city
    st.write(f"Displaying skyscrapers in {city if city != 'ALL CITIES' else 'all cities'} within selected height range.")
    st.map(map_filtered_df[['latitude', 'longitude']])
