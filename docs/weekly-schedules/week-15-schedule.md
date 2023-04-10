# **2023 Week 15 Schedule**

<img src="/images/week-current-300-120px.png" alt="This week is CURRENT">

### This was generated on **2023/03/31** and has **14** events from **2023/04/11** to **2023/04/11**. 

!!! info 
    This month there are events which I'm not trading because the trading pairs aren't available on [Blackbull Markets](https://blackbullmarkets.com/en/) i.e. **USDNOK** & **USDSEK**. 

      - I didn't realize this until after paying for a server in New Jersey which is close to where the broker's server is. 
      - Originally I planned on using [fpmarkets](https://www.fpmarkets.com/) because according to [this](https://offbeatforex.com/forex-brokers-for-trading-news/) article where they tested brokers for order execution speed and spreads, and fpmarkets was one of the best.
          - However, because of the current global banking collapse, I decided to go with **Blackbull Markets** who are regulated in New Zealand meaning that their client funds are kept with NZ banks who have [high reserve requirements](https://theconversation.com/credit-suisse-is-an-anomaly-why-australia-and-new-zealand-are-safe-from-bank-run-contagion-202126) and should be relatively safe from bank-runs. The FMA in New Zealand also allow brokers to offer 1:500 leverage.
      - I didn't realize until after paying for the dedicated server in **New Jersey** (Close to **Blackbull Markets'** server in **NY4**) that **fpmarkets** (Whose server is in **LD4** in **London**) keeps their client funds with Australian banks (Even with their international/non-ASIC branch with 1:500 leverage) who also have high reserve requirements and should be safe.
      - So next month (or possibly earlier?) I will switch to **fpmarkets** which does have those pairs available for trading. 
        - I'll have to get a new server in London and change my [haawks](https://www.haawks.com/) subsciption IP address. 

### Out of those events, **3** will actually be traded:

- [ ] **U.S. Core Consumer Price Index (CPI) MoM** ***(Wed 12/04/23 @12:30 GMT)***
- [ ] **U.S. Core Producer Price Index (PPI) MoM** ***(Thu 13/04/23 @12:30 GMT)***
- [ ] **U.S. Retail Sales MoM** ***(Fri 14/04/23 @12:30 GMT)***

#### For events which are at the same time, it's only possible to trade one of them, so in those cases the ones with the highest c_3 scores were chosen which works out to 5 events to trade.

#### If the lowest c_3 is:

- Between **75-80** (`if 75 <= lowest_c_3_val < 80:`): Lot Size = **0.5/$1000**
- Between **80-85** (`elif 80 <= lowest_c_3_val < 85:`): Lot Size = **0.75/$1000**
- Between **85-90** (`elif 85 <= lowest_c_3_val < 90:`): Lot Size = **1/$1000**
- Between **90-95** (`elif 90 <= lowest_c_3_val < 95:`): Lot Size = **1.5/$1000**
- Above or equal to **95** (`elif lowest_c_3_val >= 95:`): Lot Size = **2/$1000**

#### Color-coded borders

- <span><strong class="white-text">White: </strong>Events happening at the same time are grouped together so that one can be chosen.</span>
- <span><strong class="blue-text">Blue: </strong>Events that will be traded.</span>
- <span><strong class="green-text">Green: </strong>Events that were traded and made profit.</span>
- <span><strong class="red-text">Red: </strong>Events that were traded and lost money.</span>
- <span><strong class="gray-text">Gray: </strong>Events which are not being traded, either because there's another event at the same time which is being traded, or the pair isn't available on Blackbull Markets.</span>


--------

## **Tuesday**

<div class="time-group">
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>Norway Consumer Price Index (CPI) YoY</h3>
      <h3>Tuesday 11/4 @06:00 (GMT)</h3>
      <h3>Tuesday 11/4 @02:00 (ET)</h3>
      <h3>USDNOK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>79.5</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
              <h4>-LT2:</h4>
              <h5>c_3: <span>89.3</span></h5>
              <h5>data pts: <span>17</span></h5>
              <h5>dev: <span>-0.2</span></h5>
              <h5>lots/$1k: <span>1</span></h5>
              <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>89.9</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>79.5</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>89.3</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>+UT3:</h4>
              <h5>c_3: <span>89.9</span></h5>
              <h5>data pts: <span>16</span></h5>
              <h5>dev: <span>0.3</span></h5>
              <h5>lots/$1k: <span>1</span></h5>
              <h5>lots: <span>3.0</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>Norway Consumer Price Index (CPI) MoM</h3>
      <h3>Tuesday 11/4 @06:00 (GMT)</h3>
      <h3>Tuesday 11/4 @02:00 (ET)</h3>
      <h3>USDNOK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>81.2</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>81.2</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
--------

## **Wednesday**
<div class="time-group">
  <div class="card-wrapper">
    <div class="card to-trade">
      <h3>U.S. Core Consumer Price Index (CPI) MoM</h3>
      <h3>Wednesday 12/4 @12:30 (GMT)</h3>
      <h3>Wednesday 12/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>89.8</span></h5>
            <h5>data pts: <span>34</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>92.2</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>89.8</span></h5>
            <h5>data pts: <span>34</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>92.2</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Consumer Price Index (CPI) YoY</h3>
      <h3>Wednesday 12/4 @12:30 (GMT)</h3>
      <h3>Wednesday 12/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>89.3</span></h5>
            <h5>data pts: <span>36</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>91.8</span></h5>
            <h5>data pts: <span>19</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>89.3</span></h5>
            <h5>data pts: <span>36</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>91.8</span></h5>
            <h5>data pts: <span>19</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>  
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>U.S. Consumer Price Index (CPI) Index, n.s.a.</h3>
      <h3>Wednesday 12/4 @12:30 (GMT)</h3>
      <h3>Wednesday 12/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>84.0</span></h5>
            <h5>data pts: <span>23</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>82.7</span></h5>
            <h5>data pts: <span>31</span></h5>
            <h5>dev: <span>-0.4</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>84.0</span></h5>
            <h5>data pts: <span>23</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>82.7</span></h5>
            <h5>data pts: <span>31</span></h5>
            <h5>dev: <span>0.4</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

--------

## **Thursday**

<div class="time-group">
  <div class="card-wrapper">
    <div class="card to-trade">
      <h3>U.S. Core Producer Price Index (PPI) MoM</h3>
      <h3>Thursday 13/4 @12:30 (GMT)</h3>
      <h3>Thursday 13/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3_ema5: <span>77.8</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>81.0</span></h5>
            <h5>data pts: <span>25</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3_ema5: <span>77.8</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>81.0</span></h5>
            <h5>data pts: <span>25</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  
  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Producer Price Index (PPI) YoY</h3>
      <h3>Thursday 13/4 @12:30 (GMT)</h3>
      <h3>Thursday 13/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>79.4</span></h5>
            <h5>data pts: <span>29</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>79.4</span></h5>
            <h5>data pts: <span>29</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>  
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>U.S. Producer Price Index (PPI) MoM</h3>
      <h3>Thursday 13/4 @12:30 (GMT)</h3>
      <h3>Thursday 13/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>76.4</span></h5>
            <h5>data pts: <span>28</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>76.4</span></h5>
            <h5>data pts: <span>28</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
--------

## **Friday**
<div class="time-group">
  <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index (CPI) YoY</h3>
      <h3>Friday 14/4 @06:00 (GMT)</h3>
      <h3>Friday 14/4 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>75.3</span></h5>
            <h5>data pts: <span>27</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>83.7</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>83.6</span></h5>
            <h5>data pts: <span>18</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>75.3</span></h5>
            <h5>data pts: <span>27</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>83.7</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>c_3: <span>83.6</span></h5>
            <h5>data pts: <span>18</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index (CPI) MoM</h3>
      <h3>Friday 14/4 @06:00 (GMT)</h3>
      <h3>Friday 14/4 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>84.6</span></h5>
            <h5>data pts: <span>22</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>83.9</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>84.6</span></h5>
            <h5>data pts: <span>22</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>83.9</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>Sweden Consumer Price Index at Constant Interest Rates (CPIF) YoY</h3>
      <h3>Friday 14/4 @06:00 (GMT)</h3>
      <h3>Friday 14/4 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>80.9</span></h5>
            <h5>data pts: <span>26</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>85.2</span></h5>
            <h5>data pts: <span>21</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>79.8</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>80.9</span></h5>
            <h5>data pts: <span>26</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>85.2</span></h5>
            <h5>data pts: <span>21</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>c_3: <span>79.8</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>Sweden Consumer Price Index at Constant Interest Rates (CPIF) MoM</h3>
      <h3>Friday 14/4 @06:00 (GMT)</h3>
      <h3>Friday 14/4 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>76.7</span></h5>
            <h5>data pts: <span>26</span></h5>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>90.2</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>76.4</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>76.7</span></h5>
            <h5>data pts: <span>26</span></h5>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>90.2</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/$1k: <span>1.5</span></h5>
            <h5>lots: <span>4.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>c_3: <span>76.4</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="time-group">
  <div class="card-wrapper">
    <div class="card no-bottom-margin">
      <h3>U.S. Core Retail Sales MoM</h3>
      <h3>Friday 14/4 @12:30 (GMT)</h3>
      <h3>Friday 14/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>89.2</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>75.2</span></h5>
            <h5>data pts: <span>20</span></h5>
            <h5>dev: <span>-0.5</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>78.4</span></h5>
            <h5>data pts: <span>29</span></h5>
            <h5>dev: <span>-1.0</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>89.2</span></h5>
            <h5>data pts: <span>16</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>1</span></h5>
            <h5>lots: <span>3.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>75.2</span></h5>
            <h5>data pts: <span>20</span></h5>
            <h5>dev: <span>0.5</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>c_3: <span>78.4</span></h5>
            <h5>data pts: <span>29</span></h5>
            <h5>dev: <span>1.0</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="card-wrapper">
    <div class="card to-trade no-bottom-margin">
      <h3>U.S. Retail Sales MoM</h3>
      <h3>Friday 14/4 @12:30 (GMT)</h3>
      <h3>Friday 14/4 @08:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>c_3: <span>96.2</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/$1k: <span>2</span></h5>
            <h5>lots: <span>6.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>c_3: <span>77.4</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>-0.5</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>c_3: <span>83.5</span></h5>
            <h5>data pts: <span>22</span></h5>
            <h5>dev: <span>-0.9</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>2.25</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>c_3: <span>96.2</span></h5>
            <h5>data pts: <span>15</span></h5>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/$1k: <span>2</span></h5>
            <h5>lots: <span>6.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>c_3: <span>77.4</span></h5>
            <h5>data pts: <span>17</span></h5>
            <h5>dev: <span>0.5</span></h5>
            <h5>lots/$1k: <span>0.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>c_3: <span>83.5</span></h5>
            <h5>data pts: <span>22</span></h5>
            <h5>dev: <span>0.9</span></h5>
            <h5>lots/$1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>