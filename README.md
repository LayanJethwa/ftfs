
# FTF (**F**irst **T**o **F**ind) map
This project is a data visualisation, that shows the time taken for an FTF in geocaches around my area.

I have used LeafletJS mapping with the Folium Python module. The map is in the index.html file.


## Demo

https://layanjethwa.github.io/ftfs/


## Screenshots

![App Screenshot](https://github.com/LayanJethwa/ftfs/blob/main/image.png)


## What does this mean?

Geocaching is a worldwide game, where people attempt to find hidden containers. It is similar to a scavenger hunt. When you find a geocache, you put your name on the logbook, and can log it online.

Some people compete to be the first to find these geocaches as soon as they are published - this map displays the time taken between a geocache being published, and the FTF being claimed.
## Features

- Nodes marking geocaches, coloured and sized by time
    - A darker colour (and bigger circle) indicates a longer time
    - Light blue circles are outliers from the main dataset, which have an especially long time between publication and FTF
- Filterable list of geocachers, ordered by their number of FTFs in the dataset
- Can identify where people have claimed joint FTFs
- Hover over a node to see the GC code, cache name, and publication date
- Click on a node to see the time between publication and FTF (with a link to the cache page), and who claimed the FTF
