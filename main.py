import copy
import io
import json
import os
import re

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

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

TEMPLATES_FILE = "templates.json"

current_date = datetime.now()
order_date = current_date.strftime("%d/%m/%Y")
default_store_details = {
        "from": {
            "store_name": "ship gifts online",
            "store_address": "18/7 Booshanam St, Ayanvaram, Chennai 600023",
            "email_id": "sudhansadanand@gmail.com",
            "phone_number": "8925383335",
            "tin_no": "234578234",
            "cst_no": "34535442345",
            "gst_no": "31413342342"
        },
        "to": {
            "store_name": "wishfullly",
            "store_address": "E9 Shanti Gulmohar apartments, RK mutt road, Chennai 600023",
            "email_id": "ranjithavasu@gmail.com",
            "phone_number": "8925393335",
            "tin_no": "5424523453415",
            "cst_no": "1234123414344",
            "gst_no": "3245263523455"
        },
        "order_num": "896754",
        "order_date": order_date,
        "cgst rate": 9,
        "sgst rate": 9
    }


# ---------------------------------------------------------------------------
# Template management
# ---------------------------------------------------------------------------

def load_templates():
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_template(template_name, template_data):
    templates = load_templates()
    templates[template_name] = template_data
    with open(TEMPLATES_FILE, "w") as f:
        json.dump(templates, f, indent=2)


def delete_template(template_name):
    templates = load_templates()
    if template_name in templates:
        del templates[template_name]
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=2)


# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------

