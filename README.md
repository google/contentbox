ContentBox
==========

Open Scalable Content Deliver project

# Project general objective

Make social content produced available to communities worldwide in one place, with a standard format and quality level

* Repository and UI to store and distribute content in a scalable, simple and consistent way
* Metadata to organize and discover content through search
* Sign-in and subscription s to particular content
* Content Update process, and user alerts
* Metrics of content usage and behaviour User and content Admin: accounts and permissions

# General Structure Features

Manage (feature options)

* Admin site for managing
    * Boxes
    * FAQs
    * Term&conditions
* Roles in admin site. Content creator and super-admin
* Responsive admin site
* Whitelist login with csv import
* Global configurations
* Translation ready

Users (feature options)

* Google Sign-in
* Boxes subscription
* Search Boxes
* Friendly Boxes urls

# Prototype
[Testing Portal](https://scalable-content-delivery-test.appspot.com/)
[Stable Portal, without drive integration](http://scalable-content-delivery.appspot.com/)

# Dependencies

pip install -r requirements.txt -t third_party/

# Install config

### Localhost testing
* Create app in Cloud Console. [https://console.developers.google.com/](https://console.developers.google.com/)
* In APIs & auth -> APIs Enable Google+ API.
* In APIs & auth -> Credentials Create an OAuth ID and an API Access
* Visit [http://localhost:8000/](http://localhost:8000/) (or the corresponding admin port) and enter the datastore viewer. Select the entity kind config_siteconfiguration edit the entity listed, copy the client id, client secret, and API key from the previous step and save.
* Go back to [http://localhost:8080/](http://localhost:8080/) and sign in.
* Go back to the datastore viewer, select the entity kind auth_user, edit your user and make you admin checking “is staff” and “is superuser” and saving. Now you can access the admin site in [http://localhost:8080/admin](http://localhost:8080/admin).