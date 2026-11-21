Write today's Morning Markets Brief as a single HTML file.

Follow these rules exactly:
1. Read the numbers.txt and headlines.txt data above. Also use art_text.py to read
   articles behind the key stories (ET, Mint, Business Standard, CNBC links only).
2. Write a file called content.html containing ONLY <section class="sec"> blocks.
   Copy the HTML patterns from example_content.html (section order, table shapes,
   kicker paragraphs, change spans, Sources lines, links-box in section 7).
3. Sections, in this order:
   1. Start here / The two-minute version — five bullets, most important first.
   2. Before the bell / How India may open — GIFT Nifty if available, Asia so far,
      overnight US close, oil and rupee moves. Weekends/holidays: "Week ahead" instead.
   3. Capital markets — India equity table (Nifty 50, Sensex, Nifty 500, Midcap 150,
      Smallcap 250, India VIX), breadth, sector moves, FII/DII flows, biggest Nifty
      movers with reasons, notable bulk/block deals. Then global equity (US, Europe,
      Asia), debt (India 10y, US 2/10/30y, Germany 10y, Japan 10y), commodities
      (Brent, WTI, US gas, gold, silver, copper, aluminium), currency (USD/INR,
      dollar index, EUR/USD, USD/JPY, USD/CNY). Each table has an "As of" column.
      On phone: fold "As of" under the name in small grey type (build_site.py does
      this automatically, so keep the column in the table).
   4. Companies — overnight India results and announcements (profit, revenue, key
      operating number, stock reaction; IPOs). Global results with India read-across
      (IT services, semiconductors, autos, oil, FMCG, pharma).
   5. Economies — India, US, China, Europe, Japan: data released (actual vs previous
      and vs forecast), central bank moves or odds.
   6. Policy — RBI, SEBI, government actions (taxes, duties, trade, export curbs, PLI).
   7. Geopolitics — only events with a route into markets. End with the links-box:
      "Possible market links (read after forming your own view)" with 3–5 bullets.
4. Every number comes from numbers.txt, an article you read, or a headline you cite.
   Never fill a gap from memory. If a source failed, skip that row and say so.
5. Each section ends with <p class="src">Sources: …</p> with clickable links.
6. Use Indian formats (₹, crore, lakh crore). bp for yield changes. A real minus
   sign (−) for negatives. up/down/flat spans for changes.
7. Say plainly which session the numbers are from. Weekends and Indian market holidays
   are included — just label the session clearly.
8. No investment advice. No stock tips. No "today's calendar" section.
9. Finish with one plain-text line (outside the HTML): the edition date and anything
   that failed (e.g. "GIFT Nifty unavailable" or "NSE blocked; India numbers from news").