def extract_invoice_data_from_pdf(pdf_bytes):
    """Parse a BillThis-generated PDF and return extracted field values.

    Returns (extracted_dict, raw_text).
    """
    extracted = {
        "from": {
            "store_name": "",
            "store_address": "",
            "email_id": "",
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
        "cgst_rate": 9.0,
        "sgst_rate": 9.0,
    }

    if not PDFPLUMBER_AVAILABLE:
        return extracted, "pdfplumber library is not installed."

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        return extracted, f"Error reading PDF: {e}"

    lines = full_text.split("\n")

    # Field label patterns that appear side-by-side (From ... To) on the same line.
    # The BillThis PDF places both columns on one line separated by whitespace.
    paired_patterns = [
        ("store_name",    r"Store Name\s*:\s*(.+?)\s{2,}Store Name\s*:\s*(.+)"),
        ("store_address", r"Store Address\s*:\s*(.+?)\s{2,}Store Address\s*:\s*(.+)"),
        ("email_id",      r"Email id\s*:\s*(.+?)\s{2,}Email id\s*:\s*(.+)"),
        ("phone_number",  r"Phone Number\s*:\s*(.+?)\s{2,}Phone Number\s*:\s*(.+)"),
        ("tin_no",        r"TIN number\s*:\s*(.+?)\s{2,}TIN number\s*:\s*(.+)"),
        ("cst_no",        r"CST number\s*:\s*(.+?)\s{2,}CST number\s*:\s*(.+)"),
        ("gst_no",        r"GST number\s*:\s*(.+?)\s{2,}GST number\s*:\s*(.+)"),
    ]

    in_address_continuation = False
    from_addr_parts = []
    to_addr_parts = []

    for line in lines:
        for field, pattern in paired_patterns:
            m = re.search(pattern, line)
            if m:
                from_val = m.group(1).strip()
                to_val = m.group(2).strip()
                extracted["from"][field] = from_val
                extracted["to"][field] = to_val

                if field == "store_address":
                    from_addr_parts = [from_val]
                    to_addr_parts = [to_val]
                    in_address_continuation = True
                else:
                    in_address_continuation = False
                break
        else:
            # Check for address continuation line (second address line in long-address format)
            if in_address_continuation:
                # A continuation line has heavy leading whitespace and two values separated by spaces
                cont = re.match(r"^\s{8,}(\S.+?)\s{2,}(\S.+?)\s*$", line)
                if cont:
                    from_addr_parts.append(cont.group(1).strip())
                    to_addr_parts.append(cont.group(2).strip())
                    extracted["from"]["store_address"] = ", ".join(from_addr_parts)
                    extracted["to"]["store_address"] = ", ".join(to_addr_parts)
                in_address_continuation = False

    # Extract CGST / SGST amounts to back-calculate rates (best-effort)
    # The table rows look like: "CGST ... 450" and "Total Amount Before Tax ... 5000"
    # We look for them to derive rates, but fall back to 9% defaults if not found.
    subtotal_match = re.search(r"Total Amount Before Tax\s+[\d,]+", full_text)
    cgst_amt_match = re.search(r"\bCGST\b\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+)", full_text)
    sgst_amt_match = re.search(r"\bSGST\b\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+)", full_text)

    # Simpler fallback: look for standalone CGST / SGST amount at end of a table row
    cgst_simple = re.search(r"^CGST\s+([\d,]+)\s*$", full_text, re.MULTILINE)
    sgst_simple = re.search(r"^SGST\s+([\d,]+)\s*$", full_text, re.MULTILINE)
    subtotal_simple = re.search(r"^Total Amount Before Tax\s+([\d,]+)\s*$", full_text, re.MULTILINE)

    if cgst_simple and subtotal_simple:
        try:
            cgst_amt = int(cgst_simple.group(1).replace(",", ""))
            subtotal = int(subtotal_simple.group(1).replace(",", ""))
            if subtotal > 0:
                extracted["cgst_rate"] = round((cgst_amt / subtotal) * 100, 1)
        except (ValueError, ZeroDivisionError):
            pass

    if sgst_simple and subtotal_simple:
        try:
            sgst_amt = int(sgst_simple.group(1).replace(",", ""))
            subtotal = int(subtotal_simple.group(1).replace(",", ""))
            if subtotal > 0:
                extracted["sgst_rate"] = round((sgst_amt / subtotal) * 100, 1)
        except (ValueError, ZeroDivisionError):
            pass

    return extracted, full_text


# ---------------------------------------------------------------------------
# Existing helpers
# ---------------------------------------------------------------------------

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
    pdf_filename = invoice_data["order_num"] + "__" + str(invoice_data["order_date"]).replace("/", "-") + ".pdf"

    doc = SimpleDocTemplate(pdf_filename, pagesize=portrait(A4))
    doc.leftMargin = 10
    doc.rightMargin = 10
    elements = []

    styles = getSampleStyleSheet()
    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    title = Paragraph("Tax Invoice", styles["Title"])
    elements.append(title)

    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    text = """

         Order Number: {:70}     Order Date: {:20}

        """.format(invoice_data["order_num"], invoice_data["order_date"])

    font_path = "./Consolas.ttf"
    pdfmetrics.registerFont(TTFont("Consolas", font_path))
    custom_style = ParagraphStyle(name="ConsolasStyle", fontName="Consolas", fontSize=8)

    paragraph1 = Preformatted(text, style=custom_style)
    elements.append(paragraph1)

    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    if ((len(invoice_data["from"]["store_address"]) <= 30) and
            (len(invoice_data["to"]["store_address"]) <= 30)):

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
            """.format(invoice_data["from"]["store_name"],
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
                       invoice_data["to"]["gst_no"])

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
            """.format(str(invoice_data["from"]["store_name"]),
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
                       invoice_data["to"]["gst_no"])

    paragraph2 = Preformatted(text, style=custom_style)
    elements.append(paragraph2)
    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    text = """
        --------------------------------------------------------------------------------------------------------------------
    """
    line = Preformatted(text, style=custom_style)
    elements.append(line)
    blank_line = Spacer(1, 12)
    elements.append(blank_line)
    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    text = """
        List of Items:
        """
    line = Preformatted(text, style=custom_style)
    elements.append(line)

    blank_line = Spacer(1, 12)
    elements.append(blank_line)

    data = invoice_data["user_data"]
    table_data = [["item", "description", "Qty", "Units", "UnitPrice", "Amount(Rs)"]]
    item_number = 1
    amt_before_tax = 0
    for item in data:
        table_data.append([item_number, item["description"],
                           item["Qty"], item["Units"],
                           add_thousand_separator(str(item["UnitPrice"])), add_thousand_separator(str(item["Amount"]))])
        item_number += 1
        amt_before_tax += item["Amount"]

    table_data.append(["Total Amount Before Tax", "", "", "", "", add_thousand_separator(str(amt_before_tax))])
    cgst = round((invoice_data["cgst_rate"] / 100) * amt_before_tax)
    sgst = round((invoice_data["sgst_rate"] / 100) * amt_before_tax)
    grand_total = round(amt_before_tax + cgst + sgst)

    table_data.append(["CGST", "", "", "", "", add_thousand_separator(str(cgst))])
    table_data.append(["SGST", "", "", "", "", add_thousand_separator(str(sgst))])
    table_data.append(["Grand Total", "", "", "", "", add_thousand_separator(str(grand_total))])

    table = Table(table_data, colWidths=[40, 230, 50, 50, 70, 90])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Consolas'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('SPAN', (0, -1), (-2, -1)),
                               ('BACKGROUND', (0, -1), (-2, -1), colors.grey),
                               ('TEXTCOLOR', (0, -1), (-2, -1), colors.whitesmoke),
                               ('ALIGN', (0, -1), (-2, -1), 'RIGHT'),
                               ('SPAN', (0, -2), (-2, -2)),
                               ('BACKGROUND', (0, -2), (-2, -2), colors.grey),
                               ('TEXTCOLOR', (0, -2), (-2, -2), colors.whitesmoke),
                               ('ALIGN', (0, -2), (-2, -2), 'RIGHT'),
                               ('SPAN', (0, -3), (-2, -3)),
                               ('BACKGROUND', (0, -3), (-2, -3), colors.grey),
                               ('TEXTCOLOR', (0, -3), (-2, -3), colors.whitesmoke),
                               ('ALIGN', (0, -3), (-2, -3), 'RIGHT'),
                               ('SPAN', (0, -4), (-2, -4)),
                               ('BACKGROUND', (0, -4), (-2, -4), colors.grey),
                               ('TEXTCOLOR', (0, -4), (-2, -4), colors.whitesmoke),
                               ('ALIGN', (0, -4), (-2, -4), 'RIGHT'),
                               ]))

    elements.append(table)
    doc.build(elements)
    return pdf_filename


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

