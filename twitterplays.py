import twitter
import requests
from datetime import datetime, timezone
import time
import traceback
from io import BytesIO
import urllib
import json
import dateutil.parser
from threading import Thread

version = "v2.3.2"

# CHANGE THESE TO REFLECT YOUR SERVER CONFIGURATION - MUST BE ACCESSIBLE BY INDEX.HTML
pngFile = "current.png" # Location to save current frame (probably want this on your webserver)
tweetFile = "tweets.html" # Location to save most recent tweets (also want this on your webserver)

jsonFile = "https://screenshake.club/share/tpp" # Location of the JSON file containing relevant game data (if present)

profile_name = "screenshakes" # Twitter profile to pull image from

# Twitter API Keys - fill in with your own OAuth info
CONSUMERKEY=""
CONSUMERSECRET=""
ACCESSKEY=""
ACCESSSECRET=""

'''
Gets an API object and returns it
'''
def getAPI():
    api = twitter.Api(consumer_key=str(CONSUMERKEY),
                  consumer_secret=str(CONSUMERSECRET),
                  access_token_key=str(ACCESSKEY),
                  access_token_secret=str(ACCESSSECRET))
    return api

'''
Download and parse the latest game data file from Constantin
'''
def getJSONData():
    pressxtojson = urllib.request.urlopen(jsonFile)
    jsondata = json.loads(pressxtojson.read())
    pressxtojson.close()
    time = jsondata["LastInputTime"]
    time = dateutil.parser.parse(time)
    chosenInput = jsondata["LastInput"]
    inputCount = jsondata["ChosenInputCount"]
    return time, chosenInput, inputCount

'''
Load the most recent tweets and save them to an html file
'''
def updateTweets():
    while True:
        try:
            api = getAPI()
            lastTime, chosenInput, inputCount = getJSONData()

            results = api.GetSearch(
                raw_query="q=%40"+profile_name+"&src=typeahead_click&f=live&count=50")
                
            tweetstr = "<head><script> \n\
        // Set the date we're counting down to \n\
        var countDownDate = new Date(\""+lastTime.strftime("%m/%d/%Y %H:%M:%S UTC")+"\").getTime(); \n\
        \n\
        // Update the count down every 1 second \n\
        var x = setInterval(function() { \n\
        \n\
          // Get today's date and time \n\
          var now = new Date().getTime(); \n\
        \n\
          // Find the distance between now and the count down date \n\
         var distance = now - countDownDate; \n\
        \n\
          var seconds = Math.floor(distance / 1000); \n\
        \n\
          // Display the result in the element with id=\"demo\" \n\
          document.getElementById(\"demo\").innerHTML = seconds; \n\
        \n\
          // If the count down is finished, write some text \n\
          if (distance < -15) { \n\
            clearInterval(x); \n\
            document.getElementById(\"demo\").innerHTML = \"EXPIRED\"; \n\
          } \n\
        }, 1000); \n\
        </script></head><body>\n"

            counter = 0
            timesince = (datetime.now(timezone.utc)-lastTime).seconds
            inputStr = "NONE"
            if str(chosenInput) != "":
                inputStr = str(chosenInput)
            tweetstr += "<b>Time Since Press: </b>" + "<span id=\"demo\"> </span>" + "s (" + inputStr + ", " + str(inputCount) + " votes)<br><br>"
            for result in results:
                if counter > 9:
                    break
                status = api.GetStatus(result.id)
                if not status.text.startswith("RT @"):
                    text = status.text.replace("@"+profile_name, " ") # Hide the leading @ tag
                    author = status.user.name
                    tweettime = status.created_at
                    tweettime = datetime.strptime(tweettime,'%a %b %d %H:%M:%S +0000 %Y').strftime("%m/%d/%Y, %H:%M:%S")
                
                    tweetstr += text
                    tweetstr += "<span style=\"color:grey;\"><br>— <b>"
                    tweetstr += author + "</b><small> "
                    tweetstr += tweettime
                    tweetstr += " UTC</small></span><br><br>"

                    counter += 1
            timestamp = datetime.now().strftime('%d-%b-%Y %H-%M-%S')
            print(timestamp+" Updating tweets...")
            tweetfile = open(tweetFile, "wb")
            tweetfile.write(tweetstr.encode('utf-8'))
            tweetfile.close()
            
            lastTime, chosenInput, inputCount = getJSONData()
            timesince = (datetime.now(timezone.utc)-lastTime).seconds
            if timesince < 4:
                print("Tweets in sync...")
                time.sleep(15)
            else:
                print("Tweets not in sync, realigning...")
                time.sleep(14)
        except twitter.error.TwitterError as err: # Completely ignore API errors for unattended running
            print(err)
        except Exception as exc: # Print other errors, but ignore them. Again, for unattended running
            print(traceback.format_exc())
            print(exc)

'''
Load the most recent profile picture and save it to a png file
'''
def updateImage():
    while True: # Endlessly loop
        try:
            api = getAPI()
            pic_url = api.GetUser(screen_name=profile_name).profile_image_url
            pic_url = pic_url.split("_normal")[0]
            timestamp = datetime.now().strftime('%d-%b-%Y %H-%M-%S')
            print(timestamp+" Updating image...")
            with open(pngFile, "wb") as handle:
                response = requests.get(pic_url+".png", stream=True)
                if not response.ok:
                    print(response)

                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)          
            handle.close()
            time.sleep(5)
        except twitter.error.TwitterError as err: # Completely ignore API errors for unattended running
            print(err)
        except Exception as exc: # Print other errors, but ignore them. Again, for unattended running
            print(traceback.format_exc())
            print(exc)

def main():
    print("twitterplays "+version+" by LeifEricson")

    # Due to API limitations, pfp is refreshed every 5s and the tweets every 15s
    # A new API object is created in case of random api errors, since script runs unattended
    t1 = Thread(target = updateTweets, args = ())
    t2 = Thread(target = updateImage, args = ())
    t1.start()
    t2.start()

if __name__ == "__main__":
    main()
