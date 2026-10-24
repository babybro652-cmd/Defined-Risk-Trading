# Anti-lag and supercharger research (10/24/2026)

Tim asked (10/24): (1) anti-lag for the two turbo builds (1979 Cutlass, 2012 Cruze), and
(2) centrifugal vs traditional superchargers for the Charger. Goal stays the same (10/23):
reliability first, build once, no redo later.

Prices marked "checked 10/24" came from a retailer or maker listing that day. Everything else is
an estimate: confirm before buying. Sources are listed at the end.

---

## Short answers

| Car | Recommendation | Optional cost | Big risk | Legal note (NC) |
|---|---|---|---|---|
| 1979 Cutlass (forged LS stroker, twin turbo, 4L80E, Terminator X Max) | **No true anti-lag.** Use "soft" anti-lag already in the Terminator X Max: 2-step launch with launch timing retard and a launch boost target, boost by gear and by speed, boost safeties. Keep ball-bearing 62 mm twins and pick a 3,000-3,200 stall converter. Add a Holley dual boost solenoid for dome control | about $135-460 parts plus 1-2 hrs of dyno time | 2-step pops and heat on launches: use it at the track, not on every street light | Cats required on the road (G.S. 20-128(c), 1968 and newer). Exempt from emissions inspection (older than 20 model years). Dumps and cutouts closed on public roads (20-128(b)) |
| 2012 Cruze 1.4T (forged pistons, ZZP Z04 plus tune, daily) | **No anti-lag of any kind.** The ZZP tune already controls boost (wastegate tables, torque management, spool). If lag bothers him, the fix is turbo choice: the ZZP V3.2 spools about like stock; the Z04 spools 500-700 rpm later | $0 (in the Z04 plan), or switch to the V3.2 and save about $1,100 | Anti-lag on a small 1.4T kills the turbo, exhaust valves (the burnt-valve car) and the cat fast | Keep a cat: the Z04 downpipe includes a high-flow cat. Person County is out of the emissions test program, but 20-128(c) still applies |
| 2016 Charger (forged 392, Whipple 3.0L) | No anti-lag needed: a supercharger has no turbo lag | n/a | n/a | n/a |

**Supercharger verdict for the Charger: keep the Whipple twin-screw (traditional). It is the
better fit for Tim's goals.** One change: set the pulley for about 5.5-6.5 psi, not 7, because
dyno results show a 392 with this blower makes more than the 575-600 whp target at 7 psi. Details
in Part 2.

---

## Part 1: Anti-lag for the turbo cars

### What the options are

| Option | How it works | Lag fix | Wear | Street fit |
|---|---|---|---|---|
| True anti-lag (rally "bang-bang", ALS) | Off throttle, the ECU holds the throttle or an air bypass open, retards timing far past normal and adds fuel. The mix burns in the exhaust manifold and keeps the turbo spinning | Best: boost stays up between corners | Severe. Turbo temps jump from about 800 C to 1,100 C plus; manifold, turbine wheel, exhaust valves and cats take the hit. Rally teams rebuild turbos often. Wiki and tuning-ECU docs say it can destroy the turbo, exhaust, valves and cat and is not emissions legal | No. Loud bangs and flames, kills cats, competition only |
| Rolling anti-lag | Ignition cut or retard that holds a set rpm or speed while you stay on the throttle (roll racing) | Good for roll racing only | High while active | No for daily use |
| 2-step / launch control | A second rev limiter for launches (ignition cut or timing retard) so boost builds while stopped | Launch only | Moderate: short bursts of heat, pops, converter and trans heat on an auto | Track and occasional use only |
| Boost by gear, speed or time | ECU sets target boost per gear or road speed through the wastegate solenoid | None, but it lets you run more boost where you can use it, and less in 1st and 2nd | Lowers wear (less wheelspin, less shock) | Yes: the best street tool |
| No-lift shift / flat-foot shift | Brief ignition cut during a manual shift so you keep the throttle down and keep boost | Keeps boost between shifts (manual only) | Low to moderate (driveline shock) | OK on a manual, not needed on an auto |
| Throttle-kick / idle-air anti-lag | Opens the throttle a little off-throttle with heavy retard (milder ALS) | Some | Still exhaust heat; still pops | No for daily use |
| Turbo sizing | Smaller or ball-bearing turbos, more cubic inches, a stall converter on an auto | Real and permanent | None added | Yes: the reliable fix |
| E-turbo (electric assist) | Motor on the turbo shaft spins it before exhaust flow arrives | Best possible | n/a | Not available: Garrett's E-Turbo is an OEM 48V/400V product; no aftermarket street kit found 10/24 |

