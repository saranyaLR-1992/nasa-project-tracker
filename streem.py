import streamlit as st
import pandas as pd
import pymysql
from streamlit_option_menu import option_menu

# Establish database connection
connection = pymysql.connect(
    host='127.0.0.1',
    user='saranyaLR',
    password='saranyaLR',
    database='nasa'
)
cursor = connection.cursor()

# App config
st.set_page_config(page_title="NASA Asteroid Tracker", layout="wide")
st.title("🚀 NASA Asteroid Tracker")

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Asteroids Approaches",
        options=["Filters", "Queries"]
    )

# Helper function
def execute_and_display(query):
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error executing query: {e}")

# Filters section
if selected == "Filters":
    st.write("### Filter Asteroid Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        magnitude = st.slider("Absolute Magnitude (H)", 0.0, 35.0, 25.0)
        min_dia = st.slider("Estimated Diameter Min (km)", 0.0, 5.0, 0.1)
        velocity = st.slider("Relative Velocity (km/h)", 0.0, 200000.0, 10000.0)
    with col2:
        hazardous = st.selectbox("Only show potentially hazardous?", ["All", "Yes", "No"])
        max_dia = st.slider("Estimated Diameter Max (km)", 0.0, 5.0, 1.0)
        miss_distance_km = st.slider("Miss Distance (km)", 0.0, 50000000.0, 10000000.0)
    with col3:
        start_date = st.date_input("Start Date", pd.to_datetime("2024-01-01"))
        end_date = st.date_input("End Date", pd.to_datetime("2025-04-13"))

    dataset = st.selectbox("Choose a dataset", ["Asteroids Details", "Close Approach1"])

    if st.button("Run Filters"):
        if dataset == "Asteroids Details":
            query = f"""
                SELECT * FROM asteroids_details
                WHERE absolute_magnitude_h <= {magnitude}
                AND estimated_diameter_min_km >= {min_dia}
                AND estimated_diameter_max_km <= {max_dia}
            """
            if hazardous == "Yes":
                query += " AND is_potentially_hazardous_asteroids = 1"
            elif hazardous == "No":
                query += " AND is_potentially_hazardous_asteroids = 0"
        else:
            query = f"""
                SELECT * FROM close_approach1
                WHERE relative_velocity_kmph >= {velocity}
                AND miss_distance_km <= {miss_distance_km}
                AND close_approach_data BETWEEN '{start_date}' AND '{end_date}'
            """
        execute_and_display(query)

# Queries section
elif selected == "Queries":
    query_text = st.selectbox("Select SQL query", [
        "1. Count how many times each asteroid has approached Earth",
        "2. Average velocity of each asteroid over multiple approaches",
        "3. List top 10 fastest asteroids",
        "4. Find potentially hazardous asteroids that have approached Earth more than 3 times",
        "5. Find the month with the most asteroid approaches",
        "6. Get the asteroid with the fastest ever approach speed",
        "7. Sort asteroids by maximum estimated diameter (descending)",
        "8. Asteroids whose closest approach is getting nearer over time",
        "9. Display the name of each asteroid along with the date and miss distance of its closest approach to Earth",
        "10. List names of asteroids that approached Earth with velocity > 50,000 km/h",
        "11. Count how many approaches happened per month",
        "12. Find asteroid with the highest brightness (lowest magnitude value)",  
        "13. Get number of hazardous vs non-hazardous asteroids",
        "14. Find asteroids that passed closer than the Moon (less than 1 LD), along with their close approach date and distance",
        "15. Find asteroids that came within 0.05 AU (astronomical unit)",
        "16. Sort asteroids by minimum estimated diameter (ascending)",
        "17. Get top 5 closest approaches",
        "18. Find asteroids with a miss distance < 5,000,000 km",
        "19. List asteroids sorted by name alphabetically",
        "20. Group asteroids by year of close approach"
    ])

    if st.button("Run Query"):
        if query_text.startswith("1."):
            sql = """SELECT neo_reference_id, COUNT(*) AS approach_count
                     FROM close_approach1
                     WHERE orbiting_body='Earth'
                     GROUP BY neo_reference_id
                     ORDER BY approach_count DESC"""
        elif query_text.startswith("2."):
            sql = """SELECT neo_reference_id, AVG(relative_velocity_kmph) AS avg_velocity_kmph
                     FROM close_approach1
                     WHERE orbiting_body='Earth'
                     GROUP BY neo_reference_id
                     ORDER BY avg_velocity_kmph DESC"""
        elif query_text.startswith("3."):
            sql = """SELECT neo_reference_id, relative_velocity_kmph
                     FROM close_approach1
                     WHERE orbiting_body='Earth'
                     ORDER BY relative_velocity_kmph DESC
                     LIMIT 10"""
        elif query_text.startswith("20."):
            sql = """SELECT YEAR(close_approach_data) AS approach_year, COUNT(*) AS total_approaches
                     FROM close_approach1
                     GROUP BY YEAR(close_approach_data)
                     ORDER BY approach_year"""
        else:
            st.warning("This query is not implemented yet.")
            sql = None

        if sql:
            execute_and_display(sql)
