# OverStreet


Comics classification code that uses a mix of image algorithms and ML to identify comic archives to their corresponding ComicVine entries and file them.

### System architecture

![Data Pipeline](/diagrams/data-pipeline.png)



## Command Line Scripts

Python services are primarily implemented as set of command line scripts:

| Script   | Description                                       |
|-------------|------------------------------------------------------------------------------------------------|
| cv-update   | Download latest updates from ComicVine to a set directory                                      | 
| db-update   | Walk ComicVine 'source of truth' system, rebuilding the database used for image classification | 
| cb-classify | Walk a directory containing comics and generate a JSON file outlining ML matches for later use | 


### Launch Configuration ###

```
    {
        "name": "on-deck",
        "type": "python",
        "request": "launch",
        "program": "scripts/on-deck.py",
        "env" : {
            "UNRAR_LIB_PATH" : "C:\\Program Files (x86)\\UnrarDLL\\x64\\UnRAR64.dll"
        },
        "args" : [ "--dir", "f:/comics/unfiled"],
        "console": "integratedTerminal"
    },
```