**Honest summary:** true anti-lag is a race tool. It trades parts for response. On a street car
with cats it burns the cats out, it puts the exhaust valves through the same heat that burnt the
Cruze valve, and it is loud enough to draw attention on NC roads. Neither turbo car should run it.
The reliable answer is the right turbo size, a good converter (Cutlass), and the ECU's boost
control.

### NC legal check

- **Catalytic converters:** G.S. 20-128(c): any car registered in NC and made after model year
  1967 must keep the emissions devices it was built with, connected. Both turbo cars came with
  cats. Anti-lag burns cats out, which is then a tampering problem. Civil penalty for tampering:
  G.S. 20-183.8A and 19A NCAC 03D .0542 (lists the cat, EGR, PCV, O2 sensor and more).
- **Exhaust noise and cutouts:** G.S. 20-128(a) requires a muffler in good working order to
  prevent "excessive or unusual noise"; 20-128(b) makes a muffler cutout illegal on a highway.
  Anti-lag bangs fall under (a). The Cutlass front dumps stay closed on public roads (already
  noted in the Cutlass file).
- **Emissions inspection:** G.S. 20-183.2(b) covers cars within 20 model years. The 1979 is out.
  S.L. 2023-134 removed 18 counties from the emissions test program; only Mecklenburg was still
  in, and EPA proposed approving the end of testing in May 2026. Person County is not in the
  program, so the Cruze gets a safety inspection only. Exempt from the test is not exempt from
  20-128(c): the cat stays.

### Cutlass: recommended setup

**What to run:** soft anti-lag through the Holley Terminator X Max that is already in the parts
list. No ALS.

- **ECU:** Holley Terminator X Max 550-933 (drive-by-wire, LS truck/LS2/LS3; $1,999.95 at Holley,
  checked 10/24; the 550-933T laptop-only version is $1,949.95). Already budgeted. Holley lists
  boost control by time, gear, rpm and speed, boost safeties, single or dual wastegate control,
  multiple 2-step strategies, launch boost targets and launch retard, and 4L80E control on the Max.
