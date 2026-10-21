# Morning Markets Brief — daily playbook

A daily markets brief for an equity research analyst at an Indian PMS (mid/small-cap focus).
It is published every morning as a private web page (Claude artifact) that the reader opens on their phone by 7:00 AM IST.

- **Page (republish to this SAME link every day):** https://claude.ai/artifact/SyGAypMcXp6i4uAyNazCfr
- **Folder:** the folder this README is in (on the laptop: `C:\Users\lenovo\.claude\morning-brief\`; in the cloud: the repository checkout). Run every script from this folder.
- **Reader's wishes:** India first, then global. Plain English, short sentences. About 15 minutes to read. Every number shows when it was taken and where it came from. Anything you cannot confirm is left out. No investment advice, no stock tips. Geopolitics ends with a "Possible market links" box, so the reader forms their own view first. **No "today's calendar" section** (the reader dropped it).

## Steps (run every day, including weekends and Indian market holidays)

Use `python -I -X utf8` for every script (plain `-I` breaks on ₹ and other symbols).
Let `DATE` be today's date in IST as `YYYY-MM-DD` and `RUN` be `runs/DATE`.

1. **Numbers:** `python -I -X utf8 fetch_numbers.py runs/DATE`, then read `runs/DATE/numbers.txt`.
   - NSE gives India's last session (indices, breadth, FII/DII provisional, Nifty and F&O movers, bulk/block deals).
   - Yahoo gives global indices, commodities and FX. Each row shows `last <date> vs <prev date>` and the quote time in IST. Use those dates in the "As of" column. If the two dates are not consecutive sessions (futures contract rolls, missing bars), the % change may be wrong: leave the change out ("–") or take it from a news article.
   - Official yields: US Treasury (date, 2y/10y/30y), Bundesbank 10-year Bund, Japan MoF 10-year JGB. India's 10-year G-sec yield and the rupee close come from ET's bonds and forex stories (`ET Bonds`, `ET Forex` in the headlines).
   - If a source failed (see ERRORS at the bottom), skip that row; never fill a gap from memory.
2. **Headlines:** `python -I -X utf8 fetch_news.py runs/DATE 30`, then read `runs/DATE/headlines.txt`.
   - WebSearch is poor for the last 48 hours, and WebFetch is blocked (403) on Business Standard, CNBC and ET. Use these feeds instead.
3. **Check facts behind the stories you will use:** `python -I -X utf8 art_text.py runs/DATE <url1> <url2> …` with direct ET, Mint, Business Standard or CNBC links (8–20 articles is typical). Google News links (`news.google.com/rss/articles/...`) cannot be read; use them only for a fact stated in the headline itself, and cite them as the source.
4. **Write `runs/DATE/content.html`** using the components in `example_content.html` (open it and copy its patterns). Sections, in this order:
   1. **Start here / The two-minute version:** five bullets, the most important first.
   2. **Before the bell / How India may open:** the GIFT Nifty indication if a headline or article this morning states it (with link); otherwise say "GIFT Nifty: not available this morning". Then Asia so far today, the overnight US close, and moves in oil and the rupee. On Saturdays, Sundays and Indian market holidays, replace this with "Week ahead in brief" or "When India reopens", in two or three lines.
   3. **Capital markets / Equity, debt, commodities and currency:**
      - India equity table (Nifty 50, Sensex, Nifty 500, Midcap 150, Smallcap 250, India VIX), then breadth, best and worst sectors, FII/DII flows, the biggest Nifty 50 moves, the reason for the move (from articles), and notable bulk/block deals in Nifty 500 names (say so when the largest deals were only same-day trading-firm round trips).
      - Global equity table with an "As of" column: US (S&P 500, Nasdaq, Dow), Europe (Stoxx 600, FTSE, DAX, CAC), Asia (Nikkei, Kospi, Hang Seng, Shanghai, Taiwan).
      - Debt table: India 10-year (and 1-year OIS if available), US 2/10/30-year, Germany 10-year, France 10-year (if in an article), Japan 10-year. Then two short paragraphs: India and global.
      - Commodities table: Brent, WTI, US natural gas, gold, silver, copper, aluminium. Then one paragraph on oil and its drivers.
      - Currency table: USD/INR, dollar index, EUR/USD, USD/JPY, USD/CNY. Then one paragraph on the rupee, RBI action and forex reserves.
   4. **Companies / Overnight company news:** India (results and big announcements since the last edition: profit, revenue and the key operating number, plus how the stock reacted if known; IPOs) and Global (results with an India read-across: IT services, semiconductors, autos, oil, FMCG, pharma). Mid and small caps are welcome.
   5. **Economies / Data and central banks:** India, US, China, Europe and Japan — data released since the last edition (actual vs previous, and vs forecast if an article gives it) and central-bank moves or odds.
   6. **Policy / Regulators and government:** RBI, SEBI and government actions (taxes, duties, trade deals, export curbs, PLI and similar schemes).
   7. **Geopolitics / Major geopolitical actions:** wars and ceasefires, sanctions, tariffs and trade deals, elections, shipping disruptions — only events with a route into markets. Close with the `links-box` "Possible market links (read after forming your own view)", 3–5 bullets.
   - **Rules for every section:**
     - Every number must come from `numbers.txt`, an article you read, or a headline you cite.
     - Each section ends with `<p class="src">Sources: …</p>`, and company and economy bullets carry their own link.
     - Use Indian formats (₹, crore, lakh crore), bp for yield changes, a real minus sign (−), and `up`/`down` spans for changes.
     - Say plainly when a market was closed (holiday or weekend) and which session the numbers are from.
     - Don't predict prices or give buy/sell views; when an article quotes an analyst, name the source.
5. **Build the page:** `python -I -X utf8 build_page.py runs/DATE/content.html runs/DATE/page.html "<Weekday D Month YYYY>" "<h:mm AM>"`.
   - Optionally add a 5th argument: a text file with a one-line notice shown under the masthead (for example "Indian markets are closed today for Diwali." or "NSE data was unavailable this morning; India figures are from news reports.").
6. **Check before publishing:**
   - The numbers in the page match `numbers.txt`.
   - Every table row has an "As of" cell.
   - There are no placeholder links (`https://…`).
   - All seven sections are present, and the page reads in about 15 minutes.
7. **Publish to the same link:**
   - First call the Artifact tool with `action: "read"` and `url` = the page link above.
   - Then call it again with `file_path` = the full path of `runs/DATE/page.html` and `url` = the page link. Do not pass `icon`. Do not change the title.
   - If the publish is refused because someone published a newer version, stop and report it instead of forcing.
   - If this session has no Artifact tool, don't publish anywhere else. Finish with a line saying the page was built but couldn't be published because the Artifact tool was missing.
8. **Archive:** copy `runs/DATE/page.html` to `editions/DATE.html`. Skip this in the cloud; the page's version history keeps past editions.
9. **Finish** with one line: the edition date, the link, and anything that failed (for example "GIFT Nifty unavailable" or "NSE blocked; India numbers from news").

## Notes
- Times: US markets close at 1:30 AM IST (2:30 AM after US clocks change on 1 November), Europe at 9:00–9:30 PM IST, and Japan and Korea open at 5:30 AM IST.
- Sunday editions: markets tables show Friday's closes (say so). Lead with the weekend's news and the week ahead in two lines.
- Keep `runs/` folders; they are the record of what each edition was built from.
