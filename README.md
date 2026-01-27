# Syrinx

<img src="http://syrinx.site/assets/logo_syrinx.png" width="70" alt="logo of singing bird with pan flute as vocal chords">


> *Spreadsheet to website*

[website](https://syrinx.site)

Simple static site generator in python


## Deployment options

### DO App Platform + "Pull"

This is the simplest option. Commit the `dist` directory with generated html files and assets to your github repository. Next create a DigitalOcean App Platform "App", and point it to your github repository. Configure it to find the files in the `dist` directory. 

### DO App Platform + "Push"

This gives you more control over both the server environment as well as the deployment pipeline, but it is more involved. You'd include two files in your repository: a `Dockerfile` specifying the server, and a DigitalOcean App specification in yaml. In the deployment pipeline you then build the docker container and push it to a central registry. In the app specification you'd list the container registry address, and using the commandline tool `doctl` you tell DigitalOcean to schedule a deployment from the new container.