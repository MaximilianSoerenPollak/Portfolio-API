<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<h2 align="center">NOTE: This repo is archived and not under active development anynmore. </h2>
<div align="center">

[![GPL3.0 License][license-shield]][license-url]

</div>


<h3 align="center">Portfolio-API</h3>

  <p align="center">
    This is a project used to combining all my data engineering knowledge.
    <br />
    This project is a Postgres DB with an API middleware and a Streamlit frontend.
    <br />
    It is used to track portfolio performance in comparision to set goals, so I can easier track it.
    <br />
    <br />
    <a href="https://github.com/maximiliansoerenpollak/portfolio-api/issues">Report Bug</a>
    ·
    <a href="https://github.com/maximiliansoerenpollak/portfolio-api/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation-without-docker">Installation without docker</a></li>
        <li><a href="#installation-with-docker">Installation with docker</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project started as a capstone project for [Pipeline Academy](https://www.dataengineering.academy) but since it is a project I build for personal use I continue to develop it.
<br />
**So let it be clear that this is a slow work in progress and I will work on it still although slowly.**

<br />
This portfolio tracker is consistent of three individual parts.
 
 * Data Acquisition
 * API
 * Streamlit frontend

This was a concious choice so in the future I can come back, improve or re-build any of these three parts without affecting the other two.
The *data acquisition* is done by a python script that grabs the current tickers from the stock exchanges and then gathers the data on them on yahoo finance via a library.
The API is acting as the middleware and is build with help of the amazing fastAPI framework.
The streamlit frontend simply allows you to interact with the API easier and it adds some nice visuals.
<br />
The project allows you to filter all available stocks in the database as well as add your own (if the ones you have in your portfolio are not in the DB yet).
It also is possible to create or view your portfolios (you can make an account easily from the frontend). You also can add stocks from the database to your portfolio.
It then shows you some nice overall statistics as well as calculates some simple return %. 




<p align="right">(<a href="#top">back to top</a>)</p>





### Built With

* [Python](https://www.python.org/)
* [fastAPI](https://fastapi.tiangolo.com/)
* [Streamlit](https://streamlit.io/)
* [Postgres](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)
* [Digital Ocean](https://www.digitalocean.com/)
* [Yahoo_query](https://yahooquery.dpguthrie.com/)
* [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt)
* [Pandas](https://pandas.pydata.org/)
* [Plotly](https://plotly.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how can get the whole thing up and running on your *local* machine.
To get a local copy up and running follow these simple example steps.

### Prerequisites
 * [Python](www.python.org)
 * [Docker](www.docker.com)
 * [Docker-Compose](https://docs.docker.com/compose)
 * [Postgres](https://www.postgresql.org)
 * Python virtualenv
   ```sh
   pip install virtualenv 
   ```

### Installation without Docker
1. Clone the repo of the branch you want.
   ```sh
   git clone https://github.com/maximiliansoerenpollak/portfolio-api.git
   ```

2. If you want the non-dockerized version then you use the `main` branch.  


3. Open a terminal and navigate to the folder where you cloned the repo and make a virtual environment.
   ```sh
      cd place/you/cloned/repo/portfolio-api
   ```
   Activate and install all requirements
   
   ```sh
      python3 -m venv name_of_virtualenv
      source name_of_virtualenv/bin/activate
      pip -r install requirements.txt
   ```
   Now you should have all requirements installed that are needed for the project.

4. Make a .env file in the main directory with all of your credentials  
   If you don't know how to make a random string for the JWT_SECRET_KEY  
   ```sh
    openssl rand -hex 24 #you can make this any digit length, just change the 24.
   ```
   Then fill in the .env file with your own Postgres credentials and the key you just generated.
   ```
      POSTGRES_USERNAME=
      POSTGRES_PASSWORD=
      DATABASE_HOSTNAME=
      DATABASE_PORT=
      DATABASE_NAME=
      JWT_SECRET_KEY=
      ACCESS_TOKEN_EXPIRE=60
      ALGORITHM=HS256
   ```
5. We also have to upgrade the database to the current schema. We can do that with a simple terminal command.
   ```sh 
      alembic upgrade head
   ```
   That was it already, our database should now be on the current schema and any data ingestion should work.

6. Now you just have to activate the API.
   ```sh
      uvicorn api.main:app  
   ```
   And in another terminal window (also in the project folder) the frontend
   ```sh
      streamlit run frontend/frontend.py
   ```
   Now you should be able to just go to localhost:8501 (for the frontend) and localhost:8000 (for the API)  
   **Please note: I have not yet integrated the data acquisition. It works but it's not callable in an easy way.**
   


### Installation with docker  
1. Clone the repo of the branch you want.
   ```sh
   git clone https://github.com/maximiliansoerenpollak/portfolio-api.git
   ```

2. Make sure you navigate to the project folder and checkout the `unit-tests` branch.

   ```sh
      cd place/you/cloned/repo/portfolio-api
      git checkout unit-tests
   ```
3. Create two .env files. One in the `api` folder the other inside of the `frontend` folder.
   ```sh
      # The .env in api
      POSTGRES_USERNAME=
      POSTGRES_PASSWORD=
      DATABASE_HOSTNAME=
      DATABASE_PORT=
      DATABASE_NAME=
      JWT_SECRET_KEY=
      ACCESS_TOKEN_EXPIRE=60
      ALGORITHM=HS256
   ```
   ```sh
      # The .env in  frontend
      API_URL=localhost:8000 # if you have not change the port this should be fine
   ```
   If you want to rename the containers just do so in the docker-compose file.
   Also make sure all the paths in the docker-compose file are correct (for the .env files)


5. Build the docker images

   ```sh
     docker-compose build 
     # Then once build just do 
     docker-compose up      
   ```
6. Now we just need to run the albemic command to make sure our database is configured correctly (with the right tables)
   Run this command inside the docker image you just created
   ```sh 
      docker exec <name_of_container> alembic upgrade head
   ```
   It now should get the everything up to date to the current database schema.
   You now can use the project.  
   **Please note: The data Acuqistion part works but is not integrated into the project yet.**

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

If want to use the project locally then you have to make the data acquisition work before. As there won't be any data in your database.  
**However** for right now I still have the API + a database hosted on Digital Ocean. The route to the API is 

`api-psosi.ondigitalocean.app`

The API is connected to a database that has over 5000 Stocks in it currently (collected with the data acquisition found in this project).  
_Please feel free to try the API out. If you need any help on whats possible please just take a look at either one of the Documentations:_ 
 * [Documentation-Style1](api-psosi.ondigitalocean.app/docs)
 * [Documentation-Style2](api-psosi.ondigitalocean.app/redoc)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Initialize Repo
- [x] Working MVP (without data acquistition)
- [ ] Put project in the Cloud
    - [x] Put database in the Cloud
    - [x] Put API in the Cloud
    - [ ] Put frontend in the Cloud
- [x] Implement Unit-Tests
- [ ] Fix data acquisition
- [ ] Fix the frontend
- [ ] Implement data quality (via great_expectations)
- [ ] Add stock exchanges where data is gathered
    - [ ] Add Euronext
    - [ ] Add Hang Seng 

    
See the [open issues](https://github.com/maximiliansoerenpollak/portfolio-api/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GPL3.0 License. See `LICENSE.md` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Maximilain Soeren Pollak - pollakmaximilian@gmail.com

Project Link: [https://github.com/maximiliansoerenpollak/portfolio-api](https://github.com/maximiliansoerenpollak/portfolio-api)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Sanjeev Thiyagarajan](https://www.youtube.com/channel/UC2sYgV-NV6S5_-pqLGChoNQ)
* All my colleagues from the Data Engineering Bootcamp (Pipeline Academy)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-shield]: https://img.shields.io/github/license/maximiliansoerenpollak/portfolio-api
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png