@st.cache_resource()
def initialize_data():
    return []


@st.cache_resource()
def initialize_from_data():
    return []


@st.cache_resource()
def initialize_to_data():
    return []


def add_or_update_data(data, new_data):
    updated = False
    for i, row in enumerate(data):
        if row["description"] == new_data["description"]:
            data[i] = new_data
            updated = True
            break
    if not updated:
        data.append(new_data)


def add_or_update_from_storedata(data, new_data):
    updated = False
    for i, row in enumerate(data):
        if row["from_store_name"] == new_data["from_store_name"]:
            data[i] = new_data
            updated = True
            break
    if not updated:
        data.append(new_data)


def add_or_update_to_storedata(data, new_data):
    updated = False
    for i, row in enumerate(data):
        if row["to_store_name"] == new_data["to_store_name"]:
            data[i] = new_data
            updated = True
            break
    if not updated:
        data.append(new_data)


def delete_data(data, name_to_delete):
    data[:] = [row for row in data if row["description"] != name_to_delete]


def _get(key, default=""):
    """Return session_state value or default."""
    return st.session_state.get(key, default)


def _apply_template_to_session(tpl):
    """Write template field values into st.session_state so the form picks them up."""
    frm = tpl.get("from", {})
    to = tpl.get("to", {})
    st.session_state["inv_from_store_name"]    = frm.get("store_name", "")
    st.session_state["inv_from_store_address"] = frm.get("store_address", "")
    st.session_state["inv_from_email_id"]      = frm.get("email_id", "")
    st.session_state["inv_from_phone_number"]  = frm.get("phone_number", "")
    st.session_state["inv_from_tin_no"]        = frm.get("tin_no", "")
    st.session_state["inv_from_cst_no"]        = frm.get("cst_no", "")
    st.session_state["inv_from_gst_no"]        = frm.get("gst_no", "")
    st.session_state["inv_to_store_name"]      = to.get("store_name", "")
    st.session_state["inv_to_store_address"]   = to.get("store_address", "")
    st.session_state["inv_to_email_id"]        = to.get("email_id", "")
    st.session_state["inv_to_phone_number"]    = to.get("phone_number", "")
    st.session_state["inv_to_tin_no"]          = to.get("tin_no", "")
    st.session_state["inv_to_cst_no"]          = to.get("cst_no", "")
    st.session_state["inv_to_gst_no"]          = to.get("gst_no", "")
    st.session_state["inv_cgst_rate"]          = float(tpl.get("cgst_rate", 9.0))
    st.session_state["inv_sgst_rate"]          = float(tpl.get("sgst_rate", 9.0))


# ---------------------------------------------------------------------------
# Tab renderers
# ---------------------------------------------------------------------------

