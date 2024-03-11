import copy

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib import fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate
from reportlab.lib.pagesizes import portrait,A4
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib import colors
import base64

current_date = datetime.now()
order_date = current_date.strftime("%d/%m/%Y")
default_store_details =  {
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


def dev_load_defaults(invoice_data):
    current_date = datetime.now()
    order_date = current_date.strftime("%d/%m/%Y")
    invoice_data = {
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
    return invoice_data

def add_thousand_separator(number_str):
    try:
        # Convert the string to a float or int
        number = int(number_str)

        # Format it with thousand and lakh separators
        #formatted_number = "{:,.2f}".format(number) if '.' in number_str else "{:,.0f}".format(number)
        Cr = int(number // 10000000)
        Lakh = int(number // 100000)
        Thousand = int(number % 100000) // 1000
        Rupees = str(number_str[-3:])

        formatted_amt = ""
        if Cr > 0:
            formatted_amt += str(Cr) + ","
        if Lakh > 0:
            formatted_amt += str(Lakh) + ","
        if Thousand > 0:
            formatted_amt += str(Thousand) + ","
        formatted_amt+=Rupees
        return formatted_amt
    except ValueError:
        # Handle invalid input gracefully
        return "Invalid Input"


def generate_pdf(invoice_data):
    pdf_filename = invoice_data["order_num"]+"__"+str(invoice_data["order_date"]).replace("/","-")+".pdf"

    doc = SimpleDocTemplate(pdf_filename, pagesize=portrait(A4))
    doc.leftMargin=10
    doc.rightMargin=10
    # Create a list to hold the flowables (elements) of the PDF
    elements = []

    # Define styles for the document
    styles = getSampleStyleSheet()
    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)

    # Add a title to the PDF report
    title = Paragraph("Tax Invoice", styles["Title"])
    elements.append(title)

    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)

    # Add some paragraphs of text to the PDF
    text = """
         
         Order Number: {:70}     Order Date: {:20}
        
        """.format(invoice_data["order_num"],invoice_data["order_date"] )

    font_path = "./Consolas.ttf"

    # Register the custom font
    pdfmetrics.registerFont(TTFont("Consolas", font_path))

    custom_style = ParagraphStyle(name="ConsolasStyle", fontName="Consolas", fontSize=8)

    paragraph1 = Preformatted(text, style=custom_style)
    elements.append(paragraph1)

    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)


    # Add some paragraphs of text to the PDF
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



    paragraph2 = Preformatted(text,style=custom_style)
    elements.append(paragraph2)
    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)

    text = """
        --------------------------------------------------------------------------------------------------------------------
    """
    line = Preformatted(text, style=custom_style)
    elements.append(line)
    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)
    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)



    text = """
        List of Items:
        """
    line = Preformatted(text, style=custom_style)
    elements.append(line)

    blank_line = Spacer(1, 12)  # 12 points of blank space (adjust as needed)
    elements.append(blank_line)

    # Create a sample table
    data = invoice_data["user_data"]
    table_data = [["item", "description", "Qty", "Units", "UnitPrice", "Amount(Rs)"]]
    item_number = 1
    amt_before_tax=0
    for item in data:
        table_data.append([item_number, item["description"],
                           item["Qty"], item["Units"],
                           add_thousand_separator(str(item["UnitPrice"])), add_thousand_separator(str(item["Amount"]))])
        item_number += 1
        amt_before_tax += item["Amount"]

    table_data.append(["Total Amount Before Tax", "", "", "", "", add_thousand_separator(str(amt_before_tax))])
    cgst = round((invoice_data["cgst_rate"]/100)*amt_before_tax)
    sgst = round((invoice_data["sgst_rate"]/100)*amt_before_tax)
    grand_total = round(amt_before_tax+cgst+sgst)

    #table_data.append(["Total Amount Before Tax", "", "", "", "", amt_before_tax])
    table_data.append(["CGST", "", "", "", "", add_thousand_separator(str(cgst))])
    table_data.append(["SGST", "", "", "","", add_thousand_separator(str(sgst))])
    table_data.append(["Grand Total", "", "", "", "", add_thousand_separator(str(grand_total))])

    table = Table(table_data, colWidths=[30, 220, 30, 30, 50, 80, 80])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Consolas'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('SPAN', (0, -1), (-2, -1)),  # Merge cells for the grand total row
                               ('BACKGROUND', (0, -1), (-2, -1), colors.grey),  # Grand total row background color
                               ('TEXTCOLOR', (0, -1), (-2, -1), colors.whitesmoke),  # Grand total row text color
                               ('ALIGN', (0, -1), (-2, -1), 'RIGHT'),
                               ('SPAN', (0, -2), (-2, -2)),  # Merge cells for the SGST
                               ('BACKGROUND', (0, -2), (-2, -2), colors.grey),  # SGST row background color
                               ('TEXTCOLOR', (0, -2), (-2, -2), colors.whitesmoke),  # SGST row text color
                               ('ALIGN', (0, -2), (-2, -2), 'RIGHT'),
                               ('SPAN', (0, -3), (-2, -3)),  # Merge cells for the SGST
                               ('BACKGROUND', (0, -3), (-2, -3), colors.grey),  # SGST row background color
                               ('TEXTCOLOR', (0, -3), (-2, -3), colors.whitesmoke),  # SGST row text color
                               ('ALIGN', (0, -3), (-2, -3), 'RIGHT'),
                               ('SPAN', (0, -4), (-2, -4)),  # Merge cells for the SGST
                               ('BACKGROUND', (0, -4), (-2, -4), colors.grey),  # SGST row background color
                               ('TEXTCOLOR', (0, -4), (-2, -4), colors.whitesmoke),  # SGST row text color
                               ('ALIGN', (0, -4), (-2, -4), 'RIGHT'),
                               #('ALIGN', (0, -5), (-2, -5), 'RIGHT'),
                               #('SPAN', (0, -5), (-2, -5)),  # Merge cells for the SGST
                               #('BACKGROUND', (0, -5), (-2, -5), colors.grey),  # SGST row background color
                               #('TEXTCOLOR', (0, -5), (-2, -5), colors.whitesmoke),  # SGST row text color
                               ]))

    elements.append(table)

    # Build the PDF document
    doc.build(elements)
    return pdf_filename

