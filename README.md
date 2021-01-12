# twitterpokemon-feed
Script that updates the TwitterPlaysPokemon feed site at https://leif.gg/tpp/new

Note: The script ignores all errors, which is pretty bad practice. However, it can run unattended for long periods (which is perfect for this application.)

## Usage
1. Download source here: https://github.com/EBLeifEricson/twitterpokemon-feed/archive/main.zip
2. Paste OAuth key info into twitterplays.py
3. Edit the "output_image" variable to choose where to save the image file url
4. Edit the "url" variable in index.html to reflect the same image location
3. Run "runntpp.sh" file if on Linux, "runtpp.bat" if on Windows (this is to prevent crashes when running unattended)

Script requires Python 3.x with the python-twitter package
