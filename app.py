#####################################
#   Final Project
#   DSCI 554
#   #OpenToWork
#####################################


## Imports
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import geopandas as gpd


## Setup
app = Flask(__name__)
host = 'http://127.0.0.1:5000/'


## Function Definitions
# Preload data
def preload_data():
  all_cities = pd.read_csv('./data/all_cities.csv')
  all_cities = all_cities['city_name'].tolist()
  all_stores = pd.read_csv('./data/stores_new.csv')
  return all_cities, all_stores

# Filter data base on selection
def filter_city_state():
  global current_stores
  global current_city_state
  current_stores = all_stores[all_stores['city_state'] == current_city_state]
  lon, lat = current_stores.iloc[0]['longitude'], current_stores.iloc[0]['latitude']
  return lon, lat

# Create the map element
def create_map(data, lon, lat):
    # Create a map centered at the obtained location
    my_map = folium.Map(location=[lat, lon], zoom_start=11)
    #my_map = folium.Map(location=[39.678008, -75.652355], zoom_start=6)

    # Define colors for each brand
    colors = {
        'walmart': 'orange',
        'costco': 'gray',
        'target': 'red',
        'kroger': 'blue'
    }

    for index, row in data.iterrows():
        # Get the appropriate color for each brand
        marker_color = colors.get(row['brand'].lower(), 'gray')  # Default to gray if brand not found

        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"{row['brand']}<br>{row['address']}<br>{row['city']}, {row['state']} {row['postal_code']}",
            icon=folium.Icon(color=marker_color, icon="shopping-cart")
        ).add_to(my_map)

    return my_map._repr_html_()

