from typing import Any, Text, Dict, List
from flask import session
import mysql.connector
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from tabulate import tabulate
import uuid
import re
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from keras.models import load_model
from keras.layers import Dense, LSTM, Bidirectional, Dropout
from keras.losses import Huber, Loss
from keras.optimizers import Adam
from PIL import Image
import os

import sys

areas_in_polygon = {
    'A': ["kiryatgat", "be'ersheva", "beersheva", "netivot", "rahat", "rafat", "dimona", "einhatseva", "ramathovav", "ktura", "elifaz", "tsukim"],
    'B': ["ashdod", "ashkelon", "gadera", "kiryatekron", "kiryatmalakhi", "talshahar", "negba", "rehovot"],
    'C': ["birzeit", "jerusalem", "ramallah", "kohavhashahar", "jericho", "hebron", "nehusha", "shoresh", "eshta'ol", "eshtaol", "nahshon", "modi'inllit", "modiinllit"],
    'E': ["batyam", "beithanan", "holon", "lod", "modi'inmakkabbim-reut", "modiinmakkabbimreut", "ramatgan", "ramla", "rishonletsiyon", "shoham", "petahtikva"],
    'F': ["beitaryeh-ofraim", "beitaryehofraim", "elkana", "hodhasharon", "herzliya", "huwara", "kefarsava", "kadimazohran", "netanya", "ra'anana", "raanana", "ramathasharon", "roshhaayin", "salfit", "shiloh", "tubas", "nablus"],
    'G': ["afula", "haifa", "tamra", "kiryatata", "kiryatbialik", "kiryatyam", "zihronya'akov", "zihronyaakov"," bakae-gabriya", "bakaegabriya", "jenin", "daliyate-kamrel", "daliyatekamrel", "hadera", "umm al-fahm", "ummalfahm", "nazareth"],
    'H': ["ma'alottarshiha", "maalottarshiha", "karmiel", "haspin", "kiryatshemona", "migdal", "qatsrin", "kafarkanna", "northshuna", "beitshe'na"]
}


list_of_products = ["electronic", "households", "clothes", "cloths", "electric"]

# ============================== GET,SET REQUIRED DATA and CHECK THAT IS PRESENT IN list ==============================


def present_loc(location: str, areas_in_polygon: dict[str, list[str]]) -> bool:
    location = location.lower()
    location = location.replace(" ", "")
    for locations_list in areas_in_polygon.values():
        if location in locations_list:
            return True
    return False


class ActionGetSourceAddress(Action):
    def name(self) -> Text:
        return "utter_get_source_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_get_source_address")
        return []


class ActionSetSourceAddress(Action):
    def name(self) -> Text:
        return "set_source_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        source_address = tracker.latest_message.get('text')

        source_city = get_city_name(source_address)
        if present_loc(source_city, areas_in_polygon):
            return [SlotSet("source_address", source_address)]
        # else:
        #     dispatcher.utter_message(response="utter_error_from_location")


class ActionGetDestAddress(Action):
    def name(self) -> Text:
        return "utter_get_dest_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_get_dest_address")
        return []


class ActionSetDestAddress(Action):
    def name(self) -> Text:
        return "set_dest_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dest_address = tracker.latest_message.get('text')

        dest_city = get_city_name(dest_address)
        if present_loc(dest_city, areas_in_polygon):
            return [SlotSet("dest_address", dest_address)]
        # else:
        #     dispatcher.utter_message(response="utter_error_to_location")


def check_product(product: str, list_of_products: list[str]) -> bool:
    product = product.lower()
    if product in list_of_products:
        return True
    return False


class ActionGetProduct(Action):
    def name(self) -> Text:
        return "utter_get_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_get_product")
        return []


class ActionSetProduct(Action):
    def name(self) -> Text:
        return "set_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        product = tracker.latest_message.get('text')
        if check_product(product, list_of_products):
            return [SlotSet("product", product)]
        # else:
        #     dispatcher.utter_message(response="utter_error_products")


class ActionGetWeight(Action):
    def name(self) -> Text:
        return "utter_get_weight"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_get_weight")
        return []


class ActionGetPhoneNumber(Action):
    def name(self) -> Text:
        return "utter_get_phone_number"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_get_phone_number")
        return []


class ActionSetPhoneNumber(Action):
    def name(self) -> Text:
        return "set_phone_number"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        message = tracker.latest_message.get('text')
        # phone_number = re.search(r'(0[2-9]-\d{3}-\d{4}|05[2-9]-\d{3}-\d{4}|0[2-9]\d{7}|05[2-9]\d{7})', message)
        phone_number = re.search(r'(0[2-9]\d{7}|05[2-9]\d{7})', message)
        if phone_number:
            phone_number = phone_number.group()
            return [SlotSet("phone_number", phone_number)]
        else:
            dispatcher.utter_message(response="utter_error_phone_number")


class ActionAskOrderId(Action):
    def name(self) -> Text:
        return "utter_ask_order_id"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_order_id")
        return []


