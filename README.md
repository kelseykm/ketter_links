# **Ketter Links**

* Ketter Links is a webscraping application that scrapes free TV Series download sites, gets the specified links and writes them to a urls.txt file.
* It uses requests, beautiful soup and selenium.
* It is named after ketter, the asynchronous http file downloader, because its output (a urls.txt) is ketter's input (also a urls.txt); and so with the two programs can be used in combination. You can find ketter here: https://github.com/kelseykm/ketter
* For now, the only sites implemented are: www.thenetnaija.com, www.lightdl.xyz and o2tvseries.com. They should be enough, but feel free to add others!

### Installing depends 
To install the dependencies, ```cd``` into the directory with the requirements.txt run:
```
pip3 install -r requirements.txt
```

#### Usage

* For help, run the main.py file with the option "--help"
```
./main.py --help
```

* Example:
```
ketter_links/main.py 'https://o2tvseries.com/The-100-9/Season-04/' '^(episode )(05)$'
```
* The regex will be a regex of the text of the link of the episodes whose links you wish to scrape. In the example above, if you go to the url provided, you will see the links to the episodes named "Episode XX". So the regex will reflect the link names. In the above example, I only want the episode whose link
text is "Episode 05"

* Note that the regex you supply on the commandline option will be compiled with the re.IGNORECASE flag, so you need not worry yourself with the case as you write the regex.

* You may create a symbolic link to the main.py file and put the link in your PATH so as to make running Ketter Links easier.