# Create the choropleth map
def create_choro_map():
    global all_stores

    store_counts = all_stores.groupby(['state_full_name'])['brand'].count().reset_index(name='store_count')
    usa = gpd.read_file('./data/us-states.json')
    choro_dataset = usa.merge(store_counts, left_on='name', right_on='state_full_name', how='left').dropna()

    # Initialize the map
    m = folium.Map(location=[35.4052172, -109.6062729], zoom_start=4, scrollWheelZoom=False, dragging=True)

    # Setup binning for legend
    bins = list(choro_dataset['store_count'].quantile([0, 0.25, 0.5, 0.75, 1]))

    # Main map init
    folium.Choropleth(
        geo_data=choro_dataset.to_json(),
        name='choropleth',
        data=choro_dataset,
        columns=['name', 'store_count'],
        key_on='feature.properties.name',
        fill_color='BuPu',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='Number of Grocery Stores',
        bins=bins,
        reset=True
    ).add_to(m)

    # Tooltip styling
    style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}

    # Add GeoJson for tooltip
    NIL = folium.features.GeoJson(
        choro_dataset,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name', 'store_count'],
            aliases=['State', 'Number of Grocery Stores'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    m.add_child(NIL)
    m.keep_in_front(NIL)

    # Adding a LayerControl object
    folium.LayerControl().add_to(m)

    # Return the HTML representation of the map
    return m._repr_html_()
  
# Calculate data - Pie
def calc_pie():
  global current_stores
  global current_city_state
  
  counts = [0, 0 ,0, 0]
  store_counts = current_stores['brand'].value_counts()
  for store in store_counts.items():
    if store[0] == 'walmart':
      counts[0] = store[1]
    elif store[0] == 'target':
      counts[1] = store[1]
    elif store[0] == 'kroger':
      counts[2] = store[1]
    elif store[0] == 'costco':
      counts[3] = store[1]
  data = {
    'labels': ['Walmart', 'Target', 'Kroger', 'Costco'],
    'datasets': [{'data': counts, 'backgroundColor': ['#ffc22080', 'rgba(255, 0, 0, 0.6)', 'rgba(0, 0, 255, 0.6)', 'rgba(128, 128, 128, 0.6)']}]
  }
  
  return data

# Calculate data - Table
def calc_table():
  global current_stores
  global current_city_state
  
  counts = [0, 0 ,0, 0]
  store_counts = current_stores['brand'].value_counts()
  for store in store_counts.items():
    if store[0] == 'walmart':
      counts[0] = store[1]
    elif store[0] == 'target':
      counts[1] = store[1]
    elif store[0] == 'kroger':
      counts[2] = store[1]
    elif store[0] == 'costco':
      counts[3] = store[1]
  data = {
    'labels': ['Walmart', 'Target', 'Kroger', 'Costco'],
    'datasets': [{'data': counts}]
  };
  
  return data

# Calculate data - Bar
def calc_bar():
  global current_stores
  global current_city_state
  
  data = current_stores.values.tolist()
  return data

# Calculate data - Donut
def calc_donut():
  global current_stores
  global current_city_state
  
  data = current_stores.to_dict(orient='records')
  return data

# Calculcate data - Top Cities
def calc_top_cities():
  global all_stores
  dataSources = {
    'all': {'labels':[], 'data':[], 'backgroundColor':'#64c22099'},
    'walmart': {'labels':[], 'data':[], 'backgroundColor':'#ffc22080'},
    'kroger': {'labels':[], 'data':[], 'backgroundColor':'rgba(0, 0, 255, 0.6)'},
    'target': {'labels':[], 'data':[], 'backgroundColor':'rgba(255, 0, 0, 0.6)'},
    'costco': {'labels':[], 'data':[], 'backgroundColor':'rgba(128, 128, 128, 0.6)'}
  }
  
  all_counts = all_stores['city_state'].value_counts()
  dataSources['all']['labels'] = all_counts.head(10).index.tolist()
  dataSources['all']['data'] = all_counts.head(10).values.tolist()
  
  walmart_counts = all_stores[all_stores['brand']=='walmart']['city_state'].value_counts()
  dataSources['walmart']['labels'] = walmart_counts.head(10).index.tolist()
  dataSources['walmart']['data'] = walmart_counts.head(10).values.tolist()
  
  kroger_counts = all_stores[all_stores['brand']=='kroger']['city_state'].value_counts()
  dataSources['kroger']['labels'] = kroger_counts.head(10).index.tolist()
  dataSources['kroger']['data'] = kroger_counts.head(10).values.tolist()
  
  target_counts = all_stores[all_stores['brand']=='target']['city_state'].value_counts()
  dataSources['target']['labels'] = target_counts.head(10).index.tolist()
  dataSources['target']['data'] = target_counts.head(10).values.tolist()
  
  costco_counts = all_stores[all_stores['brand']=='costco']['city_state'].value_counts()
  dataSources['costco']['labels'] = costco_counts.head(10).index.tolist()
  dataSources['costco']['data'] = costco_counts.head(10).values.tolist()
  
  return dataSources


## Variable Initialization
all_cities, all_stores = preload_data()
current_city_state = 'Los Angeles, CA'
current_stores = all_stores[all_stores['city_state'] == current_city_state]


## Flask HTML Calls
# Load index.html on '/' url load
@app.route('/')
def initial_load():
  global all_stores
  
  choro_map_html = create_choro_map()
  top_cities_data = calc_top_cities()
  
  walmart = 0
  kroger = 0
  target = 0
  costco = 0
  
  for store in all_stores['brand'].value_counts().items():
    if store[0] == 'walmart':
      walmart = store[1]
    elif store[0] == 'target':
      target = store[1]
    elif store[0] == 'kroger':
      kroger = store[1]
    elif store[0] == 'costco':
      costco = store[1]
  
  return render_template('index.html', all_cities=all_cities, choro_map_html=choro_map_html, walmart=walmart, kroger=kroger, target=target, costco=costco, top_cities_data=top_cities_data)

# Actions post city selection
@app.route('/', methods=['POST', 'GET'])
def get_city():
  global current_stores
  global current_city_state
  
  if request.method == 'POST':
    current_city_state = request.form['city_state_select']
    print(current_city_state)
    lon, lat = filter_city_state()
    map_html = create_map(current_stores, lon, lat)
    return render_template('map.html', map_html=map_html, current_city_state=current_city_state)
    
# Load map
@app.route('/map')
def mymap():
  global current_city_state

  lon, lat = filter_city_state()
  map_html = create_map(current_stores, lon, lat)
  return render_template('map.html', map_html=map_html, current_city_state=current_city_state)
  
# Load store count
@app.route('/store_counts')
def pie():
  global current_city_state
  
  pie_data = calc_pie()
  bar_data = calc_bar()
  table_data = calc_table()
  return render_template('store_counts.html', pie_data=pie_data, bar_data=bar_data, table_data=table_data, current_city_state=current_city_state)

# Load store rating
@app.route('/store_ratings')
def donut():
  global current_city_state
  
  data = calc_donut()
  Radardata = [
      { "brand": "kroger", "cheap": 4, "fresh": 3, "variety": 4, "friendly": 3 },
      { "brand": "costco", "cheap": 5, "fresh": 3, "variety": 4, "friendly": 4 },
      { "brand": "target", "cheap": 5, "fresh": 4, "variety": 4, "friendly": 3 },
      { "brand": "walmart", "cheap": 4, "fresh": 2, "variety": 3, "friendly": 4 }
  ]
  return render_template('store_ratings.html', data=data, Radardata=Radardata, current_city_state=current_city_state)

# Load top cities
@app.route('/top_cities')
def top_cities():
  top_cities_data = calc_top_cities()
  return render_template('top_cities.html', top_cities_data=top_cities_data)








# Command Line Input
@app.route('/', methods=['POST', 'GET'])
def execute_command():
  if request.method == 'POST':
    raw_input = request.form['command']
    raw_input_split = raw_input.split(' ') # split command and input
    
    if raw_input_split[0] == 'mkdir': # detect mkdir command
      response = mkdir_hd(raw_input_split)
      
    elif raw_input_split[0] == 'ls': # detect ls command
      if len(raw_input_split) == 1:
        raw_input_split = ['ls', '/']
        response = ls_hd(['ls', '?'])
      else:
      	response = ls_hd(raw_input_split)
      if not isinstance(response, str):
        return render_template('ls_display.html', children_display=response, parent_display=raw_input_split[1]) # list of tuples
      
    elif raw_input_split[0] == 'cat': # detect cat command
      response = cat_hd(raw_input_split)
      if not isinstance(response, str):
        return render_template('cat_display.html', blocks=response.to_html(justify='center').replace('<tr>', '<tr align="center">'), file_name=raw_input_split[1])
      
    elif raw_input_split[0] == 'rm': # detect rm command
      response = rm_hd(raw_input_split)
      
    elif raw_input_split[0] == 'put': # detect put command
      response = put_hd(raw_input_split)
    
    elif raw_input_split[0] == 'getPartitionLocations': # detect getPartitionLocations command
      response = getPartitionLocations_hd(raw_input_split)
      
    elif raw_input_split[0] == 'readPartition': # detect readPartition command
      response = readPartition_hd(raw_input_split)
      if not isinstance(response, str):
      	return render_template('cat_display.html', blocks=response.to_html(justify='center').replace('<tr>', '<tr align="center">'), file_name=raw_input_split[1], partition_num=raw_input_split[2])
    else:
      return render_template('cmd_main.html')
      
  return render_template('cmd_main.html', response=response)


# Load navigate.html on '/navigate' url load
@app.route('/navigate')
def load_navigate():
  current_dir = '/' # defaults to root
  child_dir, child_all = navigate_child(current_dir) # get child_dir and child_all
  return render_template('navigate.html', current_dir=current_dir, parent_dir=None, child_dir=child_dir, child_all=child_all)


## Main
if __name__ == "__main__":
    app.run()
