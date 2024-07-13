from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
from pdf_generator import PdfGenerator as PDF
from werkzeug.utils import secure_filename
import os
from helper import (
    download_images,
    classify_images,
    count_files_in_folder,
    generate_car_parts_pdf,
)
from datetime import datetime
import requests
import json
from database import insert, check_login, get_db_connection, bcrypt, get_costs, get_count
from Scrapping import scrap_Car_Data
from Vin_Scrapper import scrape_vehicle_info_and_options, scrape_navigation_tabs

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Translations
with open("translations/page_1/translation.json", "r", encoding="UTF-8") as file1:
    page_1_translation = json.load(file1)
with open("translations/page_2/translation.json", "r", encoding="UTF-8") as file2:
    page_2_translation = json.load(file2)
with open("translations/page_3/translation.json", "r", encoding="UTF-8") as file3:
    page_3_translation = json.load(file3)


#with open("translations/terms/translation.json", "r", encoding="UTF-8") as file4:
#terms_translation = json.load(file4)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        result = check_login(username, password)

        if result is not None:  # Check if login was successful
            user_type, phone, user_id = result

            session['loginPage'] = {
                "username": username,
                "user_type": user_type,
                "phone": phone,
                "user_id": user_id,
            }
            if user_type == 1:
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("page_1"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


# Admin page
@app.route("/admin", methods=["GET", "POST"])
def admin():
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users")
                users = cursor.fetchall()
        week_no, go_fees_percent, germany_shipping, custom_fees = get_costs()
        costs = {
            "week_no": week_no,
            "go_fees_percent": go_fees_percent,
            "germany_shipping": germany_shipping,
            "custom_fees": custom_fees
        }
        session["costs"] = costs
        return render_template("admin.html", users=users, costs=costs)
    except Exception as e:
        flash(f"An error occurred: {e}")
        return render_template("admin.html", users=[], costs={})


@app.route("/update_cost/<field_name>", methods=["POST"])
def update_cost(field_name):
    field_value = request.form.get(field_name)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"UPDATE costs SET {field_name} = %s", (field_value,))
                conn.commit()

        # Update the session data
        session['costs'][field_name] = field_value
        flash(f"{field_name.replace('_', ' ').title()} updated successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('admin'))


# Add user
@app.route("/add_user", methods=("GET", "POST"))
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        if not name or not password or not user_type:
            flash("Name, Password, and User Type are required!")
        else:
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO users (Name,Phone_Number,Email, Password, User_Type) VALUES (%s,%s,%s,%s, %s)",
                            (name, phone, email, hashed_password.decode("utf-8"), user_type),
                        )
                        conn.commit()
                return redirect(url_for("admin"))
            except Exception as e:
                flash(f"An error occurred: {e}")
    return render_template("add_user.html")


