import copy
import os
import tempfile

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib import fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate
from reportlab.lib.pagesizes import portrait, A4
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib import colors
import base64

import database

# ---------------------------------------------------------------------------
# Page config – must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Invoice Maker",
    page_icon="🧾",
    layout="centered",   # "centered" works best on mobile screens
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Bootstrap the database once per process
# ---------------------------------------------------------------------------
database.init_db()

# ---------------------------------------------------------------------------
# Auth gate – requires Streamlit >= 1.41 with Google configured in secrets.toml
# ---------------------------------------------------------------------------
if not st.user.is_logged_in:
    st.markdown(
        """
        <div style='text-align:center; padding: 3rem 1rem;'>
            <h1>🧾 Invoice Maker</h1>
            <p style='font-size:1.1rem; color:#555;'>
                Sign in with your Google account to start creating invoices.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign in with Google", use_container_width=True, type="primary"):
            st.login("google")
    st.stop()

# ---------------------------------------------------------------------------
# User is authenticated from here on
# ---------------------------------------------------------------------------
user_email: str = st.user.email
user_name: str = st.user.name or user_email
user_picture: str = st.user.picture or ""

# Persist user record so we can associate data with them
database.upsert_user(user_email, user_name, user_picture)

# ---------------------------------------------------------------------------
# Per-user session state keys
# ---------------------------------------------------------------------------
USER_DATA_KEY = f"user_data_{user_email}"
if USER_DATA_KEY not in st.session_state:
    st.session_state[USER_DATA_KEY] = []


def get_user_data() -> list:
    return st.session_state[USER_DATA_KEY]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
current_date = datetime.now()
order_date = current_date.strftime("%d/%m/%Y")

default_store_details = {
    "from": {
        "store_name": "",
        "store_address": "",
        "email_id": user_email,
        "phone_number": "",
        "tin_no": "",
        "cst_no": "",
        "gst_no": "",
    },
    "to": {
        "store_name": "",
        "store_address": "",
        "email_id": "",
        "phone_number": "",
        "tin_no": "",
        "cst_no": "",
        "gst_no": "",
    },
    "order_num": "",
    "order_date": order_date,
    "cgst rate": 9,
    "sgst rate": 9,
}


def add_thousand_separator(number_str):
    try:
        number = int(number_str)
        s = str(abs(number))
        if len(s) <= 3:
            return s
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        return result
    except ValueError:
        return "Invalid Input"


def generate_pdf(invoice_data):
    # Write PDF to a temp file so multiple concurrent users don't collide
    pdf_filename = (
        invoice_data["order_num"]
        + "__"
        + str(invoice_data["order_date"]).replace("/", "-")
        + ".pdf"
    )
    tmp_path = os.path.join(tempfile.gettempdir(), f"{user_email}_{pdf_filename}")

    doc = SimpleDocTemplate(tmp_path, pagesize=portrait(A4))
    doc.leftMargin = 10
    doc.rightMargin = 10
    elements = []

    styles = getSampleStyleSheet()
    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    title = Paragraph("Tax Invoice", styles["Title"])
    elements.append(title)

    elements.append(Spacer(1, 12))

    text = """

         Order Number: {:70}     Order Date: {:20}

        """.format(
        invoice_data["order_num"], invoice_data["order_date"]
    )

    font_path = "./Consolas.ttf"
    pdfmetrics.registerFont(TTFont("Consolas", font_path))

    custom_style = ParagraphStyle(name="ConsolasStyle", fontName="Consolas", fontSize=8)

    paragraph1 = Preformatted(text, style=custom_style)
    elements.append(paragraph1)
    elements.append(Spacer(1, 12))

    if (len(invoice_data["from"]["store_address"]) <= 30) and (
        len(invoice_data["to"]["store_address"]) <= 30
    ):
        text = """
        --------------------------------------------------------------------------------------------------------------------
                   From                                                                     To
        --------------------------------------------------------------------------------------------------------------------
        Store Name    : {:<20}                                   Store Name   : {:<20}
        Store Address : {:<30}                                   Store Address: {:<30}
        Email id      : {:<30}                                   Email id     : {:<30}
        Phone Number  : {:<20}                                   Phone Number : {:<20}
        TIN number    : {:<20}                                   TIN number   : {:<20}
        CST number    : {:<20}                                   CST number   : {:<20}
        GST number    : {:<20}                                   GST number   : {:<20}
            """.format(
            invoice_data["from"]["store_name"],
            invoice_data["to"]["store_name"],
            invoice_data["from"]["store_address"],
            invoice_data["to"]["store_address"],
            invoice_data["from"]["email_id"],
            invoice_data["to"]["email_id"],
            invoice_data["from"]["phone_number"],
            invoice_data["to"]["phone_number"],
            invoice_data["from"]["tin_no"],
            invoice_data["to"]["tin_no"],
            invoice_data["from"]["cst_no"],
            invoice_data["to"]["cst_no"],
            invoice_data["from"]["gst_no"],
            invoice_data["to"]["gst_no"],
        )
    else:
        text = """
        --------------------------------------------------------------------------------------------------------------------
                   From                                                    To
        --------------------------------------------------------------------------------------------------------------------
        Store Name    : {:<30}        Store Name   : {:<30}
        Store Address : {:<30}        Store Address: {:<30}
                        {:<30}                       {:<30}
        Email id      : {:<30}        Email id     : {:<30}
        Phone Number  : {:<30}        Phone Number : {:<30}
        TIN number    : {:<30}        TIN number   : {:<30}
        CST number    : {:<30}        CST number   : {:<30}
        GST number    : {:<30}        GST number   : {:<30}
            """.format(
            str(invoice_data["from"]["store_name"]),
            invoice_data["to"]["store_name"],
            ",".join(invoice_data["from"]["store_address"].split(",")[:-2]).strip(),
            ",".join(invoice_data["to"]["store_address"].split(",")[:-2]).strip(),
            ",".join(invoice_data["from"]["store_address"].split(",")[-2:]).strip(),
            ",".join(invoice_data["to"]["store_address"].split(",")[-2:]).strip(),
            invoice_data["from"]["email_id"],
            invoice_data["to"]["email_id"],
            invoice_data["from"]["phone_number"],
            invoice_data["to"]["phone_number"],
            invoice_data["from"]["tin_no"],
            invoice_data["to"]["tin_no"],
            invoice_data["from"]["cst_no"],
            invoice_data["to"]["cst_no"],
            invoice_data["from"]["gst_no"],
            invoice_data["to"]["gst_no"],
        )

    paragraph2 = Preformatted(text, style=custom_style)
    elements.append(paragraph2)
    elements.append(Spacer(1, 12))

    text = """
        --------------------------------------------------------------------------------------------------------------------
    """
    elements.append(Preformatted(text, style=custom_style))
    elements.append(Spacer(1, 24))

    text = """
        List of Items:
        """
    elements.append(Preformatted(text, style=custom_style))
    elements.append(Spacer(1, 12))

    data = invoice_data["user_data"]
    table_data = [["item", "description", "Qty", "Units", "UnitPrice", "Amount(Rs)"]]
    item_number = 1
    amt_before_tax = 0
    for item in data:
        table_data.append(
            [
                item_number,
                item["description"],
                item["Qty"],
                item["Units"],
                add_thousand_separator(str(item["UnitPrice"])),
                add_thousand_separator(str(item["Amount"])),
            ]
        )
        item_number += 1
        amt_before_tax += item["Amount"]

    table_data.append(
        ["Total Amount Before Tax", "", "", "", "", add_thousand_separator(str(amt_before_tax))]
    )
    cgst = round((invoice_data["cgst_rate"] / 100) * amt_before_tax)
    sgst = round((invoice_data["sgst_rate"] / 100) * amt_before_tax)
    grand_total = round(amt_before_tax + cgst + sgst)

    table_data.append(["CGST", "", "", "", "", add_thousand_separator(str(cgst))])
    table_data.append(["SGST", "", "", "", "", add_thousand_separator(str(sgst))])
    table_data.append(["Grand Total", "", "", "", "", add_thousand_separator(str(grand_total))])

    table = Table(table_data, colWidths=[40, 230, 50, 50, 70, 90])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Consolas"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("SPAN", (0, -1), (-2, -1)),
                ("BACKGROUND", (0, -1), (-2, -1), colors.grey),
                ("TEXTCOLOR", (0, -1), (-2, -1), colors.whitesmoke),
                ("ALIGN", (0, -1), (-2, -1), "RIGHT"),
                ("SPAN", (0, -2), (-2, -2)),
                ("BACKGROUND", (0, -2), (-2, -2), colors.grey),
                ("TEXTCOLOR", (0, -2), (-2, -2), colors.whitesmoke),
                ("ALIGN", (0, -2), (-2, -2), "RIGHT"),
                ("SPAN", (0, -3), (-2, -3)),
                ("BACKGROUND", (0, -3), (-2, -3), colors.grey),
                ("TEXTCOLOR", (0, -3), (-2, -3), colors.whitesmoke),
                ("ALIGN", (0, -3), (-2, -3), "RIGHT"),
                ("SPAN", (0, -4), (-2, -4)),
                ("BACKGROUND", (0, -4), (-2, -4), colors.grey),
                ("TEXTCOLOR", (0, -4), (-2, -4), colors.whitesmoke),
                ("ALIGN", (0, -4), (-2, -4), "RIGHT"),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)
    return tmp_path, pdf_filename


# ---------------------------------------------------------------------------
# Functions that mutate per-user item list
# ---------------------------------------------------------------------------
def add_or_update_data(new_data):
    data = get_user_data()
    for i, row in enumerate(data):
        if row["description"] == new_data["description"]:
            data[i] = new_data
            return
    data.append(new_data)


def delete_item(description):
    data = get_user_data()
    data[:] = [row for row in data if row["description"] != description]


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
def main():
    # ---- Header with user info ----
    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.markdown("<h2 style='margin-bottom:0'>🧾 Invoice Maker</h2>", unsafe_allow_html=True)
        st.caption(f"Signed in as **{user_name}** ({user_email})")
    with header_right:
        if st.button("Sign out", use_container_width=True):
            st.logout()

    st.divider()

    # ---- Store profile: load saved profile ----
    profiles = database.get_store_profiles(user_email)
    profile_names = [p["profile_name"] for p in profiles]

    selected_profile: dict | None = None
    if profiles:
        with st.expander("Load a saved store profile", expanded=False):
            chosen = st.selectbox("Select profile", [""] + profile_names, key="load_profile_sel")
            if chosen:
                selected_profile = next(p for p in profiles if p["profile_name"] == chosen)
                if st.button("Load profile", key="load_profile_btn"):
                    st.session_state["_loaded_profile"] = selected_profile
                    st.rerun()
                delete_col, _ = st.columns([1, 3])
                with delete_col:
                    if st.button("Delete profile", key="del_profile_btn"):
                        database.delete_store_profile(user_email, chosen)
                        st.success(f"Profile '{chosen}' deleted.")
                        st.rerun()

    lp = st.session_state.get("_loaded_profile", {})

    # ---- Store details ----
    current_date = datetime.now()
    order_date_default = current_date.strftime("%d/%m/%Y")

    from_data: dict = {}
    to_data: dict = {}

    with st.expander("Store Details", expanded=not bool(lp)):
        st.subheader("Store Information")
        from_col, to_col = st.columns(2)
        lp_from = lp.get("from_store", default_store_details["from"])
        lp_to = lp.get("to_store", default_store_details["to"])

        with from_col:
            st.write("From:")
            from_data["store_name"] = st.text_input("Store Name", key="from_store_name", value=lp_from.get("store_name", ""))
            from_data["store_address"] = st.text_input("Store Address", key="from_store_address", value=lp_from.get("store_address", ""))
            from_data["email_id"] = st.text_input("Email Address", key="from_email_address", value=lp_from.get("email_id", user_email))
            from_data["phone_number"] = st.text_input("Phone Number", key="from_phone_number", value=lp_from.get("phone_number", ""))
            from_data["tin_no"] = st.text_input("TIN No", key="from_tin_number", value=lp_from.get("tin_no", ""))
            from_data["cst_no"] = st.text_input("CST No", key="from_cst_number", value=lp_from.get("cst_no", ""))
            from_data["gst_no"] = st.text_input("GST No", key="from_gst_number", value=lp_from.get("gst_no", ""))

        with to_col:
            st.write("To:")
            to_data["store_name"] = st.text_input("Store Name", key="to_store_name", value=lp_to.get("store_name", ""))
            to_data["store_address"] = st.text_input("Store Address", key="to_store_address", value=lp_to.get("store_address", ""))
            to_data["email_id"] = st.text_input("Email Address", key="to_email_id", value=lp_to.get("email_id", ""))
            to_data["phone_number"] = st.text_input("Phone Number", key="to_phone_number", value=lp_to.get("phone_number", ""))
            to_data["tin_no"] = st.text_input("TIN No", key="to_tin_number", value=lp_to.get("tin_no", ""))
            to_data["cst_no"] = st.text_input("CST No", key="to_cst_number", value=lp_to.get("cst_no", ""))
            to_data["gst_no"] = st.text_input("GST No", key="to_gst_number", value=lp_to.get("gst_no", ""))

        # Save profile
        st.divider()
        save_col1, save_col2 = st.columns([3, 1])
        with save_col1:
            profile_save_name = st.text_input(
                "Save these details as a profile (name it):",
                placeholder="e.g. My Shop → Client A",
                key="profile_save_name",
            )
        with save_col2:
            st.write("")  # vertical alignment spacer
            st.write("")
            if st.button("Save profile", key="save_profile_btn"):
                if profile_save_name.strip():
                    database.save_store_profile(
                        user_email,
                        profile_save_name.strip(),
                        from_data,
                        to_data,
                        lp.get("cgst_rate", 9.0),
                        lp.get("sgst_rate", 9.0),
                    )
                    st.success(f"Profile '{profile_save_name.strip()}' saved.")
                else:
                    st.warning("Enter a profile name first.")

    # ---- Tax rates ----
    with st.expander("Tax Rate", expanded=False):
        cgst_rate = st.number_input("CGST Percentage", step=0.1, value=float(lp.get("cgst_rate", 9.0)))
        sgst_rate = st.number_input("SGST Percentage", step=0.1, value=float(lp.get("sgst_rate", 9.0)))

    # ---- Order details ----
    st.write("Order Details:")
    order_number = st.text_input("Order Number")
    order_date = st.text_input("Order Date", value=order_date_default)

    # ---- Item list ----
    user_data = get_user_data()

    with st.expander("Item List", expanded=True):
        descr = st.text_input("Description")
        qty = st.number_input("Quantity", min_value=1, step=1)
        units = st.text_input("Units", value="Count")
        unit_price = st.number_input("Unit Price", min_value=0, step=1)

        new_data = {
            "description": descr,
            "Qty": qty,
            "Units": units,
            "UnitPrice": unit_price,
            "Amount": qty * unit_price,
        }

        if st.button("Add / Update Item"):
            if descr.strip():
                add_or_update_data(new_data)
                st.rerun()
            else:
                st.warning("Enter an item description.")

        if user_data:
            st.dataframe(
                [{k: v for k, v in row.items()} for row in user_data],
                use_container_width=True,
            )
            for row in list(user_data):
                if st.button(f"Delete — {row['description']}", key=f"del_{row['description']}"):
                    delete_item(row["description"])
                    st.rerun()

    # ---- Generate invoice ----
    if st.button("Generate Invoice", type="primary", use_container_width=True):
        if not user_data:
            st.error("Add at least one item before generating the invoice.")
        elif not order_number.strip():
            st.error("Enter an order number.")
        else:
            invoice_data = {
                "from": from_data,
                "to": to_data,
                "order_num": order_number,
                "order_date": order_date,
                "cgst_rate": cgst_rate,
                "sgst_rate": sgst_rate,
                "user_data": list(user_data),
            }
            tmp_path, pdf_filename = generate_pdf(invoice_data)
            st.success("Invoice generated!")
            with open(tmp_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Invoice PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
