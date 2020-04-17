<h1 align="center">Trading Bot</h1>

## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)


## About The Project

Primarily functioning as a back-testing application, this app helps you test trading algorithms using a paper trading platform, Selenium is currently used to scrap the top gainers stock data.

### Built With

* []() Selenium
* []() Alpaca Python API
* []() Chrome Driver

### Prerequisites

Install the following pip packages.

* Selenium
```sh
pip install selenium
```
* alpaca-trade-api-python
```sh
pip3 install alpaca-trade-api
```
### Installation
 
1. Clone the repo
```sh
git clone https://github.com/orlovcs/Trading-Bot.git
```

## Usage

Rename and input your API keys into APIKeys.py.

Run main.py.
```sh
python3.7 main.py
```
### Overnight Hold

Currently only the Overnight Hold is available, this strategy looks back a specified amount of days, for each day it will request volume and price bars for a certain amount of stocks. For each applicable stock a rating will be calculated using the normalized momentum of the price changes and standard deviations in volume over the last day. Stocks will then be bought on market close and sold immediately on market open the day after being held overnight.

### AAPL Buy Open Sell Close

An ingenious strategy which takes a specified amount of initial cash and a back-testing window and then proceeds to buy the maximum amount of AAPL stocks it can on market open and sell them all off on market close for each day.

## Todo

See [open issues](https://github.com/orlovcs/Trading-Bot/issues).


## License

Distributed under the GPL3 License.

## Acknowledgements

* []() Alpaca Python API for the Overnight Hold strategy




