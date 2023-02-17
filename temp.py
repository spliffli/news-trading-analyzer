input_string = """
30000	U.S. Crude Oil Inventories
30001	U.S. Gasoline Inventories
30002	U.S. Distillate Fuel Production
30008	U.S. Cushing Crude Oil Inventories
30010	U.S. Natural Gas Storage
10000	U.S. Nonfarm Payrolls
10005	U.S. Unemployment Rate
10010	U.S. Producer Price Index (PPI) MoM
10011	U.S. Producer Price Index (PPI) YoY
10012	U.S. Core Producer Price Index (PPI) MoM
10013	U.S. Core Producer Price Index (PPI) YoY
10020	U.S. Import Price Index MoM
10022	U.S. Export Price Index MoM
10030	U.S. Consumer Price Index (CPI) MoM
10031	U.S. Consumer Price Index (CPI) YoY
10032	U.S. Core Consumer Price Index (CPI) MoM
10033	U.S. Core Consumer Price Index (CPI) YoY
10034	U.S. Consumer Price Index (CPI) Index, n.s.a.
10037	U.S. Core Consumer Price Index (CPI) Index
10040	U.S. Industrial Production MoM
10041	U.S. Industrial Production YoY
10042	U.S. Capacity Utilization Rate
10044	U.S. Manufacturing Production MoM
10060	U.S. Gross Domestic Product (GDP) QoQ
10061	U.S. Gross Domestic Product (GDP) Price Index QoQ
10070	U.S. Personal Spending MoM
10071	U.S. Core PCE Price Index MoM
10072	U.S. Core PCE Price Index YoY
10073	U.S. PCE price index
10074	U.S. PCE Price index YoY
10075	U.S. Personal Income MoM
10076	U.S. Real Personal Consumption MoM
10080	U.S. JOLTs Job Openings
10090	U.S. Michigan Consumer Sentiment
10091	U.S. Michigan Inflation Expectations
10092	U.S. Michigan Current Conditions
10100	U.S. Trade Balance
10110	U.S. Factory Orders MoM
10120	U.S. Wholesale Inventories MoM
10130	U.S. Retail Sales MoM
10132	U.S. Core Retail Sales MoM
10140	U.S. Business Inventories MoM
10150	U.S. Housing Starts MoM
10152	U.S. Housing Starts
10154	U.S. Building Permits MoM
10156	U.S. Building Permits
10160	U.S. New Home Sales MoM
10162	U.S. New Home Sales
10170	U.S. Durable Goods Orders MoM
10172	U.S. Core Durable Goods Orders MoM
10180	U.S. Retail Inventories Excluding Auto
10190	U.S. Goods Trade Balance
10200	U.S. Wholesale Inventories MoM
10210	U.S. Construction Spending MoM
10220	U.S. Employment Cost Index QoQ
10230	U.S. Initial Jobless Claims
10240	Fed Interest Rate Decision
10242	U.S. Federal Open Market Committee (FOMC) Statement
10250	Canada Consumer Price Index (CPI) MoM
10251	Canada Consumer Price Index (CPI) YoY
10252	Canada Core Consumer Price Index (CPI) MoM
10253	Canada Core Consumer Price Index (CPI) YoY
10260	Canada Core Retail Sales MoM
10261	Canada Retail Sales MoM
10270	Canada Gross Domestic Product (GDP) MoM
10272	Canada Gross Domestic Product (GDP) YoY
10280	Canada Trade Balance
10281	Canada Exports
10282	Canada Imports
10290	Canada Employment Change
10291	Canada Unemployment Rate
10292	Canada Full Employment Change
10293	Canada Part Time Employment Change
10294	Canada Participation Rate
10300	Canada Building Permits MoM
10310	Canada New Housing Price Index MoM
10320	Canada Manufacturing Sales MoM
10330	Canada Foreign Securities Purchases
10331	Foreign Securities Purchases by Canadians
10340	Canada Wholesale Sales MoM
10350	Canada Current Account
10360	Canada Industrial Product Price Index (IPPI) MoM
10361	Canada Industrial Product Price Index (IPPI) YoY
10370	Canada Raw Materials Price Index (RMPI) MoM
10371	Canada Raw Materials Price Index (RMPI) YoY
10380	Canada Labor Productivity QoQ
10390	Canada Gross Domestic Product (GDP) Annualized QoQ
00091	Norway Gross Domestic Product (GDP) QoQ
00092	Norway Gross Domestic Product (GDP) Mainland QoQ
00047	Norway Core Retail Sales MoM
00049	Norway Unemployment Rate
00041	Norway Consumer Price Index (CPI) MoM
00042	Norway Consumer Price Index (CPI) YoY
00017	Norway Interest Rate Decision
00071	Sweden Gross Domestic Product (GDP) QoQ
00072	Sweden Gross Domestic Product (GDP) YoY
00057	Sweden Retail Sales MoM
00058	Sweden Retail Sales YoY
00059	Sweden Unemployment Rate
00051	Sweden Consumer Price Index (CPI) MoM
00052	Sweden Consumer Price Index (CPI) YoY
00053	Sweden Consumer Price Index at Constant Interest Rates (CPIF) MoM
00054	Sweden Consumer Price Index at Constant Interest Rates (CPIF) YoY
00141	Poland Interest Rate Decision
00003	Russia Interest Rate Decision
00021	Eurozone Interest Rate Decision
00013	Turkey One-Week Repo Rate
"""

output_list = [line.strip().replace('\t', '  ') for line in input_string.split("\n")]
sorted_output = sorted(output_list)

print(",\n".join(['"{}"'.format(line) for line in sorted_output]))

