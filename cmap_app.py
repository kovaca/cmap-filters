import numpy as np 
import streamlit as st 
import streamlit.components.v1 as components
from colorspacious import cspace_converter
from matplotlib.colors import LinearSegmentedColormap, rgb2hex, hex2color, ListedColormap
import os
import json

st.title("Colormap filter demo")
st.write("""This app cross references a catalogue of my favorite colormaps, 
  and implements a simple svg filter argument to apply a colormap to a Leaflet map layer.
  Filter component transfer tables remap grayscale source colors to colormap values. YMMV for rgb inputs.
  The sidebar shows color interpolations in various common colorspaces.""")

def colorfunc(color_1, color_2, cspace="CAM02-UCS",N=256):
    j = [hex2color(i) for i in [color_1,color_2]]
    k = cspace_converter("sRGB1",cspace)(j)
    l = cspace_converter(cspace, "sRGB1")(np.linspace(k[0],k[1],N))
    g = (l.clip(0,1) * 255.0).round().astype(np.uint8)
    return np.repeat(g[np.newaxis, :, :],30, axis=0)

def cmap_hexstring(l):
    c = ['#'+l[i:i+6] for i in range(0, len(l), 6)]
    cmp = LinearSegmentedColormap.from_list('cmp',c)
    return cmp

cm = []
for root, dirs, files in os.walk('collections'):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root, file)) as fp:
                cmap_collection = json.load(fp)
                for c in cmap_collection["contents"]:
                    cm.append(c)

colormap_names = [i['name'] for i in cm]
cname = st.selectbox("Pick a colormap. Scroll and select, or start typing and the list will filter.",colormap_names)

l = list(filter(lambda c: c['name'] == cname, cm))
color_pick = l[0]["colors"]
cmap = cmap_hexstring(color_pick)

a = cmap(np.linspace(0,1,41))
feFuncR = np.array2string(a[:,0], precision=5,floatmode="fixed", separator=' ')[1:-1].replace("\n","")
feFuncG = np.array2string(a[:,1], precision=5,floatmode="fixed", separator=' ')[1:-1].replace("\n","")
feFuncB = np.array2string(a[:,2], precision=5,floatmode="fixed", separator=' ')[1:-1].replace("\n","")


placeholder = st.empty()

col1, col2, col3 = st.beta_columns(3)
with col1:
  lat = st.number_input("Lat", value=51.50)
with col2:
  lng = st.number_input("Lng", value=-0.09)
with col3:
  zoom = st.number_input("zoom",value=13)

tile_cache = st.text_input('Privide your own {z}/{y}/{x} tile cache', 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}')
attrib = st.text_input('Add proper map attribution for good measure', 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')

leafy_map = f"""<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
   integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
   crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
   integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
   crossorigin=""></script>
  </head>
  <body>
  <figure class=demo>
  <div class="band filter"></div>
   <div id="mapid" style="width: 600px; height: 400px; position: relative; outline: none;">
   </div> 
  <script>
    var mymap = L.map('mapid').setView([{lat}, {lng}], {zoom});
    L.tileLayer('{tile_cache}', 
    {{
	  attribution: '{attrib}'
    }}).addTo(mymap);
  </script>
  
  <style>
  .demo div {{ display: block }}
  .demo {{display:flex; flex-direction:column; max-width: 100%}}
  .demo span {{font:13px/20px var(--sans-serif)}}
  .demo div.band {{margin-bottom:1%;padding-bottom:4%;background:linear-gradient(90deg, #000, #fff)}}
  .filter  {{filter: url(#scale1)}}
  .leaflet-tile-container {{filter: url(#scale1)}}
  </style>
  <style>.filter {{filter: url(#scale1)}}</style>
  <svg width=100 height=10>
<filter id="scale1" color-interpolation-filters="sRGB">
  <feComponentTransfer>
  <feFuncR type="table" tableValues="{feFuncR}"></feFuncR>
  <feFuncG type="table" tableValues="{feFuncG}"></feFuncG>
  <feFuncB type="table" tableValues="{feFuncB}"></feFuncB>
</feComponentTransfer>
</filter>
  </svg>
  </figure>
  <body>"""


#"CAM02-SCD","CAM02-LCD",'XYZ100'
spaces = ["CAM02-UCS",'sRGB1','CIELab','sRGB1-linear','xyY1','JCh','JMH','QCH','Qsh','CIELCh']

st.sidebar.title('2-color interpolations')
st.sidebar.write("""Pick gradient start and end colors to compare interpolation through various colorspaces. 
  Colors will update when colormaps are selected in the main section.""")
c1 = rgb2hex(cmap(0.0))
color1 = st.sidebar.color_picker('Start Color', c1)
st.sidebar.write(color1)
c2 = rgb2hex(cmap(1.0))
color2 = st.sidebar.color_picker('End Color', c2)
st.sidebar.write(color2)

with placeholder.beta_container():
  components.html(leafy_map,height=450)

st.sidebar.header('Color interpolations:')
st.sidebar.image(np.vstack([colorfunc(color1,color2,cspace=i) for i in spaces]),clamp=True)
st.sidebar.subheader('Colorspaces used above:')
st.sidebar.write(spaces)