// Add this line at the beginning of your code to define the button ids
#define SELL3_ID 1
#define SELL2_ID 2
#define SELL1_ID 3
#define BUY1_ID 4
#define BUY2_ID 5
#define BUY3_ID 6

// Modify your OnInit() function to assign button ids
int OnInit()
{
   // Create buttons
   Button_SELL3.Create(0, "SELL3", SELL3_ID, 20, 80, 40);
   Button_SELL2.Create(0, "SELL2", SELL2_ID, 70, 80, 40);
   Button_SELL1.Create(0, "SELL1", SELL1_ID, 120, 80, 40);
   Button_BUY1.Create(0, "BUY1", BUY1_ID, 170, 80, 40);
   Button_BUY2.Create(0, "BUY2", BUY2_ID, 220, 80, 40);
   Button_BUY3.Create(0, "BUY3", BUY3_ID, 270, 80, 40);

   return (INIT_SUCCEEDED);
}

// Remove the checks for button clicks from the OnTick() function
void OnTick()
{
}

// Add this new ChartEvent() function to handle button clicks
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if (id == CHARTEVENT_OBJECT_CLICK)
   {
      if (lparam == SELL3_ID)
      {
         trade(Lot_SELL3, OP_SELL);
      }
      else if (lparam == SELL2_ID)
      {
         trade(Lot_SELL2, OP_SELL);
      }
      else if (lparam == SELL1_ID)
      {
         trade(Lot_SELL1, OP_SELL);
      }
      else if (lparam == BUY1_ID)
      {
         trade(Lot_BUY1, OP_BUY);
      }
      else if (lparam == BUY2_ID)
      {
         trade(Lot_BUY2, OP_BUY);
      }
      else if (lparam == BUY3_ID)
      {
         trade(Lot_BUY3, OP_BUY);
      }
   }
}