class ActionSetOrderId(Action):
    def name(self) -> Text:
        return "set_order_id"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:
        message = tracker.latest_message.get('text')
        order_id = re.search(r'\b\d{14}-[0-9a-f]{8}\b', message)
        if order_id:
            order_id = order_id.group()
            return [SlotSet("order_id", order_id)]
        else:
            dispatcher.utter_message(response="utter_error_order_id")

# ================================================== DATABASE CONNECTION ==============================================


mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Krunal2810",
                database="chatbot_data",
                auth_plugin='mysql_native_password'
            )

# ============================================ 3. QUOTATION FUNCTIONALITY ============================================


def get_polygon_for_location(location: str, areas_in_polygon: dict[str, list[str]]) -> str:
    for polygon, locations in areas_in_polygon.items():
        if location in locations:
            return polygon
    return 'unknown'


def get_city_name(address: str) -> str:
    city_match = re.search(r'\b(\w+)\b$', address)
    city_name = city_match.group(1)
    return city_name


class ActionCalculateQuotation(Action):
    def name(self) -> Text:
        return "calculate_quotation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict[Text, Any]) -> list[dict[Text, Any]]:

        source_address = tracker.get_slot('source_address')
        dest_address = tracker.get_slot('dest_address')

        source_city = get_city_name(source_address)
        dest_city = get_city_name(dest_address)
        product = tracker.get_slot('product')
        parcel_weight_string = tracker.get_slot('weight')
        parcel_weight_int = int(parcel_weight_string)

        quotation_amount = None

        if present_loc(source_city, areas_in_polygon) and present_loc(dest_city,areas_in_polygon) and check_product(product,list_of_products):

            source_polygon = get_polygon_for_location(source_city, areas_in_polygon)
            dest_polygon = get_polygon_for_location(dest_city, areas_in_polygon)

            mycursor1 = mydb.cursor(buffered=True)
            mycursor1.execute("SELECT price FROM price_polygon WHERE source_polygon = %s AND dest_polygon = %s",(source_polygon, dest_polygon))
            polygon_price = mycursor1.fetchone()
            mycursor1.close()

            mycursor2 = mydb.cursor(buffered=True)
            mycursor2.execute("SELECT price FROM price_weight WHERE min_range <= %s AND max_range >= %s",(parcel_weight_int, parcel_weight_int))
            weight_price = mycursor2.fetchone()
            mycursor2.close()

            if polygon_price is not None and weight_price is not None:
                polygon_price = polygon_price[0]
                weight_price = weight_price[0]

                quotation_amount = polygon_price + weight_price

                dispatcher.utter_message(text=f"you are requesting a quotation from {source_city} to {dest_city} with weight of {parcel_weight_int} KG of {product}.")
                dispatcher.utter_message(text=f"Your Quotation is about {quotation_amount} ₪(NIS).")
                dispatcher.utter_message(text="Would you like to confirm the order? 1) For Yes, Say - Yes, Confirm order, Book order 2) For No, Say - Nope, No")

        elif not present_loc(source_city, areas_in_polygon) and not present_loc(dest_city, areas_in_polygon):
            dispatcher.utter_message(response="utter_error")

        elif not present_loc(dest_city, areas_in_polygon):
            dispatcher.utter_message(response="utter_error_to_location")

        elif not present_loc(source_city, areas_in_polygon):
            dispatcher.utter_message(response="utter_error_from_location")

        else:
            dispatcher.utter_message(response="utter_error_products")

        return [SlotSet('total_price', quotation_amount)]


# ============================================== 1. NEW ORDER FUNCTIONALITY ===========================================


def generate_order_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Generate a unique identifier
    order_id = f"{timestamp}-{unique_id}"
    return order_id


class ActionInsertOrder(Action):
    def name(self) -> Text:
        return "action_insert_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[Text, Any]) -> list[dict[Text, Any]]:

        # username = session.get('username')

        # flask_url = "http://127.0.0.1:5000/get_username"
        # response = requests.get(flask_url)
        # username = response.json().get('username')

        # custom_data = tracker.get_slot("custom_data")
        # username = custom_data.get("username")

        # username = tracker.get_slot('username')

        username = "KrunalShinde"

        order_id = generate_order_id()
        source_address = tracker.get_slot('source_address')
        dest_address = tracker.get_slot('dest_address')

        source_city = get_city_name(source_address)
        dest_city = get_city_name(dest_address)
        source_polygon = get_polygon_for_location(source_city, areas_in_polygon)
        dest_polygon = get_polygon_for_location(dest_city, areas_in_polygon)
        product = tracker.get_slot("product")
        parcel_weight = tracker.get_slot("weight")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        phone_number = tracker.get_slot("phone_number")

        total_price = tracker.get_slot('total_price')

        status = "delivery scheduled"

        # Insert the order into the database
        try:
            mycursor5 = mydb.cursor(buffered=True)
            # add_order = ("INSERT INTO deliveries (order_id, username, source_address, dest_address, source_city, dest_city, source_polygon, dest_polygon, product, parcel_weight, total_price, phone_number, timestamp, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            add_order = ("INSERT INTO deliveries_data (order_id, username, source_address, dest_address, source_city, dest_city, source_polygon, dest_polygon, product, parcel_weight, total_price, phone_number, timestamp, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            order_data = (order_id, username, source_address, dest_address, source_city, dest_city, source_polygon, dest_polygon, product, parcel_weight, total_price, phone_number, timestamp, status)
            mycursor5.execute(add_order, order_data)
            mycursor5.close()
            mydb.commit()

            dispatcher.utter_message(response="utter_order_placed")
            dispatcher.utter_message(text=f"Here is your Order ID: {order_id}")

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        return []


