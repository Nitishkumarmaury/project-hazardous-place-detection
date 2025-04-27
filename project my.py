import time
import datetime
import folium
import requests


locations = [
    {"name": "Bus Parking", "lat": 30.767245, "lon": 76.578947, "update_delay": 20, "clear_delay": 40, "impact": "Clear", "impact_10": "Low impact", "impact_30": "High impact", "updated": False, "cleared": False},
    {"name": "Block B1", "lat": 30.769943, "lon": 76.575689, "update_delay": 30, "clear_delay": 60, "impact": "Clear", "impact_10": "High impact", "impact_30": "Severe impact", "updated": False, "cleared": False},
    {"name": "AIT Dept.", "lat": 30.771294, "lon": 76.570741, "update_delay": 40, "clear_delay": 50, "impact": "Clear", "impact_10": "Low impact", "impact_30": "High impact", "updated": False, "cleared": False},
]


BOT_TOKEN = "7982878792:AAGrPx4pD-A-ZHRCa4WwwheXwZ3LJX9KCDA"
CHAT_ID = "1186220114"


IMPACT_COLORS = {
    "Low impact": "green",
    "High impact": "orange",
    "Severe impact": "red",
    "Clear": "gray" 
}


def send_telegram_notification(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print(f"Failed to send notification: {response.text}")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")


def plot_map(locations, map_file="C:\\Users\\Nitish Maurya\\Desktop\\my projectmm\\danger_map.html"):
    time.sleep(2) 
    m = folium.Map(location=[30.7699, 76.5748], zoom_start=16)
    for loc in locations:
     
        if loc["impact"] == "Clear":
            continue
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=f"{loc['name']}: {loc['impact']}",
            icon=folium.Icon(color=IMPACT_COLORS.get(loc["impact"], "gray")),
        ).add_to(m)
    m.save(map_file)
    print(f"Map saved at {map_file}")


def main():
    print("Starting rain monitoring system...")
    script_start_time = datetime.datetime.now()
    rain_duration = 60  
    clear_duration = 120  
    rain_end_time = script_start_time + datetime.timedelta(seconds=rain_duration)
    clear_end_time = rain_end_time + datetime.timedelta(seconds=clear_duration)

    while True:
        current_time = datetime.datetime.now()

       
        if script_start_time <= current_time < rain_end_time:
            for loc in locations:
                elapsed_time = (current_time - script_start_time).total_seconds()
                if not loc["updated"] and elapsed_time >= loc["update_delay"]:
                    loc["impact"] = loc["impact_10"] if elapsed_time < 30 else loc["impact_30"]
                    loc["updated"] = True
                    print(f"Updating location: {loc['name']} with impact: {loc['impact']}")
                    
                   
                    message = f"Rain update: {loc['name']} - {loc['impact']}"
                    send_telegram_notification(BOT_TOKEN, CHAT_ID, message)

            plot_map(locations)


        if rain_end_time <= current_time < clear_end_time:
            for loc in locations:
                clear_time = rain_end_time + datetime.timedelta(seconds=loc["clear_delay"])
                if not loc["cleared"] and current_time >= clear_time:
                    loc["impact"] = "Clear"
                    loc["cleared"] = True
                    print(f"Clearing location: {loc['name']}")
                    
                
                    message = f"Rain has stopped. Clearing location: {loc['name']}."
                    send_telegram_notification(BOT_TOKEN, CHAT_ID, message)

            plot_map(locations)

 
        if current_time >= clear_end_time:
            print("All locations are now clear.")
            break

        time.sleep(1)

if __name__ == "__main__":
    main()
9