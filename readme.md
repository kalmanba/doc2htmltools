# Doc2html tools

The purpuse of this small tool is to make HTML files expored from Microsoft Word usable on an actual website.

## Functions
- Uploading the images from the exported HTML and connected folders onto a simple Laravel API endpoint. 
    - To set up a simple Laravel endpoint please check out [this](apiendpoint.md) page. 
- Replacing the original image with the new uploaded image
- Making the image responsive, so there isn't a y axis overflow. 
- Converting all the wierd MS Word encodings into something sesible 
- Hardcoded replace for `õ => ő` and `û => ű` to fix encoding issues with the Hunagrian languange.
- Removing the __Default__ MS  Word left indents so everything looks Ok on mobile as well.
    - There are two options. `-m` halves the margine values
    - On the other hand `-i` makes the negative text indent values double. Sometimes one works sometimes the other. Try and see.

## Usage 
```
$ doc2htmltools.py "/your/path/to/the/file" [-m][-i]
```
## Installation
Download the latest relase for your OS. Run the installer file (install.sh for Linux, install.exe for Windows). Restart your terminal and use the tools.

