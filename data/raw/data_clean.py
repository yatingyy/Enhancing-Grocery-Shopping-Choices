import pandas as pd
from geopy.geocoders import Nominatim

kroger = pd.read_csv('kroger_store.csv')
costco = pd.read_csv('costco_store.csv')
target = pd.read_csv('target.csv', encoding='latin-1')
walmart = pd.read_csv('Walmart_Locations.csv')

kroger = kroger[['address', 'city', 'state', 'postal_code', 'latitude', 'longitude']]
kroger['brand'] = 'kroger'
kroger['cheap'] = 4
kroger['fresh'] = 3
kroger['variety'] = 4
kroger['friendly'] = 3

costco = costco[['address_1', 'city', 'state', 'postal_code', 'latitude', 'longitude']]
costco.columns = ['address', 'city', 'state', 'postal_code', 'latitude', 'longitude']
costco['brand'] = 'costco'
costco['cheap'] = 5
costco['fresh'] = 3
costco['variety'] = 4
costco['friendly'] = 4

target = target[['Address.AddressLine1', 'Address.City', 'Address.Subdivision', 'Address.PostalCode', 'Address.Latitude', 'Address.Longitude']]
target.columns = ['address', 'city', 'state', 'postal_code', 'latitude', 'longitude']
target['brand'] = 'target'
target['cheap'] = 5
target['fresh'] = 4
target['variety'] = 4
target['friendly'] = 3

walmart = walmart[['Address', 'City_and_State', 'Zipcode']]
walmart = pd.concat([walmart[['Address']], walmart['City_and_State'].str.split(', ', expand=True), walmart[['Zipcode']]], axis=1)
walmart.columns = ['address', 'city', 'state', 'postal_code']
walmart['latitude'] = None
walmart['longitude'] = None
walmart['brand'] = 'walmart'
walmart['cheap'] = 4
walmart['fresh'] = 2
walmart['variety'] = 3
walmart['friendly'] = 4


stores_all = pd.concat([kroger, costco, target, walmart])
stores_all['city'] = stores_all['city'].str.title()+', '+stores_all['state']

all_cities = stores_all['city'].str.title()+', '+stores_all['state']
all_cities = all_cities.sort_values(ascending=True).unique()


walmart['full_address'] = walmart['address'].astype(str) + ', ' + walmart['city'].astype(str) + ', ' + walmart['state']
loc = Nominatim(user_agent="Geopy Library")
for i in walmart.index: 
    try: 
        getLoc = loc.geocode(walmart.loc[i,'full_address'])
        walmart.loc[i,'latitude'] = getLoc.latitude
        walmart.loc[i,'longitude'] = getLoc.longitude
    except: 
        continue
      
stores_new = pd.read_csv('data/stores_new.csv')
stores_new['city_state'] = stores_new['city']+', '+stores_new['state']
stores_new.to_csv('stores_new.csv', index=False)
all_cities = stores_new['city_state'].sort_values(ascending=True).unique()
pd.DataFrame(all_cities, columns=['city_name']).to_csv('all_cities.csv', index=False)





stores_new = pd.read_csv('data/stores_new.csv')
all_cities = stores_new['city_state'].sort_values(ascending=True).unique()
pd.DataFrame(all_cities, columns=['city_name']).to_csv('all_cities.csv', index=False)