# Remove user
@app.route("/remove_user/<int:user_id>")
def remove_user(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
        return redirect(url_for("admin"))
    except Exception as e:
        flash(f"An error occurred: {e}")
        return redirect(url_for("admin"))


# Modify user
@app.route("/modify_user/<int:user_id>", methods=("GET", "POST"))
def modify_user(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()

        if request.method == "POST":
            name = request.form["name"]
            phone = request.form["phone"]
            email = request.form["email"]
            password = request.form["password"]
            user_type = request.form["user_type"]

            if not name or not user_type:
                flash("Name and User Type are required!")
            else:
                # Only hash and update the password if it is provided
                if password:
                    hashed_password = bcrypt.hashpw(
                        password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")
                else:
                    hashed_password = user["Password"]

                try:
                    with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "UPDATE users SET Name = %s, Phone_Number=%s,Email=%s, Password = %s, User_Type = %s WHERE user_id = %s",
                                (name, phone, email, hashed_password, user_type, user_id),
                            )
                            conn.commit()
                    return redirect(url_for("admin"))
                except Exception as e:
                    flash(f"An error occurred: {e}")

        return render_template("modify_user.html", user=user)
    except Exception as e:
        flash(f"An error occurred: {e}")
        return redirect(url_for("admin"))


@app.route("/change_language", methods=["POST"])
def change_language():
    selected_language = request.form.get("language")
    session["selected_language"] = selected_language
    return "", 200


@app.route("/page_1", methods=["GET", "POST"])
def page_1():
    selected_language = session.get("selected_language", "en")
    translations = page_1_translation[selected_language]
    loginPage = session.get("loginPage")
    user_type = loginPage.get("user_type")
    message = ""

    try:
        response = requests.get(
            "https://v6.exchangerate-api.com/v6/93f053c4ff131ee837f2e026/latest/USD"
        )
        rates = response.json()
        dollar_rate = (rates["conversion_rates"]["EGP"]) * 1.5
        euro_rate = (rates["conversion_rates"]["EUR"]) * 1.5
    except Exception as e:
        message = "Error In Retrieving The Currency Rates....Check The API."
        return render_template(
            "page_1.html",
            dollar_rate=None,
            euro_rate=None,
            translations=translations,
            selected_language=selected_language,
            message=message,
            user_type=user_type,
        )

    if request.method == "POST":
        try:
            default_dollar_rate = float(request.form.get("Default_dollar_rate"))
            default_euro_rate = float(request.form.get("Default_euro_rate"))
        except ValueError:
            message = "Error: Please Enter A Number For The Currency Rate."
            return render_template(
                "page_1.html",
                dollar_rate=None,
                euro_rate=None,
                translations=translations,
                selected_language=selected_language,
                message=message,
                user_type=user_type,
            )

        session["form_data_page1"] = {
            "pdf_language": request.form.get("pdfLanguage"),
            "dollar_rate": default_dollar_rate,
            "euro_rate": default_euro_rate,
            #"client_Message": request.form.get("defaultClientMessage"),
            #"GO_Message": request.form.get("defaultGoMessage"),
        }

        return redirect(url_for("page_2"))
    # Add conditional logic to render a back button for admin user
    if user_type == 1:
        return render_template(
            "page_1.html",
            dollar_rate=dollar_rate,
            euro_rate=euro_rate,
            translations=translations,
            selected_language=selected_language,
            message=message,
            user_type=user_type,
            show_back_button=True,
        )
    else:
        return render_template(
            "page_1.html",
            dollar_rate=dollar_rate,
            euro_rate=euro_rate,
            translations=translations,
            selected_language=selected_language,
            message=message,
            user_type=user_type,
        )


#@app.route("/terms_and_conditions")
#def terms_and_conditions():
#    selected_language = session.get("selected_language", "en")
#    translations = terms_translation[selected_language]
#    return render_template("terms.html", translations=translations)


@app.route("/page_2", methods=["GET", "POST"])
def page_2():
    selected_language = session.get("selected_language", "en")
    translations = page_2_translation[selected_language]
    message = ""

    if request.method == "POST":
        manual_checked = "manualCheckbox" in request.form
        session["form_data_page2"] = {
            "purchaser_name": request.form.get("purchaser_name"),
            "purchaser_email": request.form.get("purchaser_email"),
            "purchaser_phone": request.form.get("purchaser_phone"),
            "gender": request.form.get("gender"),
            "ad_link": request.form.get("ad_link"),
            "destination_city": request.form.get("defaultDestCity"),
            "Index": request.form.get("Index"),
            "manualCheckbox": manual_checked,
            "vin_num": request.form.get("vin_num"),
            "customs_option": request.form.get("customs_option"),
            "Egyptian_Customs": request.form.get("Egyptian_Customs"),
        }
        return redirect(url_for("page_3"))

    return render_template(
        "page_2.html",
        translations=translations,
        selected_language=selected_language,
        message=message,
    )


@app.route("/page_3", methods=["GET", "POST"])
def page_3():
    selected_language = session.get("selected_language", "en")
    translations = page_3_translation[selected_language]
    form_data_page1 = session.get("form_data_page1", {})
    form_data_page2 = session.get("form_data_page2", {})
    loginPage = session.get("loginPage", {})
    message = ""
    use_manual = form_data_page2.get("manualCheckbox")
    if request.method == "POST":
        egyptian_pound = request.form.get("egyptian_pound")
        title = request.form.get("title")

        week_no, go_fees_percent, germany_shipping, custom_fees = get_costs()

        if not use_manual:
            api_data, message = scrap_Car_Data(form_data_page2.get("ad_link"))
        else:
            car_features = request.form.get("car_features")
            car_features = [car_features.strip() for car_features in car_features.strip().split('\n') if
                            car_features.strip()]
            uploaded_files = request.files.getlist('images[]')
            app.config['images'] = 'images'
            for file in uploaded_files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['images'], filename))
            api_data = {
                "car_title": request.form.get("manufacturer_brand") + request.form.get("model"),
                "manufacturer_brand": request.form.get("manufacturer_brand"),
                "model": request.form.get("model"),
                "EngineSize": request.form.get("EngineSize"),
                "car_features": car_features,
                #"car_images": [],
                "car_price": request.form.get("car_price"),
                "mileage": request.form.get("mileage"),
                "fuel": request.form.get("fuel"),
                "transmission": request.form.get("transmission"),
                "power": request.form.get("power"),
                "color": request.form.get("color"),
                "firstregistration": request.form.get("firstregistration"),
            }
        session["api_data"] = api_data
        if message:
            return render_template(
                "page_3.html",
                translations=translations,
                selected_language=selected_language,
                message=message,
                use_manual=use_manual
            )

        date = datetime.today().strftime("%d.%m.%Y")
        username = loginPage.get("username")
        quotation_count = get_count(username) + 1
        Customs_option = form_data_page2.get("customs_option")

        if Customs_option == "New Car":
            car_type = "A"
        elif Customs_option == "Used Car":
            car_type = "B"
        else:
            car_type = "C"

        quotation_num = f"GO_{username}_{date}_{quotation_count}_{car_type}"
        input_data = {
            "purchaser_name": form_data_page2.get("purchaser_name"),
            "quotation_num": quotation_num,
            "Gender": form_data_page2.get("gender"),
            "gender_title": "Mr." if form_data_page2.get("gender") == "Male" else "Ms.",
            "purchaser_phone": form_data_page2.get("purchaser_phone", "(PHONE NO)"),
            "purchaser_email": form_data_page2.get("purchaser_email", ""),
            "Customs_option": form_data_page2.get("customs_option"),
            "Egyptian_Customs": float(form_data_page2.get("Egyptian_Customs")),
            "destination_city": form_data_page2.get("destination_city"),
            "seller_name": loginPage.get("username"),
            "seller_phone": loginPage.get("phone"),
            "dollar_rate": float(form_data_page1.get("dollar_rate", 0)),
            "euroRate": float(form_data_page1.get("euro_rate", 0)),
            "egyptian_pound": egyptian_pound,
            "G&O_Fees": float(go_fees_percent),
            "Germany_Shipping": float(germany_shipping),
            "Port_Customs_Fees": float(custom_fees),
            "Index": quotation_count,
            "user_id": loginPage.get("user_id"),
        }
        # PDF Checkboxes
        selected_language = form_data_page1.get("pdf_language")
        offer_pdf = request.form.get("offer_pdf")
        image_pdf = request.form.get("image_pdf")
        car_info_pdf = request.form.get("car_info_pdf")
        all_pdfs = request.form.get("all_pdfs")

        if not use_manual:
            download_images(api_data.get("car_images"))
            classify_images()
        else:
            classify_images()
        count = count_files_in_folder()
        if count < 7:
            message = "Error: Number Of Images In Folders Is Not Enough"
            return render_template(
                "page_3.html",
                translations=translations,
                selected_language=selected_language,
                message=message,
                use_manual=use_manual
            )

        if offer_pdf or all_pdfs:
            cost, customs, car_dict = PDF(
                api_data, input_data, selected_language, use_manual, title
            ).generate_pdf()

        quotation_num = input_data.get("quotation_num")

        if image_pdf or all_pdfs:
            generate_car_parts_pdf(quotation_num)

        vin = form_data_page2.get("vin_num")
        if vin and (car_info_pdf or all_pdfs):
            vehicle_url, options_url = scrape_navigation_tabs(vin)
            scrape_vehicle_info_and_options(vehicle_url, options_url, quotation_num)

        insert(cost=cost, customs=customs, car_dict=car_dict, input_data=input_data)

        message = "PDF generated successfully."
        return redirect(url_for('pdf_directory'))

    return render_template(
        "page_3.html",
        translations=translations,
        selected_language=selected_language,
        message=message,
        use_manual=use_manual
    )


@app.route("/pdf/")
def pdf_directory():
    subfolders = []
    directory = os.path.join(app.root_path, 'PDFS')
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            subfolders.append(os.path.relpath(os.path.join(root, dir), directory))
        break  # To only get the subfolders at the top level
    return render_template('pdf_list.html', subfolders=subfolders)


@app.route('/pdf/<path:subfolder>/')
def pdf_files_in_subfolder(subfolder):
    pdf_files = []
    directory = os.path.join(app.root_path, 'PDFS', subfolder)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.relpath(os.path.join(root, file), directory))
    return render_template('pdf_files.html', subfolder=subfolder, pdf_files=pdf_files)


@app.route('/pdf/download/<path:filename>')
def download_pdf(filename):
    directory = os.path.join(app.root_path, 'PDFS')
    return send_from_directory(directory, filename)