- **What the Terminator X does not list:** Holley's "Boost Builder" (timing, fuel and nitrous
  strategy to build boost on the line, also usable as anti-lag) is on the Dominator and HP, not
  the Terminator X (Holley's comparison table; confirm in the current spec sheet). Tim does not
  need it.
- **If he ever wants true ALS or rolling anti-lag:** Holley Dominator (Boost Builder), Haltech
  Elite 2500 (lists closed-throttle anti-lag and rolling anti-lag; about $1,760-1,960 bare ECU,
  checked 10/24, plus an LS harness) or FuelTech FT550 (2-step, built-in boost control, gear-based
  timing; about $900 for the LS550 harness alone; anti-lag not confirmed). Not recommended for this
  car.
- **Turbos:** keep ball-bearing 62 mm class twins. The Precision 6266 Gen2 is ball bearing only and
  rated about 800 hp each, so the pair is loafing at the 800-1,000 hp target. The Speed Engineering
  A/F-body kit uses Precision 62 mm turbos ($2,999.99-3,299.99 listed, checked 10/24; bearing type
  not listed: ask). Faster-spool option if Tim cares more about response than top end: Garrett
  G25-660 pair (ball bearing; price estimate $1,900-2,400 each, not checked). With a 402-408 ci
  stroker, twin 62s should hit full boost early (estimate: around 3,000-3,500 rpm under load).
  Electric turbo: not an option.
- **Converter (the real street "anti-lag" on an automatic):** have Circle D or Yank build the
  4L80E converter for the twins, about 3,000-3,200 stall (estimate; give them the cam card, turbo
  size, rear gear 3.50 and weight). Too tight and the turbos can't spool off the line; too loose and
  it heats the fluid on the street. Already in the trans line; this is a spec, not a new part.
- **Boost control hardware:** Turbosmart GenV CompGate40 x2 (already listed) have top and bottom
  dome ports. Add a Holley high-flow dual solenoid (557-202, $134.95 at EFI System Pro, checked
  10/24) or the dual-solenoid kit (557-201, $460.95 listed) so the ECU can control the domes.
  Without one, boost is spring pressure only (fine for break-in).

**How it gets tuned (on the dyno, after the 500-mile break-in):**
1. Base: wastegate springs at the low target (about 7-8 psi). Boost safeties first: overboost cut
   about 2 psi over target, lean cut, knock and oil pressure cuts, coolant over 220 F cuts boost.
2. Boost by gear: low in 1st and 2nd (spring pressure), full target from 3rd up. Boost by speed
   as the backup if the trans gear signal ever drops out.
3. Launch: 2-step around 2,500-3,500 rpm (set on the dyno and at the track), launch boost target
   modest, launch retard only as much as needed, timed out after a few seconds, armed by a console
   switch so it never works by accident. Use it at the strip, not on the street.
4. Boost by time after launch so the tires hook, then hand off to boost by gear.
5. Datalog EGT if fitted (optional EGT probes per bank, estimate $150-400), AFR per bank, knock.
6. No rolling anti-lag, no throttle-kick ALS, no decel pops/crackle map (it kills cats).

**Optional parts (not in the total):**

| Part | Price | Note |
|---|---|---|
| Holley 557-202 high-flow dual solenoid | $134.95 (checked 10/24) | Dome control for the CompGates. Or the 557-201 kit at $460.95 listed |
| Console arm switch for the 2-step | $20-60 est | Keeps launch control off unless armed |
| EGT probes, one per bank, and a Holley input | $150-400 est | Watches turbo heat during launches |
| Garrett G25-660 pair instead of 62 mm (faster spool) | $3,800-4,800 est | Only if response matters more than top end |

### Cruze: recommended setup

**What to run:** no anti-lag. Let the ZZP tune run the boost.

- **Why not anti-lag:** the 1.4T is a small engine with one small turbo and cast exhaust parts.
  ALS heat lands on the exhaust valves (this car already burnt one), the turbine and the cat. No
  commercial Cruze tune lists it, and none should. It is a daily driver.
- **What the tunes offer (checked 10/24):** the ZZP Cruze/Sonic tune ($724.99) lists improved
  spool, more boost, adjusted wastegate tables, optimized torque management, higher rev limiters,
  quicker shifts and converter lock-up changes (autos), and "does not alter emissions". Launch
  control and no-lift shift are not listed. Trifecta lists No-Lift-Shift for manual cars on the
  2011-2015 Cruze 1.4T; no launch control listed. Ask ZZP whether their custom tune can add a
  launch rpm limit (manual) or no-lift shift; do not count on it.
- **Electronic boost control:** the 1.4T ECU already controls the wastegate. The tune sets boost
  by rpm and load, and torque management limits torque in low gears. That is the street version of
  "boost by gear". No add-on controller needed.
- **Turbo choice is the lag decision (Tim decided Z04 on 10/23):**
  - ZZP Z04 kit, $1,999.99 (checked 10/24): journal bearing, nearly double stock power, about
    30-50 whp over a maxed V3; ZZP says it spools about 500-700 rpm later than a good stock or V3
    turbo. Kit includes a 3 inch downpipe with high-flow cat, wideband bung, coolant lines. ZZP
    strongly recommends an upgraded rear trans mount, 3 inch cat-back, intercooler, 42 lb/hr
    injectors on 93.
  - ZZP V3.2 Big Wheel, $899.99 (checked 10/24): about 30-50 whp over stock at the same boost;
    ZZP says it doesn't spool much, if any, slower than stock. Needs a tune; 42 lb/hr injectors on
    most setups. Less power, less lag, less stress, about $1,100 cheaper.
  - For "reliability first, daily driver, least lag": the V3.2 is the better match. For the most
    power the forged pistons allow: the Z04, and accept the later spool. Both bolt on with no
    teardown. **Tim decides** (see below).
- **Manual or automatic:** the file doesn't say. A 2012 LT RS came either way (6-speed auto or
  6-speed manual). No-lift shift only matters on a manual. Tim: confirm.

