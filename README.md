# project-hazardous-place-detection
This Python project monitors rain impact across multiple locations, dynamically updating a Folium-based map and sending real-time alerts via Telegram. It simulates rainfall progression, adjusts impact levels, clears alerts after rain stops, and visualizes everything with color-coded map markers.
Below is a comprehensive, line-by-line explanation of  script. Each section first summarizes its purpose, then breaks down every line with detailed descriptions.  

## Summary  
This Python script monitors simulated “rain impact” at multiple GPS locations, updates their status over time, plots them on an interactive Folium map, and sends Telegram notifications when impacts change or clear. It uses the `time` and `datetime` modules for scheduling, `folium` for map generation, and `requests` to call the Telegram Bot API.  

---

## 📥 Imports  

| Line(s) | Code                                 | Description                                                                                                      |
|:-------:|:-------------------------------------|:-----------------------------------------------------------------------------------------------------------------|
| 1       | `import time`                        | Imports the **time** module, which provides time-related functions like `sleep()` to pause execution  ([Python Time Module | GeeksforGeeks](https://www.geeksforgeeks.org/python-time-module/?utm_source=chatgpt.com)). |
| 2       | `import datetime`                    | Imports the **datetime** module for manipulating dates and times, such as obtaining the current timestamp  ([Python Dates - W3Schools](https://www.w3schools.com/python/python_datetime.asp?utm_source=chatgpt.com)). |
| 3       | `import folium`                      | Imports **Folium**, a Python library for creating interactive Leaflet maps  ([Python Folium: Create Web Maps From Your Data](https://realpython.com/python-folium-web-maps-from-data/?utm_source=chatgpt.com)).                      |
| 4       | `import requests`                    | Imports **Requests**, a popular HTTP library to send web requests (used here for Telegram API calls)  ([Python Requests post Method - W3Schools](https://www.w3schools.com/python/ref_requests_post.asp?utm_source=chatgpt.com)). |

---

## 📍 Location Definitions  

```python
locations = [
    {"name": "Bus Parking", "lat": 30.767245, "lon": 76.578947, "update_delay": 20, "clear_delay": 40, "impact": "Clear", "impact_10": "Low impact", "impact_30": "High impact", "updated": False, "cleared": False},
    ...
]
```

- Defines a **list of dictionaries**, each representing one monitored site  ([Iterate through list of dictionaries in Python | GeeksforGeeks](https://www.geeksforgeeks.org/iterate-through-list-of-dictionaries-in-python/?utm_source=chatgpt.com)).  
- Keys per dict:  
  - `"name"`: human-readable label  
  - `"lat"`, `"lon"`: GPS coordinates  
  - `"update_delay"` / `"clear_delay"`: seconds until status change after rain starts/ends  
  - `"impact"`: current status string  
  - `"impact_10"` / `"impact_30"`: statuses at 10s-30s and after 30s of rain  
  - `"updated"` / `"cleared"`: booleans to avoid duplicate actions  

---

## 🔧 Global Constants  

```python
BOT_TOKEN = "…"  
CHAT_ID = "1186220114"  
```

- `BOT_TOKEN`: your Telegram bot’s authorization token (keeps API calls authenticated)  ([Telegram Bot API](https://core.telegram.org/bots/api?utm_source=chatgpt.com)).  
- `CHAT_ID`: destination chat or user ID for notifications.  

```python
IMPACT_COLORS = {
    "Low impact": "green",
    "High impact": "orange",
    "Severe impact": "red",
    "Clear": "gray" 
}
```

- Maps each impact level to a **Folium marker color**  ([Map with markers with Python and Folium](https://python-graph-gallery.com/312-add-markers-on-folium-map/?utm_source=chatgpt.com)).  

---

## 📨 send_telegram_notification  

```python
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
```

1. **Function signature** declares parameters for bot token, chat ID, and text  ([Python Requests post Method - W3Schools](https://www.w3schools.com/python/ref_requests_post.asp?utm_source=chatgpt.com)).  
2. Builds the **Telegram Bot API** URL using an f-string  ([Telegram Bot API](https://core.telegram.org/bots/api?utm_source=chatgpt.com)).  
3. Prepares JSON payload with `chat_id` and `text`.  
4. `try` block to catch network errors.  
5. `requests.post(...)` sends the HTTP POST  ([Python Requests post Method - W3Schools](https://www.w3schools.com/python/ref_requests_post.asp?utm_source=chatgpt.com)).  
6. Checks `response.status_code` for success (200) or logs failure.  
7. `except` prints any exception message.  

---

## 🗺️ plot_map  

```python
def plot_map(locations, map_file="…/danger_map.html"):
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
```

1. **Pauses 2 s** before regenerating map to throttle file writes  ([time.sleep() in Python | GeeksforGeeks](https://www.geeksforgeeks.org/sleep-in-python/?utm_source=chatgpt.com)).  
2. Creates a **Folium Map** centered at given coords, zoom level 16  ([Python Folium: Create Web Maps From Your Data](https://realpython.com/python-folium-web-maps-from-data/?utm_source=chatgpt.com)).  
3. Loops through each location dict  ([Iterate through list of dictionaries in Python | GeeksforGeeks](https://www.geeksforgeeks.org/iterate-through-list-of-dictionaries-in-python/?utm_source=chatgpt.com)).  
4. Skips markers when impact is `"Clear"`.  
5. Adds a **Marker** with popup text and colored icon  ([Map with markers with Python and Folium](https://python-graph-gallery.com/312-add-markers-on-folium-map/?utm_source=chatgpt.com)).  
6. Saves the HTML file and logs its path.  

---

## ⚙️ main Loop  

```python
def main():
    print("Starting rain monitoring system...")
    script_start_time = datetime.datetime.now()
    rain_duration = 60
    clear_duration = 120
    rain_end_time = script_start_time + datetime.timedelta(seconds=rain_duration)
    clear_end_time = rain_end_time + datetime.timedelta(seconds=clear_duration)
```

- Prints a start message.  
- Records **start timestamp** via `datetime.datetime.now()`  ([datetime — Basic date and time types — Python 3.13.3 documentation](https://docs.python.org/3/library/datetime.html?utm_source=chatgpt.com)).  
- Defines durations in seconds.  
- Calculates `rain_end_time` and `clear_end_time` using `timedelta`  ([Python | datetime.timedelta() function - GeeksforGeeks](https://www.geeksforgeeks.org/python-datetime-timedelta-function/?utm_source=chatgpt.com)).  

```python
    while True:
        current_time = datetime.datetime.now()
```

- Begins infinite loop; updates `current_time` each iteration.  

### 🌧️ Rain-active phase  

```python
        if script_start_time <= current_time < rain_end_time:
            for loc in locations:
                elapsed_time = (current_time - script_start_time).total_seconds()
                if not loc["updated"] and elapsed_time >= loc["update_delay"]:
                    loc["impact"] = loc["impact_10"] if elapsed_time < 30 else loc["impact_30"]
                    loc["updated"] = True
                    message = f"Rain update: {loc['name']} - {loc['impact']}"
                    send_telegram_notification(BOT_TOKEN, CHAT_ID, message)
            plot_map(locations)
```

1. Checks if still in **rain period**.  
2. For each location, computes seconds elapsed  ([Python Dates - W3Schools](https://www.w3schools.com/python/python_datetime.asp?utm_source=chatgpt.com)).  
3. If not yet updated and past its `update_delay`, sets `impact` to either `impact_10` or `impact_30`.  
4. Marks `updated=True` to avoid repeats.  
5. Sends a Telegram update  ([Telegram Bot API](https://core.telegram.org/bots/api?utm_source=chatgpt.com)).  
6. Regenerates the map to reflect new markers.  

### 🌤️ Clearing phase  

```python
        if rain_end_time <= current_time < clear_end_time:
            for loc in locations:
                clear_time = rain_end_time + datetime.timedelta(seconds=loc["clear_delay"])
                if not loc["cleared"] and current_time >= clear_time:
                    loc["impact"] = "Clear"
                    loc["cleared"] = True
                    message = f"Rain has stopped. Clearing location: {loc['name']}."
                    send_telegram_notification(BOT_TOKEN, CHAT_ID, message)
            plot_map(locations)
```

- After rain ends, but before clear period ends, each location clears after its `clear_delay`.  
- Sends a “clearing” notification and updates the map.  

### 🛑 Termination  

```python
        if current_time >= clear_end_time:
            print("All locations are now clear.")
            break
        time.sleep(1)
```

- Once past `clear_end_time`, logs completion and breaks the loop.  
- Sleeps 1 s each iteration to avoid busy-waiting  ([time.sleep() in Python | GeeksforGeeks](https://www.geeksforgeeks.org/sleep-in-python/?utm_source=chatgpt.com)).  

---

## 🚀 Entry Point  

```python
if __name__ == "__main__":
    main()
```

- Ensures `main()` runs only when script is executed directly, not when imported as a module  ([What Does if __name__ == "__main__" Do in Python?](https://realpython.com/if-name-main-python/?utm_source=chatgpt.com)).  

---

You now have a detailed breakdown of every line—feel free to ask if any part needs further clarification!