# ================================================ 4. HISTORY FUNCTIONALITY ===========================================


def fetch_and_format_data(query, data):
    mycursor6 = mydb.cursor(buffered=True)
    mycursor6.execute(query, data)
    rows = mycursor6.fetchall()
    headers = [i[0] for i in mycursor6.description]
    tabular_data = tabulate(rows, headers=headers, tablefmt='pretty', numalign="left", stralign="center")
    mycursor6.close()

    return tabular_data


class ActionDisplayTable(Action):
    def name(self):
        return "action_display_history"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[Text, Any]) -> list[dict[Text, Any]]:

        # username = session.get('username')

        # flask_url = "http://127.0.0.1:5000/get_username"
        # response = requests.get(flask_url)
        # username = response.json().get('username')

        # custom_data = tracker.get_slot("custom_data")
        # username = custom_data.get("username")

        # username = tracker.get_slot('username')

        username = "KrunalShinde"
        query = "SELECT order_id, source_city, dest_city, product, parcel_weight, total_price FROM deliveries_data WHERE username = %s"
        data = (username,)
        table = fetch_and_format_data(query, data)

        # mycursor6 = mydb.cursor(buffered=True)
        # mycursor6.execute(query, data)
        # rows = mycursor6.fetchall()
        # mycursor6.close()

        # history_data = [dict(zip(('Order ID', 'Source City', 'Dest City', 'Product', 'Parcel Weight', 'Total Price'), row)) for row in rows]
        # history_table = format_history_table(history_data)

        dispatcher.utter_message(table)

        return []


# ======================================== 2. CHECK STATUS OF ORDER FUNCTIONALITY =====================================


class ActionCheckStatus(Action):
    def name(self):
        return "action_check_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[Text, Any]) -> list[dict[Text, Any]]:

        order_id = tracker.get_slot("order_id")

        mycursor7 = mydb.cursor(buffered=True)
        # mycursor7.execute("SELECT status FROM deliveries WHERE order_id = %s", (order_id,))
        mycursor7.execute("SELECT status FROM deliveries_data WHERE order_id = %s", (order_id,))
        delivery_status1 = mycursor7.fetchone()

        delivery_status = delivery_status1[0]
        mycursor7.close()

        dispatcher.utter_message(text=f"Your delivery status for {order_id} is: {delivery_status}")

        return []


# ========================================================= ETA =======================================================


def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(city_name)
    return location.latitude, location.longitude


def calculate_distance(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) * 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) * 2
    if a > 1.0:
        a = 1.0
    elif a < 0.0:
        a = 0.0
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c
    return distance


def predict_eta(from_city, to_city, date):
    depotLatitude, depotLongitude = get_coordinates(from_city)
    endLatitude, endLongitude = get_coordinates(to_city)
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    depot_hour = int(date_obj.hour)
    depot_minute = int(date_obj.minute)
    month = int(date_obj.month)
    day_of_month = int(date_obj.day)
    year = int(date_obj.year)

    distance1 = calculate_distance(depotLatitude, depotLongitude, endLatitude, endLongitude)

    scaler = MinMaxScaler()
    distance = scaler.fit_transform(np.array([[distance1]]))[0][0]

    input_data = np.array([[depotLatitude, depotLongitude, endLatitude, endLongitude, distance, depot_hour, depot_minute, month, day_of_month, year]])
    model = load_model('ETA_Model/2.11.0.keras')
    optimizer = Adam(0.01)
    model.compile(loss=Huber, optimizer=optimizer)
    predicted_eta = model.predict(input_data)
    predicted_eta_hours, predicted_eta_minutes = divmod(predicted_eta[0][0], 60)
    delivery_datetime = date_obj + timedelta(hours=predicted_eta_hours, minutes=predicted_eta_minutes)

    return int(predicted_eta_hours), int(predicted_eta_minutes), delivery_datetime


class ActionPredictETA(Action):
    def name(self):
        return "action_predict_eta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[Text, Any]) -> list[dict[Text, Any]]:

        source_address = tracker.get_slot('source_address')
        dest_address = tracker.get_slot('dest_address')

        source_city = get_city_name(source_address)
        dest_city = get_city_name(dest_address)

        date = datetime.now().strftime('%Y-%m-%d')

        predicted_eta_hours, predicted_eta_minutes, delivery_datetime = predict_eta(source_city, dest_city, date)

        # dispatcher.utter_message(text=f"Your delivery : {predicted_eta_hours} hours {predicted_eta_minutes} minutes")
        dispatcher.utter_message(text=f"Arriving by: {delivery_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        return []