**How it gets tuned:** ZZP tune with the turbo kit (email tune with an MPVI rental, or in person),
then datalogs after break-in: knock retard near zero, AFR on target, boost on target, no
overshoot. Run dexos1 Gen 2 or newer oil (pre-ignition). No crackle tune (ZZP offers one by
request): it is a mild decel pop map and it heats the cat and exhaust valves.

**Optional parts (not in the total):**

| Part | Price | Note |
|---|---|---|
| ZZP V3.2 Big Wheel instead of the Z04 | $899.99 (checked 10/24) | Saves about $1,100; spools like stock; needs tune and injectors |
| Upgraded rear trans mount | $60-150 est | ZZP strongly recommends it with the Z04; useful with any tune |

---

## Part 2: Centrifugal vs traditional superchargers (Charger)

Plan as of 10/23: forged 392, Whipple Gen 6 3.0L twin-screw (WK-3021-30, $8,899.99-8,999.99
checked 10/23), 8HP90, street, reliability first, about 575-600 whp, widebody look.

### Comparison

| Factor | Centrifugal (ProCharger, Vortech, Paxton) | Roots (Magnuson TVS, Edelbrock E-Force) | Twin-screw (Whipple) |
|---|---|---|---|
| Power curve | Boost rises with rpm; full boost only near redline. Peak power strong, mid-range soft | Near full boost from low rpm; flat torque | Near full boost from low rpm; flat torque, strong to redline |
| Low-end torque | Weakest | Strongest hit off idle | Very strong (close to roots) |
| Heat / intercooling | Coolest and most efficient; air-to-air or air-to-water intercooler in front | Hottest at higher boost; needs the kit intercooler | Cooler than roots, hotter than centrifugal; heat soak in traffic and back-to-back pulls |
| Efficiency at boost | Highest (less power to drive, less heat) | Lowest, worst at higher boost | Middle |
| Drivetrain stress | Lowest: torque comes late, easier traction | High: big torque early | High: big torque early. Needs low-gear torque management |
| Street drivability | Feels like a bigger NA engine until high rpm; part-throttle very stock | Instant, OEM-like; can be too much on wet roads | Instant, OEM-like ("always on"); bypass valve keeps cruise near stock |
| Sound | Whistle plus blow-off valve chirp | Mild whine | Strong whine, the classic blower sound |
| Fuel economy | Near stock at cruise | Near stock at cruise (bypass valve) | Near stock at cruise (bypass valve) |
| Cost (Charger) | ProCharger P-1SC-1 HO intercooled: from $7,149 (ProCharger, 5.7); complete 5.7 kits $8,099-8,424; 6.4 Stage II $9,499 (checked 10/24) | Magnuson TVS2650 $8,465-8,995 (checked 10/23) | Whipple 3.0L $8,899.99-8,999.99 (checked 10/23) |
| Install | Bracket, head unit, intercooler and piping in front; more pieces but no intake swap | Top mount, replaces the intake | Top mount, replaces the intake; intercooler built in |
| Tuning | Simple; boost set by pulley; belt slip at high rpm is the known issue (8-rib fix) | Pulley sets boost; bypass valve calibration | Pulley sets boost; bypass valve calibration; IAT management matters |
| Hood clearance | Fits under any hood | Magnuson lists every factory hood except the Shaker | Not listed for the Charger: confirm with Whipple (flag already in the guide) |
| Reliability | Very good; self-contained oil on ProCharger; least stress on the engine and trans | Very good; OEM-proven (Eaton TVS on factory cars) | Very good; more torque means the drivetrain is the limit, not the blower |

