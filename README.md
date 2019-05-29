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

Feed the app with images using a POST HTTP request.

Call `localhost:3000/style_transfer` to upload images and select styles using:

Content-Disposition: form-data; **name="images"**
Content-Type: image/jpeg

Content-Disposition: form-data; **name="styles"**