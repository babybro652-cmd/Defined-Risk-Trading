const fs = require("fs");
const { M4, M5 } = require("./content.js");
const WPM = 140;
const words = (t) => t.replace(/\[[^\]]*\]/g, "").split(/\s+/).filter(Boolean).length;
const CHART = {
  "4.1": "A", "4.2": "A", "4.3": "B", "4.4": "C", "4.5": "D", "4.6": "E",
  "5.1": "F", "5.2": "F", "5.3": "F", "5.4": "G",
};

function lessonStats(M) {
  const out = {};
  M.slides.forEach((s, i) => {
    const k = s.lesson;
    out[k] = out[k] || { slides: [], words: 0, demo: 0, live: [] };
    out[k].slides.push(i + 1);
    out[k].words += words(s.say);
    out[k].demo += s.demo || 0;
    if (s.kind === "live") out[k].live.push(i + 1);
  });
  for (const k in out) out[k].min = Math.max(1, Math.round(out[k].words / WPM + out[k].demo + 0.3));
  return out;
}
const st4 = lessonStats(M4), st5 = lessonStats(M5);
const range = (a) => (a.length > 1 ? `${a[0]}–${a[a.length - 1]}` : `${a[0]}`);

function slideLabel(s) {
  if (s.kind === "live") return "SCREEN-SHARE";
  if (s.kind === "do") return "DO";
  if (s.kind === "image") return "EXAMPLE";
  if (s.kind === "divider") return "LESSON TITLE";
  if (s.kind === "title") return "TITLE";
  if (s.kind === "disclaimer") return "DISCLAIMER";
  if (s.kind === "agenda") return "LESSONS";
  if (s.kind === "recap") return "RECAP";
  return s.label || "TELL";
}
function slideTitle(M, s) {
  if (s.kind === "divider") return `${s.lesson}: ${M.lessons[s.lesson]}`;
  if (s.kind === "do") return `Your Turn: Lesson ${s.lesson}`;
  return (s.title || "").replace(/\n/g, " ");
}

let md = [];
md.push("# Modules 4 & 5: Recording Scripts (v4)", "");
md.push("Word-for-word teleprompter scripts for `module_4_liquidity_volume_v4.pptx` and `module_5_workflow_risk_v4.pptx`. The same script is in each slide's speaker notes, so Presenter View works as a teleprompter. Lines in [brackets] are actions, not spoken. Run times assume about 140 words a minute plus the live chart time.", "");

md.push("## Decide before you record (3 calls, 1 minute)", "");
md.push("1. **Option A daily limit.** v3 said Option A sits \"inside the $200 early-session limit\" and also \"A gives you more attempts\". With a $200 limit, one 3.5-4 point loss ($175-200) ends the day on A too, so A doesn't give more attempts. v4 keeps your $200 and says \"A takes a smaller hit per loss\" (Lesson 5.2, Module 5 slide 11). If you meant A's limit to be $400 (2 losses), change \"Daily limit: $200\" to \"$400\" on that slide and say \"A gives you two attempts\".");
md.push("2. **3.5 or 4 points.** Your rule stays 3.5-4. The 10/4 test on 137 real CRT Pro trades: a fixed 4 pt stop / 4 pt target made +$2,105 on 2 ES; the same with a 3.5 pt stop lost $745. Thin data (3 days). If you want, say once in 5.3: \"If you're unsure, use 4. 3.5 is the tightest you go.\"");
md.push("3. **Runners on the POC exit.** 4.5 teaches your read: full exit or partial with a runner. The forward-test notes show signals giving back most of their best move (median 76-93%), and on the CRT + Divergence log a full exit at the first target beat the other exit rules (+4R vs 0R). Optional line for 4.5: \"While you're learning, take the full exit at the POC. Partials come later, with screen time.\"", "");

