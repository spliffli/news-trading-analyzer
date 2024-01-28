
# **2023 Week 14 Schedule**

<img src="/images/week-past-300-120px.png" alt="This week is PAST">

### This was generated on **31/03/2023** and has **4** events from **2023/04/06** to **2023/04/06**

#### For events which are at the same time, it's only possible to trade one of them, so in those cases the one with the highest c_3 score will be chosen

#### For each trigger, the lowest value out of the ***c_3***, ***c_3_ema5***, **c_3_ema10**, & ***c_3_ema5*** was used to calculate the lot size:

#### If the lowest c_3 is:

- Between **75-80** (`if 75 <= lowest_c_3_val < 80:`): Lot Size = **0.5/$1000**
- Between **80-85** (`elif 80 <= lowest_c_3_val < 85:`): Lot Size = **0.75/$1000**
- Between **85-90** (`elif 85 <= lowest_c_3_val < 90:`): Lot Size = **1/$1000**
- Between **90-95** (`elif 90 <= lowest_c_3_val < 95:`): Lot Size = **1.5/$1000**
- Above or equal to **95** (`elif lowest_c_3_val >= 95:`): Lot Size = **2/$1000**

--------

## **Thursday**

<div class="card-wrapper">
  <div class="card">
    <h3>U.S. Initial Jobless Claims</h3>
    <h3>Thursday 6/4 @12:30 (GMT)</h3>
    <h3>Thursday 6/4 @08:30 (ET)</h3>
    <h3>USDJPY</h3>
    <hr>
    <div class="triggers">
      <h4>LTA: <span>Buy</span></h4>
      <h4>UTA: <span>Sell</span></h4>
      <br>
        <div class="lower-triggers">
        <div class="trigger">
          <h4>-LT1:</h4>
          <h5>c_3: <span>78.6</span></h5>
          <h5>data pts: <span>72</span></h5>
          <h5>dev: <span>-12.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
      </div>
      <br>
      <div class="upper-triggers">
        <div class="trigger">
        <h4>+UT1:</h4>
          <h5>c_3: <span>78.6</span></h5>
          <h5>data pts: <span>72</span></h5>
          <h5>dev: <span>12.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
      </div>
    </div>
  </div>
  </div>  <div class="card-wrapper">
  <div class="card">
    <h3>Canada Employment Change</h3>
    <h3>Thursday 6/4 @12:30 (GMT)</h3>
    <h3>Thursday 6/4 @08:30 (ET)</h3>
    <h3>USDCAD</h3>
    <hr>
    <div class="triggers">
      <h4>LTA: <span>Buy</span></h4>
      <h4>UTA: <span>Sell</span></h4>
      <br>
        <div class="lower-triggers">
        <div class="trigger">
          <h4>-LT1:</h4>
          <h5>c_3: <span>87.6</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>-10.0</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
        <div class="trigger">
          <h4>-LT2:</h4>
          <h5>c_3: <span>78.8</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>-25.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
        <div class="trigger">
          <h4>-LT3:</h4>
          <h5>c_3: <span>99.0</span></h5>
          <h5>data pts: <span>16</span></h5>
          <h5>dev: <span>-50.0</span></h5>
          <h5>lots/$1k: <span>2</span></h5>
          <h5>lots: <span>2.0</span></h5>
        </div>
      </div>
      <br>
      <div class="upper-triggers">
        <div class="trigger">
        <h4>+UT1:</h4>
          <h5>c_3: <span>87.6</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>10.0</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
        <div class="trigger">
        <h4>+UT2:</h4>
          <h5>c_3: <span>78.8</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>25.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
        <div class="trigger">
        <h4>+UT3:</h4>
          <h5>c_3: <span>99.0</span></h5>
          <h5>data pts: <span>16</span></h5>
          <h5>dev: <span>50.0</span></h5>
          <h5>lots/$1k: <span>2</span></h5>
          <h5>lots: <span>2.0</span></h5>
        </div>
      </div>
    </div>
  </div>
  </div>  <div class="card-wrapper">
  <div class="card">
    <h3>Canada Unemployment Rate</h3>
    <h3>Thursday 6/4 @12:30 (GMT)</h3>
    <h3>Thursday 6/4 @08:30 (ET)</h3>
    <h3>USDCAD</h3>
    <hr>
    <div class="triggers">
      <h4>LTA: <span>Sell</span></h4>
      <h4>UTA: <span>Buy</span></h4>
      <br>
        <div class="lower-triggers">
        <div class="trigger">
          <h4>-LT1:</h4>
          <h5>c_3: <span>86.5</span></h5>
          <h5>data pts: <span>18</span></h5>
          <h5>dev: <span>-0.3</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
      </div>
      <br>
      <div class="upper-triggers">
        <div class="trigger">
        <h4>+UT1:</h4>
          <h5>c_3: <span>86.5</span></h5>
          <h5>data pts: <span>18</span></h5>
          <h5>dev: <span>0.3</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
      </div>
    </div>
  </div>
</div>

--------

## **Friday**

<div class="card-wrapper">
  <div class="card">
    <h3>U.S. Nonfarm Payrolls</h3>
    <h3>Friday 7/4 @13:30 (GMT)</h3>
    <h3>Friday 7/4 @08:30 (ET)</h3>
    <h3>USDJPY</h3>
    <hr>
    <div class="triggers">
      <h4>LTA: <span>Sell</span></h4>
      <h4>UTA: <span>Buy</span></h4>
      <br>
        <div class="lower-triggers">
        <div class="trigger">
          <h4>-LT1:</h4>
          <h5>c_3: <span>85.8</span></h5>
          <h5>data pts: <span>17</span></h5>
          <h5>dev: <span>-25.0</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
        <div class="trigger">
          <h4>-LT2:</h4>
          <h5>c_3: <span>78.1</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>-90.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
      </div>
      <br>
      <div class="upper-triggers">
        <div class="trigger">
        <h4>+UT1:</h4>
          <h5>c_3: <span>85.8</span></h5>
          <h5>data pts: <span>17</span></h5>
          <h5>dev: <span>25.0</span></h5>
          <h5>lots/$1k: <span>1</span></h5>
          <h5>lots: <span>1.0</span></h5>
        </div>
        <div class="trigger">
        <h4>+UT2:</h4>
          <h5>c_3: <span>78.1</span></h5>
          <h5>data pts: <span>15</span></h5>
          <h5>dev: <span>90.0</span></h5>
          <h5>lots/$1k: <span>0.5</span></h5>
          <h5>lots: <span>0.5</span></h5>
        </div>
      </div>
    </div>
  </div>
</div>