### Verdict

**Traditional (twin-screw) is better for Tim's Charger. Keep the Whipple.** Deciding reasons:

1. **Street car, street rpm.** Most driving happens between 1,500 and 4,500 rpm. The twin-screw
   makes near full boost there; a centrifugal makes its boost near redline, so for the same street
   feel it needs more peak boost and more peak power.
2. **Reliability at moderate boost.** Instant torque lets the 392 hit 575-600 whp at low boost
   (about 5.5-7 psi), so less heat and less detonation risk than chasing the same area under the
   curve with a centrifugal. The 8HP90 and Driveshaft Shop axles are already sized for the torque.
3. **One package.** The Whipple kit is made for the 6.4 and brings its intercooler, Hellcat
   injectors and rails in the box. Nothing hangs out front to block the widebody's bumper, splitter
   or cooling.
4. **The look and sound he wants.** The whine and the top-mount look match a traditional blower
   build. A widebody Charger is a "show and cruise" car more than a top-speed car.

**Where centrifugal would win:** cooler running on long hot pulls, less drivetrain shock, easier
traction, any-hood fit, a bit cheaper (from $7,149 for the 5.7 tuner/HO kits). If Tim's goal ever
changes to highway roll racing or the hood won't clear, the ProCharger is the switch. Not now.

### What should change

1. **Boost: about 5.5-6.5 psi, not 7.** National Speed results: a 2016 Challenger Scat Pack
   (stock 392) with the Whipple 3.0L at about 7.5 psi on 93 made 677 whp and 621 lb-ft at the
   wheels (manual trans). A 2018 Charger SRT 392 with the smaller Whipple 2.9L made 618 whp and 576
   lb-ft at 7 psi. Both are over the 575-600 whp target, and 621 lb-ft at the wheels is roughly 700
   lb-ft at the crank (estimate), at the top of the 8HP90 range (664-738 lb-ft). So: have Whipple
   and the tuner pick the pulley for the whp target, likely around 5.5-6.5 psi (estimate), and keep
   torque management on in 1st and 2nd. Same parts, same price, more margin. The 10/23 crank
   estimates (650-700 hp, 620-660 lb-ft at 7 psi) look low for a 392 at 7 psi.
2. **Heat exchanger upgrade:** keep it as the option already listed (only if IATs climb past
   about 130-140 F in logs).
3. **Hood:** still confirm stock Pursuit hood clearance with Whipple before buying.

Nothing else changes: same kit, same budget.

---

## What Tim decides

**Answered 10/24:** 1. Z04 (keep). 2. Both options written up; manual recommended (build-guides.md). 3. Yes to the 2-step; now in the plan. 4. Superseded: Tim raised the Charger to 800 whp (build-guides.md).

1. **Cruze turbo:** keep the Z04 (most power, spools 500-700 rpm later) or switch to the ZZP V3.2
   (about stock spool, less power, about $1,100 less, easier on the engine).
2. **Cruze transmission:** manual or automatic? (No-lift shift only exists for a manual.)
3. **Cutlass:** does he want a 2-step for track days? If yes, add the arm switch and dual solenoid;
   if no, boost by gear only.
4. **Charger:** OK to target about 575-600 whp (likely about 5.5-6.5 psi) instead of a fixed 7 psi?

---

## Sources (checked 10/24/2026)