md.push("## Recording checklist", "");
md.push("**Before you hit record**", "");
md.push("- TradingView Essentials lapsed 10/5. The free plan limits indicators per chart. Open one chart now and check that Session Liquidity, your CRT indicator and Fixed Range Volume Profile all load together. If not, renew first or split them across two saved layouts.");
md.push("- Hide anything personal: broker/account panel, P&L, order history, alerts list.");
md.push("- If CRT Pro is on the chart, its SL line sits at the sweep wick (often 1-2 pts). The course teaches a 3.5-4 pt hard stop from entry. Hide the SL/TP lines, or point out the difference when you measure the stop (5.3 script has the line).");
md.push("- Record at 1080p. Slides full screen. Zoom TradingView so candles and the price scale are readable, and use the dark theme so it matches the slides.");
md.push("- Tools you'll use: Measure (Shift + drag), Fixed Range Volume Profile, Long/Short Position (shows the R on 5.4).", "");
md.push("**Charts to set up (save each as a layout or tab, ES 30-minute unless noted)**", "");
md.push("| Chart | What it shows | Used in |");
md.push("|---|---|---|");
md.push("| A | One recent full day, Session Liquidity on: Asia range, London sweeps it, New York goes after the untouched level | 4.1, 4.2 |");
md.push("| B | Yesterday's session, ready to draw Fixed Range Volume Profile | 4.3 |");
md.push("| C | Two real sweeps with the profile drawn: one through a low-volume gap, one into a high-volume node | 4.4 |");
md.push("| D | Two POC setups: one where the POC was the target, one POC entry (reaction candle, stop, untaken session-high/low target) | 4.5 |");
md.push("| E | One three-tool example: session liquidity target, CRT sweep, sweep through a low-volume gap, POC target | 4.6 |");
md.push("| F | One recent setup for the checklist, sizing and stop measuring (can reuse D's entry) | 5.1, 5.2, 5.3 |");
md.push("| G | One full trade, start to finish, inside 10 AM-12 PM ET, on your CRT entry chart plus the 30-minute profile | 5.4 |", "");
md.push("**Order and screen-shares** (record each lesson as its own video)", "");
md.push("| Lesson | Slides | Switch to TradingView at slide | Chart | Est. time |");
md.push("|---|---|---|---|---|");
let tot4 = 0, tot5 = 0;
const row = (M, st, k, label) => {
  const s = st[k];
  md.push(`| ${label} | ${range(s.slides)} | ${s.live.length ? s.live.join(", ") : "none"} | ${CHART[k] || "none"} | ${s.min} min |`);
  return s.min;
};
tot4 += row(M4, st4, "intro", "M4 intro + disclaimer");
for (const k of Object.keys(M4.lessons)) tot4 += row(M4, st4, k, `${k} ${M4.lessons[k]}`);
tot4 += row(M4, st4, "outro", "M4 recap");
tot5 += row(M5, st5, "intro", "M5 intro + disclaimer");
for (const k of Object.keys(M5.lessons)) tot5 += row(M5, st5, k, `${k} ${M5.lessons[k]}`);
tot5 += row(M5, st5, "outro", "M5 recap");
md.push("", `Module 4 is about ${tot4} minutes on camera, Module 5 about ${tot5}. Budget about 1.5x that for retakes and setup: roughly ${Math.round((tot4 + tot5) * 1.5 / 5) * 5} minutes for both.`, "");
md.push("Put the M4 intro, disclaimer and lessons slide at the start of the 4.1 video (same for 5.1), and the recap at the end of 4.6 and 5.4. Or record them as a short separate intro video.", "");
md.push("---", "");

function emit(M, st) {
  md.push(`# ${M.module}: ${M.name}`, "");
  let cur = null;
  M.slides.forEach((s, i) => {
    const k = s.lesson;
    if (k !== cur) {
      cur = k;
      const name = k === "intro" ? "Intro" : k === "outro" ? "Recap" : `${k}: ${M.lessons[k]}`;
      md.push(`## ${name} (about ${st[k].min} min)`, "");
    }
    md.push(`**Slide ${i + 1} · ${slideLabel(s)} · ${slideTitle(M, s)}**`, "");
    if (s.kind === "live") md.push(`*Screen-share, chart ${CHART[k]}. On screen: ${s.cues.join("; ")}.*`, "");
    md.push(s.say, "");
  });
  md.push("---", "");
}
emit(M4, st4);
emit(M5, st5);
md.push("## What changed from v3", "");
md.push("- One idea per slide, text at 22-36 pt for 1080p, and a speaker-notes script on every slide.");
md.push("- Every TradingView moment has its own dashed \"SCREEN-SHARE: TRADINGVIEW\" slide with the 3 things to show.");
md.push("- New example charts with large labels; the 4.5 example is split into \"POC as the exit\" and \"POC as the entry\".");
md.push("- Added: a risk disclaimer and a lessons slide at the start of each module, a recap slide at the end, a worked sizing example ($200 / 4 pts / $50 = 1 ES), and a stop-cost table that notes commissions.");
md.push("- Same method and 10/1 decisions: POC lesson 4.5, 30-minute profile, 3.5-4 pt hard stop, 1 or 2 ES fixed, 10 AM-12 PM window, your $1,000 / $200 / 1-2 trades, $400 or hourly × 8 × 2 profit goal.");
md.push("- One wording change for consistency: Option A is now \"a smaller hit per loss\" instead of \"more attempts\" (see Decide before you record #1).", "");
md.push("Still open from v3: Lesson 3.2 Kill Zones teaches three windows. One line there (\"while you're learning, 10 AM-12 PM is the one you'll use\") would set up the Module 5 checklist.");
fs.writeFileSync("scripts-m4-m5-v4.md", md.join("\n") + "\n");
console.log(tot4, tot5);
for (const [k, v] of Object.entries(st4)) console.log("M4", k, v.min, v.words);
for (const [k, v] of Object.entries(st5)) console.log("M5", k, v.min, v.words);