def render_invoice_tab(user_data, user_from_data, user_to_data):
    """Tab 1 – Create a new invoice, optionally loading a saved template."""

    # --- Template loader ---
    templates = load_templates()
    if templates:
        st.markdown("#### Load from Template (optional)")
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            chosen = st.selectbox(
                "Select a template",
                options=["— none —"] + list(templates.keys()),
                key="inv_template_selector",
                label_visibility="collapsed",
            )
        with col_btn:
            if st.button("Load", key="inv_load_template_btn"):
                if chosen != "— none —":
                    _apply_template_to_session(templates[chosen])
                    st.success(f"Template '{chosen}' loaded.")
                    st.rerun()
        st.markdown("---")

    current_date_str = datetime.now().strftime("%d/%m/%Y")

    from_data = {}
    to_data = {}

    with st.expander("Store Details:", expanded=False):
        st.subheader("Store Information")
        from_col, to_col = st.columns(2)
        with from_col:
            st.write("From:")
            from_data["from_store_name"]    = st.text_input("Store Name",    key="inv_from_store_name",    value=_get("inv_from_store_name",    default_store_details["from"]["store_name"]))
            from_data["from_store_address"] = st.text_input("Store Address", key="inv_from_store_address", value=_get("inv_from_store_address", default_store_details["from"]["store_address"]))
            from_data["from_email_id"]      = st.text_input("Email Address", key="inv_from_email_id",      value=_get("inv_from_email_id",      default_store_details["from"]["email_id"]))
            from_data["from_phone_number"]  = st.text_input("Phone Number",  key="inv_from_phone_number",  value=_get("inv_from_phone_number",  default_store_details["from"]["phone_number"]))
            from_data["from_tin_no"]        = st.text_input("TIN No",        key="inv_from_tin_no",        value=_get("inv_from_tin_no",        default_store_details["from"]["tin_no"]))
            from_data["from_CST_no"]        = st.text_input("CST No",        key="inv_from_cst_no",        value=_get("inv_from_cst_no",        default_store_details["from"]["cst_no"]))
            from_data["from_GST_no"]        = st.text_input("GST No",        key="inv_from_gst_no",        value=_get("inv_from_gst_no",        default_store_details["from"]["gst_no"]))

        with to_col:
            st.write("To:")
            to_data["to_store_name"]    = st.text_input("Store Name",    key="inv_to_store_name",    value=_get("inv_to_store_name",    default_store_details["to"]["store_name"]))
            to_data["to_store_address"] = st.text_input("Store Address", key="inv_to_store_address", value=_get("inv_to_store_address", default_store_details["to"]["store_address"]))
            to_data["to_email_id"]      = st.text_input("Email Address", key="inv_to_email_id",      value=_get("inv_to_email_id",      default_store_details["to"]["email_id"]))
            to_data["to_phone_number"]  = st.text_input("Phone Number",  key="inv_to_phone_number",  value=_get("inv_to_phone_number",  default_store_details["to"]["phone_number"]))
            to_data["to_tin_no"]        = st.text_input("TIN No",        key="inv_to_tin_no",        value=_get("inv_to_tin_no",        default_store_details["to"]["tin_no"]))
            to_data["to_CST_no"]        = st.text_input("CST No",        key="inv_to_cst_no",        value=_get("inv_to_cst_no",        default_store_details["to"]["cst_no"]))
            to_data["to_GST_no"]        = st.text_input("GST No",        key="inv_to_gst_no",        value=_get("inv_to_gst_no",        default_store_details["to"]["gst_no"]))

    with st.expander("Tax Rate:", expanded=False):
        cgst_rate = st.number_input("CGST Percentage", step=0.1, value=float(_get("inv_cgst_rate", 9.0)), key="inv_cgst_input")
        sgst_rate = st.number_input("SGST Percentage", step=0.1, value=float(_get("inv_sgst_rate", 9.0)), key="inv_sgst_input")

    st.write("Order Details:")
    order_number = st.text_input("Order Number")
    order_date   = st.text_input("Order Date", value=current_date_str)

    with st.expander("Item List", expanded=True):
        descr     = st.text_input("Description")
        Qty       = st.number_input("Quantity",   min_value=1, step=1)
        Units     = st.text_input("Units",        value="Count")
        UnitPrice = st.number_input("Unit Price", min_value=0, step=1)

        new_data = {
            "description": descr,
            "Qty":         Qty,
            "Units":       Units,
            "UnitPrice":   UnitPrice,
            "Amount":      Qty * UnitPrice,
        }
        if st.button("Add / Update Item"):
            add_or_update_data(user_data, new_data)
            add_or_update_from_storedata(user_from_data, from_data)
            add_or_update_to_storedata(user_to_data, to_data)

        with st.container():
            tcol1, tcol2 = st.columns([0.2, 0.8])
            for row in user_data:
                with tcol1:
                    row["Delete"] = st.button("Delete {}".format(row["description"]))
            if user_data:
                with tcol2:
                    st.dataframe(user_data)
            for row in user_data:
                if row["Delete"]:
                    delete_data(user_data, row["description"])

    if st.button("Generate Invoice"):
        invoice_data = {
            "from": {
                "store_name":    from_data["from_store_name"],
                "store_address": from_data["from_store_address"],
                "email_id":      from_data["from_email_id"],
                "phone_number":  from_data["from_phone_number"],
                "tin_no":        from_data["from_tin_no"],
                "cst_no":        from_data["from_CST_no"],
                "gst_no":        from_data["from_GST_no"],
            },
            "to": {
                "store_name":    to_data["to_store_name"],
                "store_address": to_data["to_store_address"],
                "email_id":      to_data["to_email_id"],
                "phone_number":  to_data["to_phone_number"],
                "tin_no":        to_data["to_tin_no"],
                "cst_no":        to_data["to_CST_no"],
                "gst_no":        to_data["to_GST_no"],
            },
            "order_num":  order_number,
            "order_date": order_date,
            "cgst_rate":  cgst_rate,
            "sgst_rate":  sgst_rate,
            "user_data":  [{k: v for k, v in row.items() if k != "Delete"} for row in user_data],
        }
        if invoice_data:
            pdf_filename = generate_pdf(invoice_data)
            st.success("PDF generated successfully!")
            with open(pdf_filename, "rb") as pdf_file:
                pdf_data   = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_data).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_filename}">Download Invoice</a>',
                unsafe_allow_html=True,
            )
        else:
            st.error("Please fill in all fields before generating the PDF.")


