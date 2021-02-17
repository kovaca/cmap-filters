# Colormap filter demo  
This repo contains a streamlit app demonstrating the use of feComponentTransfer SVG filter primitives to apply colormaps to rendered objects.  

To launch: 
```
streamlit run cmap_app.py
```

Or build an image and run with docker: 
```
docker build -f Dockerfile -t app:latest .
```

```
docker run -p 8501:8501 app:latest
```