- Antilag system overview, coolant cutout, turbo speed risk: https://en.wikipedia.org/wiki/Antilag_system
- Turbo temps 800 C to 1,100 C plus, manifold stress: https://rallycars.com/technical-stuff/bang-bang-or-anti-lag-system/
- ALS can destroy turbo, exhaust, valves and cat; not emissions legal; competition only: https://wiki.rusefi.com/Antilag
- Holley Terminator X features (boost by time/gear/rpm/speed, 2-step, launch retard): https://www.holley.com/blog/post/terminator_x_efi_for_ls_engines/
- Terminator X Max 550-933 price and DBW: https://www.holley.com/products/ls_power/ls_efi_systems/parts/550-933
- Holley ECU comparison (Boost Builder on HP and Dominator): https://www.holley.com/blog/post/which_holley_ecu_is_the_best_for_you_/
- Dominator Boost Builder usable as anti-lag: https://sdparts.com/holley-efi-550-650-dominator-efi-kit-ls1-h550-650/
- Holley 557-202 dual solenoid: https://www.efisystempro.com/add-on-modules/boost-control/manufacturer-holley_efi-holley
- Holley 557-201 kit: https://tre.dev.webshopmanager.com/product/holley-efi-high-flow-dual-solenoid-boost-control-kit
- Haltech Elite 2500 anti-lag and rolling anti-lag: https://berryperformancesales.com/products/haltech-elite-2500-ecu
- FuelTech FT550 features and LS harness: https://www.realstreetperformance.com/fueltech-ft550-efi-system-waterproof-standalone-ecu-ems-4-3-touchscreen-display-without-harness.html
- Precision 6266 Gen2 ball bearing only, 800 hp: https://www.full-race.com/store/nissan/sr20det-s13-s14-s15-silvia/62mm-precision-6266-gen2-cea-turbo
- Speed Engineering A/F-body twin kit price: https://berryperformancesales.com/products/speed-engineering-ls-swap-twin-turbo-kit-a-body-f-body-c10-trucks
- Garrett G30-770 price and ball bearing: https://www.rallysportdirect.com/products/garrett-g30-770-super-core-standard-rotation
- Garrett E-Turbo (OEM only): https://www.garrettmotion.com/newsroom/
- ZZP Z04 kit: https://zzperformance.com/products/zzp-z04-turbo-kit
- ZZP V3.2 Big Wheel: https://zzperformance.com/products/zzp-big-wheel-turbo
- ZZP Cruze/Sonic tune: https://zzperformance.com/products/zzp-cruze-sonic-tune
- Trifecta 2011-2015 Cruze 1.4T (No-Lift-Shift, manual): https://www.trifectaperformance.com/forums/store/product/2065-2011-2015-chevrolet-cruze-2016-cruze-limited-14l-turbo-advantage/
- NC G.S. 20-128 (muffler, cutout, emissions devices): https://ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_20/GS_20-128.html
- NC G.S. 20-183.2 (inspection model years): https://ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_20/GS_20-183.2.html
- NC tampering rule 19A NCAC 03D .0542: https://www.ncdot.gov:443/about-us/how-we-operate/policy-process/rules/Documents/19a-ncac-03d-0542.pdf
- NC I&M counties (S.L. 2023-134, EPA proposal 2026): https://deq.nc.gov/about/divisions/air-quality/motor-vehicles-and-air-quality/inspection-maintenance-im-program
- Supercharger types compared: https://jalopnik.com/1933856/roots-supercharger-pros-cons/ and https://en.wikipedia.org/wiki/Centrifugal-type_supercharger
- ProCharger Charger kits and prices: https://www.ProCharger.com/automotive-superchargers/dodge/2021-2011-chrysler-300-5-7/ and https://sdparts.com/i-24138616-procharger-1di415-sci-stage-ii-intercooled-system-with-p-1sc-1-2015-18-6-4-charger.html
- Whipple 3.0L on a 392 at 7.5 psi (677 whp, 621 lb-ft): https://nationalspeedinc.com/2016-dodge-challenger-r-t-scat-pack-whipple-3-0l-national-speed/
- Whipple 2.9L on a Charger SRT 392 at 7 psi (618 whp, 576 lb-ft): https://nationalspeedinc.com/2018-dodge-charger-srt-392-whipple-supercharged-2/
- ProCharger belt slip and heat soak test: https://www.enginelabs.com/?p=12835
