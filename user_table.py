import streamlit as st
import pandas as pd

# Function to initialize or load user data
@st.cache_resource()
def initialize_data():
    return []

# Function to add or update a row in the table
def add_or_update_data(data, new_data):
    updated = False
    for i, row in enumerate(data):
        if row["Name"] == new_data["Name"]:
            data[i] = new_data
            updated = True
            break
    if not updated:
        data.append(new_data)

# Function to delete a row by name
def delete_data(data, name_to_delete):
    data[:] = [row for row in data if row["Name"] != name_to_delete]

# Main Streamlit app
def main():
    st.title("Editable Table Example")

    user_data = initialize_data()

    # Add or update data

    name = st.text_input("Name")
    age = st.number_input("Age")
    country = st.selectbox("Country", ["USA", "Canada", "India"])
    new_data = {"Name": name, "Age": age, "Country": country}


    if st.button("Add/Update Data"):
        add_or_update_data(user_data, new_data)

    # Display the table
        for row in user_data:
            row["Delete"] = st.button("Delete {}".format(row['Name']))
        #df.append(user_data)
        # Show "Delete" button for each row
        for row in user_data:
            if row["Delete"]:
                delete_data(user_data, row["Name"])

        #st.table(df)
        for row in user_data:
            st.write(f"{row['Name']} | {row['Age']} | {row['Country']}")


if __name__ == "__main__":
    main()