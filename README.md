# Optimize your private Portfolio by using Modern Portfolio Theory (MPT)

This project computes the MPT Efficiency Frontier, that is the set of optimal portfolios that offer the highest expected return for a defined level of risk, for portfolios of Funds and ETFs by using data from the [Morningstar](www.morningstar.de) webpage.

![EF_Example](https://user-images.githubusercontent.com/21077042/95654896-7aeb9900-0b03-11eb-8156-91879e922a44.png)

## Background

When I was 27 years old, I was looking for ways to invest the money I earned during my PhD. Back then, I was young, unbound and didn't need the money for things other than my savings account. After getting the "hot tips" from family and friends, I attended [Theodoro Cocca's Asset Managment](https://www.jku.at/institut-fuer-betriebliche-finanzwirtschaft/ueber-uns/team/univ-prof-dr-teodoro-d-cocca/) class at JKU, where I discovered [Mondello's Finance Book](https://www.springer.com/de/book/9783658131982), which provides an excellent mathematical introduction to portfolio analysis, particularly [modern portfolio theory](https://www.investopedia.com/terms/m/modernportfoliotheory.asp) (MPT) developed by Markowitz.

MPT is usually used to construct portfolios of stocks that minimizes the risk for a given level of expected return. However, being a beginner in the market, I didnt want to buy a large number of individual stocks to achieve a good level of diversification. Thus I diversify my portfolio by using Funds and ETFs and optimize it by using MPT. 

## Usage

To aquire historical data without paying for access, I web scrape the charts provided on the [Morningstar website](www.morningstar.de). The actual optimization is done afterwards, using phython's [SciPy](https://www.scipy.org/). Thereafter the "MPT Efficiency Frontier" (set of optimal portfolios that offer the highest expected return for a defined level of risk) is computed and printed out. 

This project's aim is to provide a simple tool to investment beginners and a starting point for more sophisticated / detailed portfolio analysis.


Set the variables 

        start_date and end_date 
        
for the time frame you want to scrape the web data and set the list 

        fond_ids

to the Morningstar IDs of the Funds and ETFs you want to use in the analysis.


## Example

Coming Soon!
