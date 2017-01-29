ContentBox
==========

Open Scalable Content Delivery project

# Project general objective

Distribution of social and virtual content with an open and collaborative educational environment, available
to communities around the world in one place, with a standard format and quality.

* Repository and UI to store and distribute content in a scalable, simple and consistent way
* Metadata to organize and discover content through search
* Sign-in and subscription s to particular content
* Content Update process, and user alerts
* Metrics of content usage and behaviour User and content Admin: accounts and permissions
* Web Mobile Friendly (Tablets and CellPhones)
* General concept of boxes of content.

# General Structure Features

Users (feature options)

* Google Sign-in
* Boxes subscription
* Search Boxes
* Friendly Boxes urls

Manage (feature options)

* Admin site for managing
    * Boxes
    * FAQs
    * Term/conditions
* Roles in admin site. Content creator and super-admin
* Responsive admin site
* Whitelist login with csv import (invitations model)
* Global configurations
* Translation ready


# Prototype
[Testing Portal](https://scalable-content-delivery-test.appspot.com/)
You can validate the model using this test portal. (Remember that this website is into a test instance)

# Dependencies

```bash
pip install -r requirements.txt -t third_party/
```

# Install config

### Localhost testing
* Create app in Cloud Console. [https://console.developers.google.com/](https://console.developers.google.com/)
* In APIs & auth -> APIs Enable Google+ API.
* In APIs & auth -> Credentials Create an OAuth ID and an API Access
* Visit [http://localhost:8000/](http://localhost:8000/) (or the corresponding admin port) and enter the datastore 
viewer. Select the entity kind config_siteconfiguration edit the entity listed, copy the client id, client secret, 
and API key from the previous step and save.
* Go back to [http://localhost:8080/](http://localhost:8080/) and sign in.
* Go back to the datastore viewer, select the entity kind `auth_user`, edit your user and make yourself admin by checking 
`is staff` and `is superuser` and saving. Now you can access the admin site in [http://localhost:8080/admin](http://localhost:8080/admin).

More details about the project and support [http://google.github.io/contentbox/](http://google.github.io/contentbox/)
You can visit this website [contentbox.info](https://sites.google.com/site/contentboxcommunity/) for more installation details
