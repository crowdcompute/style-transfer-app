# Style Transfer CrowdCompute App using lengstrom/fast-style-transfer

The style transfer python library can be found on github.com/lengstrom/fast-style-transfer.

This app is running as an HTTP server. 

It gets images and styles as an input and returns a zip with the style transformed images.

## Build

While at the folder with the Dockerfile, run the below

-t flag tags the docker image with the name *style-transfer-app*

```
docker build -t style-transfer-app .
```

## Run

Docker image exposes port 3000. 

-p flag binds the port 3000 of the container to port 3000 on the host machine.

```
docker run -p 3000:3000 style-transfer-app
```

## Web app

Call `localhost:3000/style_transfer` to upload images.

Parameters:

**images** : The images you want to edit.

**styles** : The styles you want to edit the images.


Comma separate the styles you want to use.

Styles supported: la_muse,rain_princess,scream,udnie,wave,wreck