# 500px-fav-downloader
**Python web application to download your favorite pictures on 500px.**

Right now the app is just a small prototype made to run on localhost. You cannot change many settings, but when the proof of concept is done, I will improve on that side.

# Setup:

Install requirements
 
````
pip install -r requirements.txt
````

Create the config.ini file in config/ based on the config/config_example.ini file
 
Run the http server
````
python3 run.py
````

Create a bookmarklet based on the file `ressources/bookmarklet_save_image.js`

Go on 500px, browse picture and when you like one, click on the bookmarklet. It will save the image automatically.
