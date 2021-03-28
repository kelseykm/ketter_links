# **Ketter Links**

* Ketter Links is a webscraping application that scrapes free TV Series download sites, gets the specified links and writes them to a urls.txt file.
* You may also search for series using the program.
* It uses requests, beautiful soup and selenium.
* It is named after ketter, the asynchronous http file downloader, because its output (a urls.txt) is ketter's input (also a urls.txt); and so the two programs can be used in combination. You can find ketter here: https://github.com/kelseykm/ketter
* For now, the only sites implemented are: www.thenetnaija.com, www.lightdl.xyz and o2tvseries.com. They should be enough, but feel free to add others!

### Installing depends 
To install the dependencies, ```cd``` into the directory with the requirements.txt and run:
```
pip3 install -r requirements.txt
```

#### Usage

* For help, run the main.py file with the option "--help"
```
./main.py --help
```

* You may create a symbolic link to the main.py file and put the link in your PATH so as to make running Ketter Links easier.