def render_pdf_template_tab():
    """Tab 2 – Upload a PDF invoice, review extracted data, save as template."""

    st.markdown("### Create Template from PDF")
    st.write(
        "Upload a BillThis-generated invoice PDF. "
        "The app will extract the sender/recipient details and tax rates, "
        "which you can review and save as a reusable template."
    )

    if not PDFPLUMBER_AVAILABLE:
        st.error(
            "The `pdfplumber` library is not installed. "
            "Run `pip install pdfplumber` and restart the app."
        )
        return

    uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"], key="pdf_uploader")

    if uploaded_file is None:
        return

    pdf_bytes = uploaded_file.read()
    extracted, raw_text = extract_invoice_data_from_pdf(pdf_bytes)

    st.markdown("#### Extracted Data — review and correct if needed")
    st.info(
        "Fields were parsed automatically from the PDF text. "
        "Edit any values below before saving."
    )

    frm_col, to_col = st.columns(2)

    with frm_col:
        st.write("**From (Sender)**")
        frm_name  = st.text_input("Store Name",    value=extracted["from"]["store_name"],    key="tpl_from_store_name")
        frm_addr  = st.text_input("Store Address", value=extracted["from"]["store_address"], key="tpl_from_store_address")
        frm_email = st.text_input("Email Address", value=extracted["from"]["email_id"],      key="tpl_from_email_id")
        frm_phone = st.text_input("Phone Number",  value=extracted["from"]["phone_number"],  key="tpl_from_phone_number")
        frm_tin   = st.text_input("TIN No",        value=extracted["from"]["tin_no"],        key="tpl_from_tin_no")
        frm_cst   = st.text_input("CST No",        value=extracted["from"]["cst_no"],        key="tpl_from_cst_no")
        frm_gst   = st.text_input("GST No",        value=extracted["from"]["gst_no"],        key="tpl_from_gst_no")

    with to_col:
        st.write("**To (Recipient)**")
        to_name  = st.text_input("Store Name",    value=extracted["to"]["store_name"],    key="tpl_to_store_name")
        to_addr  = st.text_input("Store Address", value=extracted["to"]["store_address"], key="tpl_to_store_address")
        to_email = st.text_input("Email Address", value=extracted["to"]["email_id"],      key="tpl_to_email_id")
        to_phone = st.text_input("Phone Number",  value=extracted["to"]["phone_number"],  key="tpl_to_phone_number")
        to_tin   = st.text_input("TIN No",        value=extracted["to"]["tin_no"],        key="tpl_to_tin_no")
        to_cst   = st.text_input("CST No",        value=extracted["to"]["cst_no"],        key="tpl_to_cst_no")
        to_gst   = st.text_input("GST No",        value=extracted["to"]["gst_no"],        key="tpl_to_gst_no")

    st.markdown("**Tax Rates**")
    tax_col1, tax_col2 = st.columns(2)
    with tax_col1:
        cgst_rate = st.number_input("CGST %", value=float(extracted["cgst_rate"]), step=0.1, key="tpl_cgst_rate")
    with tax_col2:
        sgst_rate = st.number_input("SGST %", value=float(extracted["sgst_rate"]), step=0.1, key="tpl_sgst_rate")

    st.markdown("---")
    st.markdown("**Save as Template**")
    tpl_name = st.text_input(
        "Template name",
        placeholder="e.g. My Business – Regular Customer",
        key="tpl_name_input",
    )

    if st.button("Save Template", key="tpl_save_btn"):
        if not tpl_name.strip():
            st.error("Please enter a name for the template.")
        else:
            template_data = {
                "from": {
                    "store_name":    frm_name,
                    "store_address": frm_addr,
                    "email_id":      frm_email,
                    "phone_number":  frm_phone,
                    "tin_no":        frm_tin,
                    "cst_no":        frm_cst,
                    "gst_no":        frm_gst,
                },
                "to": {
                    "store_name":    to_name,
                    "store_address": to_addr,
                    "email_id":      to_email,
                    "phone_number":  to_phone,
                    "tin_no":        to_tin,
                    "cst_no":        to_cst,
                    "gst_no":        to_gst,
                },
                "cgst_rate": cgst_rate,
                "sgst_rate": sgst_rate,
            }
            save_template(tpl_name.strip(), template_data)
            st.success(f"Template '{tpl_name.strip()}' saved! Go to 'Create Invoice' tab to use it.")

    with st.expander("Raw extracted text (for debugging)", expanded=False):
        st.text(raw_text)