"10000  U.S. Nonfarm Payrolls",
"10005  U.S. Unemployment Rate",
"10010  U.S. Producer Price Index (PPI) MoM",
"10011  U.S. Producer Price Index (PPI) YoY",
"10012  U.S. Core Producer Price Index (PPI) MoM",
"10013  U.S. Core Producer Price Index (PPI) YoY",
"10020  U.S. Import Price Index MoM",
"10022  U.S. Export Price Index MoM",
"10030  U.S. Consumer Price Index (CPI) MoM",
"10031  U.S. Consumer Price Index (CPI) YoY",
"10032  U.S. Core Consumer Price Index (CPI) MoM",
"10033  U.S. Core Consumer Price Index (CPI) YoY",
"10034  U.S. Consumer Price Index (CPI) Index, n.s.a.",
"10037  U.S. Core Consumer Price Index (CPI) Index",
"10040  U.S. Industrial Production MoM",
"10041  U.S. Industrial Production YoY",
"10042  U.S. Capacity Utilization Rate",
"10044  U.S. Manufacturing Production MoM",
"10060  U.S. Gross Domestic Product (GDP) QoQ",
"10061  U.S. Gross Domestic Product (GDP) Price Index QoQ",
"10070  U.S. Personal Spending MoM",
"10071  U.S. Core PCE Price Index MoM",
"10072  U.S. Core PCE Price Index YoY",
"10073  U.S. PCE price index",
"10074  U.S. PCE Price index YoY",
"10075  U.S. Personal Income MoM",
"10076  U.S. Real Personal Consumption MoM",
"10080  U.S. JOLTs Job Openings",
"10090  U.S. Michigan Consumer Sentiment",
"10091  U.S. Michigan Inflation Expectations",
"10092  U.S. Michigan Current Conditions",
"10100  U.S. Trade Balance",
"10110  U.S. Factory Orders MoM",
"10120  U.S. Wholesale Inventories MoM",
"10130  U.S. Retail Sales MoM",
"10132  U.S. Core Retail Sales MoM",
"10140  U.S. Business Inventories MoM",
"10150  U.S. Housing Starts MoM",
"10152  U.S. Housing Starts",
"10154  U.S. Building Permits MoM",
"10156  U.S. Building Permits",
"10160  U.S. New Home Sales MoM",
"10162  U.S. New Home Sales",
"10170  U.S. Durable Goods Orders MoM",
"10172  U.S. Core Durable Goods Orders MoM",
"10180  U.S. Retail Inventories Excluding Auto",
"10190  U.S. Goods Trade Balance",
"10200  U.S. Wholesale Inventories MoM",
"10210  U.S. Construction Spending MoM",
"10220  U.S. Employment Cost Index QoQ",
"10230  U.S. Initial Jobless Claims",
"10240  Fed Interest Rate Decision",
"10242  U.S. Federal Open Market Committee (FOMC) Statement",
"10250  Canada Consumer Price Index (CPI) MoM",
"10251  Canada Consumer Price Index (CPI) YoY",
"10252  Canada Core Consumer Price Index (CPI) MoM",
"10253  Canada Core Consumer Price Index (CPI) YoY",
"10260  Canada Core Retail Sales MoM",
"10261  Canada Retail Sales MoM",
"10270  Canada Gross Domestic Product (GDP) MoM",
"10272  Canada Gross Domestic Product (GDP) YoY",
"10280  Canada Trade Balance",
"10281  Canada Exports",
"10282  Canada Imports",
"10290  Canada Employment Change",
"10291  Canada Unemployment Rate",
"10292  Canada Full Employment Change",
"10293  Canada Part Time Employment Change",
"10294  Canada Participation Rate",
"10300  Canada Building Permits MoM",
"10310  Canada New Housing Price Index MoM",
"10320  Canada Manufacturing Sales MoM",
"10330  Canada Foreign Securities Purchases",
"10331  Foreign Securities Purchases by Canadians",
"10340  Canada Wholesale Sales MoM",
"10350  Canada Current Account",
"10360  Canada Industrial Product Price Index (IPPI) MoM",
"10361  Canada Industrial Product Price Index (IPPI) YoY",
"10370  Canada Raw Materials Price Index (RMPI) MoM",
"10371  Canada Raw Materials Price Index (RMPI) YoY",
"10380  Canada Labor Productivity QoQ",
"10390  Canada Gross Domestic Product (GDP) Annualized QoQ",
"30000  U.S. Crude Oil Inventories",
"30001  U.S. Gasoline Inventories",
"30002  U.S. Distillate Fuel Production",
"30008  U.S. Cushing Crude Oil Inventories",
"30010  U.S. Natural Gas Storage"
"00003  Russia Interest Rate Decision",
"00013  Turkey One-Week Repo Rate",
"00017  Norway Interest Rate Decision",
"00021  Eurozone Interest Rate Decision",
"00041  Norway Consumer Price Index (CPI) MoM",
"00042  Norway Consumer Price Index (CPI) YoY",
"00047  Norway Core Retail Sales MoM",
"00049  Norway Unemployment Rate",
"00091  Norway Gross Domestic Product (GDP) QoQ",
"00092  Norway Gross Domestic Product (GDP) Mainland QoQ",
"00051  Sweden Consumer Price Index (CPI) MoM",
"00052  Sweden Consumer Price Index (CPI) YoY",
"00053  Sweden Consumer Price Index at Constant Interest Rates (CPIF) MoM",
"00054  Sweden Consumer Price Index at Constant Interest Rates (CPIF) YoY",
"00057  Sweden Retail Sales MoM",
"00058  Sweden Retail Sales YoY",
"00059  Sweden Unemployment Rate",
"00071  Sweden Gross Domestic Product (GDP) QoQ",
"00072  Sweden Gross Domestic Product (GDP) YoY",
"00141  Poland Interest Rate Decision"