# Talento Bot
This is a Trello bot that automates some tasks for the team management and has a dashboard for full visualization of the data.


### Motivation
The main goal is to help the management of [Talento](https://mte.org.br/talento/) partnerships by automating some tasks, like asking for updates or list the negotiation status. The team has a Trello Board to organize all the information and the bot simply fetches board's data from Trello's API.

### Technologies
##### Backend
 - [Django](https://www.djangoproject.com/)

##### Dashboard
 - [Bootstrap](https://getbootstrap.com/)

##### Database
 - [Postgres](https://www.postgresql.org/)

### Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

#### Prerequisites

- [Docker]("https://docs.docker.com/install/")
- [Docker Compose]("https://docs.docker.com/compose/install/")

#### Running
Create a `data.json` file in the project root folder with:
```json
{
    "token": "<token>",
    "key": "<key>",
    "board_id": "<board_id>",
    "api_url": "https://trello.api"
}
```
You can access the [Trello API Documentation](https://developers.trello.com/docs/api-introduction) to know better how to get those credentials.

Now run the server:
```shell
# configure initial setup and run the server
docker-compose up --build
```
Access `http://locahost:8001/admin` to see, create and edit models.
The dashboard is running in `http://localhost:8001`.



### License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT)