def render_manage_templates_tab():
    """Tab 3 – View and delete saved templates."""

    st.markdown("### Saved Templates")
    templates = load_templates()

    if not templates:
        st.info("No templates saved yet. Upload a PDF in the 'PDF → Template' tab to create one.")
        return

    for name, tpl in list(templates.items()):
        with st.expander(name, expanded=False):
            frm = tpl.get("from", {})
            to  = tpl.get("to",   {})

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**From**")
                st.write(f"Store: {frm.get('store_name', '')}")
                st.write(f"Address: {frm.get('store_address', '')}")
                st.write(f"Email: {frm.get('email_id', '')}")
                st.write(f"Phone: {frm.get('phone_number', '')}")
                st.write(f"TIN: {frm.get('tin_no', '')} | CST: {frm.get('cst_no', '')} | GST: {frm.get('gst_no', '')}")
            with col2:
                st.markdown("**To**")
                st.write(f"Store: {to.get('store_name', '')}")
                st.write(f"Address: {to.get('store_address', '')}")
                st.write(f"Email: {to.get('email_id', '')}")
                st.write(f"Phone: {to.get('phone_number', '')}")
                st.write(f"TIN: {to.get('tin_no', '')} | CST: {to.get('cst_no', '')} | GST: {to.get('gst_no', '')}")

            st.write(f"CGST: {tpl.get('cgst_rate', 9.0)}%  |  SGST: {tpl.get('sgst_rate', 9.0)}%")

            if st.button(f"Delete '{name}'", key=f"del_tpl_{name}"):
                delete_template(name)
                st.success(f"Template '{name}' deleted.")
                st.rerun()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="BillThis – GST Invoice Generator", page_icon="🧾", layout="centered")
    st.markdown("""
        <h1 style='text-align: center;'>🧾 BillThis</h1>
        <p style='text-align: center; color: #6366f1; margin-top: -12px; font-size: 1rem;'>Free GST Invoice Generator for Indian Businesses</p>
    """, unsafe_allow_html=True)

    user_from_data = initialize_from_data()
    user_to_data   = initialize_to_data()
    user_data      = initialize_data()

    tab1, tab2, tab3 = st.tabs(["Create Invoice", "PDF → Template", "Manage Templates"])

    with tab1:
        render_invoice_tab(user_data, user_from_data, user_to_data)

    with tab2:
        render_pdf_template_tab()

    with tab3:
        render_manage_templates_tab()


if __name__ == "__main__":
    main()