@st.cache_resource()
def initialize_data():
    return []

@st.cache_resource()
def initialize_from_data():
    return []

@st.cache_resource()
def initialize_to_data():
    return []

# Function to add or update a row in the table
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

# Function to delete a row by name
def delete_data(data, name_to_delete):
    data[:] = [row for row in data if row["description"] != name_to_delete]


def main():
    st.markdown("""
        <h1 style='text-align: center;'>Invoice Maker</h1>
    """, unsafe_allow_html=True)

    user_from_data = initialize_from_data()
    user_to_data = initialize_to_data()

    user_data = initialize_data()



    current_date = datetime.now()
    order_date = current_date.strftime("%d/%m/%Y")

    from_data = {}
    to_data = {}
    #order_date = st.text_input("Date")
    with st.expander("Store Details:", expanded=False):
        st.subheader("Store Information")
        from_col, to_col = st.columns(2)
        with from_col:
            st.write("From:")
            from_data["from_store_name"] = st.text_input("Store Name",key="from_store_name",value=default_store_details["from"]["store_name"])
            from_data["from_store_address"] = st.text_input("Store Address",key="from_store_address",value=default_store_details["from"]["store_address"])
            from_data["from_email_id"] = st.text_input("Email Address",key="from_email_address",value=default_store_details["from"]["email_id"])
            from_data["from_phone_number"] = st.text_input("Phone Number",key="from_phone_number",value=default_store_details["from"]["phone_number"])
            from_data["from_tin_no"] = st.text_input("TIN No",key="from_tin_number",value=default_store_details["from"]["tin_no"])
            from_data["from_CST_no"] = st.text_input("CST No",key="from_cst_numbber",value=default_store_details["from"]["cst_no"])
            from_data["from_GST_no"] = st.text_input("GST No",key="from_gst_number",value=default_store_details["from"]["gst_no"])

        with to_col:
            st.write("To:")
            to_data["to_store_name"] = st.text_input("Store Name",key="to_store_name",value=default_store_details["to"]["store_name"])
            to_data["to_store_address"] = st.text_input("Store Address",key="to_store_address",value=default_store_details["to"]["store_address"])
            to_data["to_email_id"] = st.text_input("Email Address",key="to_email_id",value=default_store_details["to"]["email_id"])
            to_data["to_phone_number"] = st.text_input("Phone Number",key="to_phone_number",value=default_store_details["to"]["phone_number"])
            to_data["to_tin_no"] = st.text_input("TIN No",key="to_tin_number",value=default_store_details["to"]["tin_no"])
            to_data["to_CST_no"] = st.text_input("CST No",key="to_cst_number",value=default_store_details["to"]["cst_no"])
            to_data["to_GST_no"] = st.text_input("GST No",key="to_gst_number",value=default_store_details["to"]["gst_no"])

    #order_reference = st.text_input("Order Reference")
    with st.expander("Tax Rate:", expanded=False):
        cgst_rate = st.number_input("CGST Percentage",step=0.1,value=9.0)
        sgst_rate = st.number_input("SGST Percentage",step=0.1,value=9.0)

    st.write("Order Details:")
    order_number = st.text_input("Order Number")
    order_date = st.text_input("Order Date",value=order_date)
    with st.expander("Item List", expanded=True):
        #Items

        #item = st.text_input("Item")
        descr = st.text_input("Description")
        #size = st.number_input("Size",min_value=1,step=1)
        Qty = st.number_input("Quantity",min_value=1,step=1)
        Units = st.text_input("Units",value="Count")
        UnitPrice = st.number_input("Unit Price",min_value=0,step=1)
        Amount = Qty * UnitPrice

        new_data = {
            "description": descr,
            "Qty": Qty,
            "Units": Units,
            "UnitPrice": UnitPrice,
            "Amount": Qty * UnitPrice
        }
        if st.button("Add / Update Item"):
            add_or_update_data(user_data, new_data)
            add_or_update_from_storedata(user_from_data, from_data)
            add_or_update_to_storedata(user_to_data, to_data)

        with st.container():

            tcol1,tcol2 = st.columns([0.2,0.8])# Display the table
            for row in user_data:
                with tcol1:
                    row["Delete"] = st.button("Delete {}".format(row['description']))
            if user_data != []:
                with tcol2:
                    st.dataframe(user_data)
            #df.append(user_data)
            # Show "Delete" button for each row
            for row in user_data:
                if row["Delete"]:
                    delete_data(user_data, row["description"])

    if st.button("Generate Invoice"):
        invoice_data = {
            "from": {
                "store_name": from_data["from_store_name"],
                "store_address": from_data["from_store_address"],
                "email_id": from_data["from_email_id"],
                "phone_number": from_data["from_phone_number"],
                "tin_no": from_data["from_tin_no"],
                "cst_no": from_data["from_CST_no"],
                "gst_no": from_data["from_GST_no"]
            },
            "to": {
                "store_name": to_data["to_store_name"],
                "store_address": to_data["to_store_address"],
                "email_id": to_data["to_email_id"],
                "phone_number": to_data["to_phone_number"],
                "tin_no": to_data["to_tin_no"],
                "cst_no": to_data["to_CST_no"],
                "gst_no": to_data["to_GST_no"]
            },
            "order_num": order_number,
            "order_date": order_date,
            "cgst_rate": cgst_rate,
            "sgst_rate": sgst_rate,
            "user_data": user_data
        }
        #st.write(invoice_data)
        #invoice_data = dev_load_defaults(invoice_data)
        if invoice_data:
            pdf_filename = generate_pdf(invoice_data)
            st.success(f"PDF generated successfully!")
            with open(pdf_filename, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_data).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{pdf_base64}" download="'.format(pdf_filename)+'">Download</a>',unsafe_allow_html=True)
        else:
            st.error("Please fill in all fields before generating the PDF.")



if __name__ == "__main__":
    main()
