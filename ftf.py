import folium.plugins
import pycaching
import folium
from colour import Color
from pycaching.geocaching import SortOrder
import math
import collections
import re
import datetime
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
import random

ftf = {}
start_coords = (52.822945, -1.060705)
map = folium.Map(location=start_coords)
gradient = list(Color("green").range_to(Color("red"),50))
gradient += [gradient[-1]]

def load_caches(number):
    global ftf
    geocaching = pycaching.login()

    for cache in geocaching.search(pycaching.Point(start_coords), number, sort_by=SortOrder.distance):
        logs = list(cache.load_logbook())[::-1]
        published = -1
        first = -1
        log_ftfs = []

        for log in logs:
            if log.type == pycaching.log.Type.publish_listing and published == -1:
                published = log.visited
            elif log.type == pycaching.log.Type.found_it and published != -1:
                text = log.text.replace("}","{").replace(")","(").replace("]","[").replace("/","").replace("<p>","")
                s = re.search("(\S+)FTF", text)
                if s != None:
                    if text.find(s.group(1)+"FTF"+''.join(list(reversed(s.group(1))))) != -1 or text.find(s.group(1)+"FTF"+s.group(1)) != -1:
                        log_ftfs += [log.author]
                if first == -1:
                    first = [log.visited, log.author]
        
        if log_ftfs == [] and first != -1:
            log_ftfs = [first[1]]
            
        if log_ftfs != []:
            days = (first[0]-published).days
            ftf[cache.wp] = ((log_ftfs, 
                days, 
                published, 
                cache.name, 
                tuple(cache.location)[0:2],))

            with open("ftf.txt","a",encoding="utf-8") as file:
                file.write(cache.wp+":"+str(list(ftf[cache.wp])))
                file.write('\n')     

def read_caches(file):
    global ftf
    lines = open(f"{file}.txt","r", encoding="utf-8").read().splitlines()
    for line in lines:
        line = [line[0:line.index(":")],line[line.index(":")+1:]]
        line[1] = eval(line[1])
        ftf[line[0]] = line[1]

def map_gen():
    global ftf
    global feature_groups
    global feature_groups_sorted
    ftf = collections.OrderedDict(sorted(ftf.items(), key=lambda item: item[1][1], reverse=True))
    feature_groups = {}
    feature_groups_sorted = {}

    mean = sum([i[1] for i in ftf.values()])/len(ftf)
    variance = (sum([i[1]**2 for i in ftf.values()])/len(ftf))-(mean**2)
    standard_deviation = math.sqrt(variance)
    upper = mean+(2*standard_deviation)
    lower = mean-(2*standard_deviation)

    maximum = max([i[1] for i in ftf.values() if i[1] <= upper])
    minimum = min([i[1] for i in ftf.values() if i[1] >= lower])

    callback = ('function (row) {'
                    'const weight = row[7];'
                    'var circle = L.circle(new L.LatLng(row[0], row[1]), {color: row[8], radius: 50+(5*weight), fill: true, fillOpacity: 0.6});'
                    '''circle.bindPopup(`<a href="https://coord.info/${row[6]}" target="_blank">${row[4]} day(s)</a>
                    <br>FTFer(s): ${row[5]}`);'''
                    'circle.bindTooltip(`${row[6]} <br> ${row[2]} <br> Published: ${row[3]}`);'
                    'return circle};')

    
    for i in ftf:
        for person in ftf[i][0]:
            person_count = f"{person}: {len([i for i in ftf if person in ftf[i][0]])}"
            feature_groups[person_count] = feature_groups.get(person_count,folium.FeatureGroup(name=person_count))
            folium.Circle((ftf[i][4][0],ftf[i][4][1]), radius=50+(5*[math.floor(((ftf[i][1]-minimum)/(maximum-minimum))*50),100][ftf[i][1]>upper]), 
                        fill=True, fill_opacity=0.6, color=[gradient[math.floor((([ftf[i][1],0][ftf[i][1]>upper]-minimum)/(maximum-minimum))*50)].hex_l,Color("cyan").hex_l][ftf[i][1]>upper],
                        tooltip=f'{i}<br>{ftf[i][3]}<br> Published: {ftf[i][2].strftime("%d/%m/%Y")}',
                        popup=f'''<a href=https://coord.info/{i} target="_blank">{str(ftf[i][1])} days</a>
                        <br>FTFer(s): {', '.join(ftf[i][0])}''').add_to(feature_groups[person_count])
    
    for group in feature_groups:
        feature_groups_sorted[group] = [feature_groups[group],int(group.split(': ')[1])]
    feature_groups_sorted = collections.OrderedDict(sorted(feature_groups_sorted.items(), key=lambda item: item[1][1], reverse=True))

    group_tree = {
        "label": "Select all",
        "select_all_checkbox": "Un/select all",
        "children": [
            {"label": person, "layer": feature_groups_sorted[person][0]} for person in feature_groups_sorted
        ]
    }

    '''
    map.add_child(FastMarkerCluster([[ftf[i][4][0], 
                                      ftf[i][4][1], 
                                      ftf[i][3], 
                                      ftf[i][2].strftime("%d/%m/%Y"), 
                                      ftf[i][1], 
                                      ', '.join(ftf[i][0]), 
                                      i, 
                                      [math.floor(((ftf[i][1]-minimum)/(maximum-minimum))*50),100][ftf[i][1]>upper], 
                                      [gradient[math.floor((([ftf[i][1],0][ftf[i][1]>upper]-minimum)/(maximum-minimum))*50)].hex_l,Color("cyan").hex_l][ftf[i][1]>upper]] 
                                      for i in ftf], callback=callback))
    '''

    for person in feature_groups_sorted:
        feature_groups_sorted[person][0].add_to(map)
    folium.plugins.TreeLayerControl(collapsed=False, overlay_tree=group_tree).add_to(map)
    map.save("map.html")

read_caches("ftf_home")
map_gen()