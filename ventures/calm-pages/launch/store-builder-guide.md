# Peace by Page: Store Builder Guide

Click-by-click build of payhip.com/PeaceByPage in Payhip's Store Builder. About 40 minutes on a laptop (the builder works on a phone, but the side panel is cramped). Written 10/6 for the 10/10 launch. Google Doc copy: "Peace by Page: Store Builder Guide" (1i6xxiF8ftmSakmafwA5YS3M0oWx9PUSBcft1UjHHb60) in Drive > 05 Peace by Page > Launch Docs.

**Before you start**
- Upload the 15 products and the free sampler first (`upload-packets.md`), and create the three collections: Calm Wings, Calm Petals, Calm Nights. The store buttons below link to them.
- Unzip `PeaceByPage_StoreImages.zip`. Every file named below is in it. Also have `payhip-logo.png` from the Brand folder.
- Payhip's free plan has every builder feature (Payhip: "no feature-gating"). You pay 5% per sale, nothing monthly.
- Click **Publish** at the end of each part. Nothing goes live until you do, so you can stop and come back.

**Words to never type into the store:** treats, cures, heals, therapy (as what we sell), relief (as a promise), clinically proven.

---

## What the builder can and can't do (read once)

From Payhip's help center, checked 10/6:

| Thing | Status |
|---|---|
| Pages made of sections; **Add section** adds one | Yes, all plans |
| Sections we use: Image with Text, Basic List (Three in a Row / Text List), Newsletter, FAQs, Text, Collection, About Me, Contact Us | Yes |
| Header navigation links, announcement bar, footer links, social icons | Yes |
| Colors (5 schemes: white, light, dark, black, highlight) and fonts | Yes |
| Fixed image sizes | **None.** Payhip says pick an aspect ratio in each section. Our images are square or 4:3, with the important parts in the middle. |
| Favicon | Only shows once a custom domain (peacebypage.com) is connected |
| Embed Code section, header/footer code, outside email signup forms | **Custom domain only** |
| Newsletter section | Saves emails to your Payhip followers list. Export them by hand until an email tool is connected. |
| Free sampler as list builder | Works now: a $0 product collects the buyer's email |
| Testimonials section | Skip until real reviews come in. Never invent reviews. |
| TikTok icon | Not in Payhip's social list (Instagram, YouTube, Facebook, Twitter, Pinterest). Use a footer text link. |
| Contact form fields | Fixed. Only the heading and text can change. Messages go to your Payhip login email. |

Where a label below is a guess (the help center doesn't show it), the step says "(or similar)".

---

## Part A: Look and feel (8 min)

**1. Open the builder.** Payhip > **Store** (top bar) > **Launch Your Store Builder**. (Or **Account** > **Store Builder**.)

**2. Pick a light theme first.** Left panel: **Change store style** > **Themes** > **Switch to another theme**. Preview **Cream** and **Oasis**; choose whichever looks lightest and most open on the phone preview (dropdown at top right). If the current theme already looks clean and light, keep it.
Switch themes before step 3: switching clears colors, fonts and custom CSS.

**3. Colors.** **Change store style** > **Colors** > **Start Editing Your Colors**. Set:

| Scheme / item | Background | Text | Headings | Buttons (fill / text) |
|---|---|---|---|---|
| White (default) | `#FFFFFF` | `#3E4050` | `#7E6BB5` | `#6B5AA6` / `#FFFFFF` |
| Light | `#F6F3FB` | `#3E4050` | `#7E6BB5` | `#6B5AA6` / `#FFFFFF` |
| Highlight | `#E7DFF5` | `#3E4050` | `#3E4050` | `#6B5AA6` / `#FFFFFF` |
| Announcement bar | `#6B5AA6` | `#FFFFFF` | | |
| Footer | `#F6F3FB` | `#3E4050` | | |
| Links | | `#6B5AA6` | | |

Buttons use `#6B5AA6`, one shade deeper than the logo violet `#7E6BB5`, so white button text is easy to read (contrast 5.8:1). Leave dark and black schemes alone; we don't use them.
Edition accents, if a field asks: Wings `#7E6BB5`, Petals `#587D69`, Nights `#3D4180`. Soft fills: mint `#D7EEEA`, peach `#FBE2D3`.

**4. Fonts.** **Change store style** > **Fonts**. Payhip's list varies by theme; pick the first one that's there:
- Headings: **Cormorant Garamond**, then Lora, Playfair Display, Libre Baskerville (italic if offered; it matches the logo)
- Body, buttons, menu: **Nunito Sans**, then Nunito, Lato, Open Sans
- Size: body at least 16 px if there's a size control

Optional, only if none of those are in the list: **Change store style** > **Advanced** > **Store Pages Custom CSS**, paste:
```
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500&family=Nunito+Sans:wght@400;700&display=swap');
h1, h2, h3, h4, .custom-style-font-heading { font-family: 'Cormorant Garamond', serif; font-style: italic; }
body, .btn, .custom-style-font-regular, .custom-style-font-button { font-family: 'Nunito Sans', sans-serif; }
```

**5. Header logo.** Click **Header** (left panel) > logo / image field (or similar) > upload `header-logo.png`. If it looks tiny on the phone preview, use `payhip-logo.png` (square) instead.

**6. Announcement bar.** **Header** > **Announcement Bar**:
- Show announcement: **on**
- Home page only: **off**
- Text: `New here? Try a week of calm pages with our free 7-day sampler.`
- Link: pick the **Free 7-Day Anxiety Journal Sampler** product

Click **Publish**.

---

## Part B: Create the pages (4 min)

**7.** Top left: **Add** > **Custom Page**. Make four, one at a time (type the title, click **Add**):
`Home`, `About`, `FAQ`, `Policies`

For each, click the cog by the page name > page settings:
- **General**: leave the URL as Payhip makes it; visibility public
- **SEO** tab, SEO description for Home: `Gentle printable anxiety journals in three editions: Calm Wings, Calm Petals and Calm Nights. Five minutes a day. Free 7-day sampler.`
- SEO description for About: `Why Peace by Page makes gentle printable journals for anyone who worries.`
- SEO description for FAQ: `Answers about downloads, printing, refunds, licensing and how Peace by Page journals work.`
- SEO description for Policies: `Refund, delivery, terms of use and privacy for Peace by Page printables.`
- **Social Media** tab: upload `social-share.png` (all four pages)

The **Contact** page already exists. The **All Products** page becomes "Shop".

---

## Part C: Build the Home page (15 min)

Open the page dropdown (top left) > **Home**. Delete any placeholder sections (hover > three dots > **Delete section**). Then **Add section** eight times, in this order:

**8. Hero: Image with Text**
- Image: `hero-art.png` (4:3). Image on the right if there's a side option; on phones it stacks above the text.
- Color scheme: Light
- Heading: `Five calm minutes a day`
- Text:
```
Gentle printable journals for anyone who worries. Undated daily pages, CBT-inspired prompts and coloring pages, in three editions. Download, print at home, start any day.
```
- Button text: `Choose your edition`  Button link: **All Products**

Option B, if you want a full-width banner instead: add a **Slideshow** section with one slide, image `hero-desktop.png` (text is in the image, so leave the slide heading blank; button `Shop the journals` to All Products). If the slide has a mobile image field, use `hero-mobile.png`. Check the phone preview; if the words in the image look small, go back to the Image with Text hero.

**9. Choose your edition: Basic List, Three in a Row**
- Color scheme: White
- Section heading: `Choose your edition`
- Section text: `Same 90 days of pages. Pick the art that feels like you.`
- Image aspect ratio (if asked): square / 1:1
- Item 1: image `edition-calm-wings.png`, title `Calm Wings`, text `Soft butterflies in lavender and mint. The original edition.`, button `Shop Calm Wings` > link: Calm Wings collection
- Item 2: image `edition-calm-petals.png`, title `Calm Petals`, text `Gentle botanicals in sage and blush.`, button `Shop Calm Petals` > Calm Petals collection
- Item 3: image `edition-calm-nights.png`, title `Calm Nights`, text `Moon and stars in navy and gold, with extra pages for winding down at night.`, button `Shop Calm Nights` > Calm Nights collection

If the link picker doesn't list collections: Payhip > Products > Collections, open each one, copy its link, paste it (starts with https://).

**10. Free sampler: Image with Text**
- Image: `free-sampler.png`. Image on the left (so it alternates with the hero).
- Color scheme: Highlight
- Heading: `Try a week, free`
- Text:
```
Not sure yet? The free 7-day sampler has seven daily pages, a week 1 review, a coloring page and a pocket SOS card. Print it tonight and see how it feels.
```
- Button: `Get the free sampler` > link: the sampler product

**11. How it works: Basic List, Text List**
- Color scheme: White
- Heading: `How it works`
- Item 1: `Download` / `Your files arrive right after checkout, in US Letter and A4.`
- Item 2: `Print` / `Print at home or at a print shop. Print the whole journal or a week at a time.`
- Item 3: `Five minutes a day` / `A few ratings, three good things, one worry and a kinder way to see it, and one small step for tomorrow.`

**12. What's in each edition: Basic List, Text List**
- Color scheme: Light
- Heading: `What's in each edition`
- Text: `Every edition has the same five printables. Every file comes in US Letter and A4.`
- Item 1: `90-Day Anxiety Journal, $11.99` / `About 170 undated pages: daily pages, weekly check-ins, an SOS toolkit, monthly mood pages and coloring rewards.`
- Item 2: `Complete Bundle, $16.99` / `The journal, the coloring pack and the mood tracker together.`
- Item 3: `Coloring Pack, $4.99` / `18 calming coloring designs plus a color-to-calm tips page.`
- Item 4: `SOS Calm-Down Kit, $3.99` / `The 10-page toolkit for hard moments: breathing, grounding and a pocket card.`
- Item 5: `Mood Tracker, $2.99` / `12 undated months. Color one cell a day and see your year at a glance.`
- Button (if offered): `Shop all printables` > All Products

**13. Newsletter**
- Color scheme: Highlight
- Heading: `Gentle notes, now and then`
- Text: `New printables and the occasional calm idea. No spam, and you can leave any time.`
- Button: `Join`

**14. About teaser: Image with Text**
- Image: `about.png`, image on the right
- Color scheme: White
- Heading: `Made for anyone who worries`
- Text:
```
Each page draws on well-known self-help ideas like thought records, worry time, grounding and gratitude writing, and takes about five minutes. Skip a day? Pick up where you left off.
```
- Button: `Read our story` > About

**15. Help and disclaimer: Text** (this one gets saved and reused)
- Color scheme: Light
- Heading: `If you need help now`
- Text:
```
In the US, call or text 988 (Suicide and Crisis Lifeline), free and confidential, 24/7. You can also text HOME to 741741. In an emergency, call 911. Outside the US, call your local emergency number or visit findahelpline.com.

Peace by Page journals are self-reflection tools for general wellbeing. They are not medical advice, diagnosis or treatment, and they support, not replace, care from a licensed professional.
```
- Click the section > **Save to Library**. Name it `Help and disclaimer`.

**16. Make Home the homepage.** Cog next to the page name > **Set As Homepage**. Click **Publish**.

---

## Part D: Shop page (All Products) (4 min)

**17.** Page dropdown > **All Products**.
- **Collection** section > **Settings**, heading (if there is one): `Shop all printables`
- **Collection** section > **Settings** > **Aspect ratio**: `1:1` (our product images are square)
- **Collection** section columns: 3 on desktop; under **Mobile Layout**, 2
- Click **About Me**: image `payhip-logo.png`, heading `Hi, and welcome`, text:
```
We make gentle printable journals for anyone who worries. Five minutes a day, undated pages, three editions. Not sure yet? Start with the free 7-day sampler.
```

- About Me > Advanced > **Show social media icons**: Yes (after step 26).
- **Add section** > **Saved Section** > `Help and disclaimer` at the bottom.

---

## Part E: About, FAQ, Policies, Contact (8 min)

**18. About page.** Page dropdown > **About**.
- Add **Image with Text**: image `about.png`, heading `About Peace by Page`, text: the full About text from `store-branding.md` (block "Store About text"), minus the last two paragraphs (they live in the help section below). Button: `Get the free sampler` > sampler product.
- Add **Saved Section** > `Help and disclaimer`.

**19. FAQ page.** Page dropdown > **FAQ**. **Add section** > **FAQs**. Heading: `Questions, answered`. Add these seven:

Q: `How do I get my files?`
```
Everything here is a digital download. Your download link appears on screen right after checkout and is emailed to you. Nothing is mailed. Can't find the email? Check spam or promotions, or write to us and we'll resend it.
```

Q: `What paper size do I need, and how do I print?`
```
Every file comes in US Letter (US and Canada) and A4 (most other countries). Print at home on plain paper at "Actual size", or take the file to a print shop. You can print the whole journal or a week at a time. Bundles come as zip files: on an iPhone, tap the zip in the Files app; on Android, open it in Files by Google; on a computer, double-click it.
```

Q: `Which edition should I pick?`
```
All three have the same pages and prompts. Only the art changes: Calm Wings has butterflies, Calm Petals has botanicals, and Calm Nights has the moon and stars, with extra pages for winding down at night. Pick the one you'd like to open each day.
```

Q: `Can I use it on a tablet?`
```
Yes. The files are standard PDFs, so you can open them in a PDF note-taking app on your own devices and write with a stylus. They are made for printing, so the writing spaces are not typeable form fields.
```

Q: `What is your refund policy?`
```
Because these are digital files, sales are final once a file has been downloaded. If a file won't open, prints wrong or something is missing, write to us and we'll fix it or send a working file. If we can't fix it, we'll refund you. Bought the same item twice by mistake? Write to us within 14 days.
```

Q: `Can I share the files or use them with clients?`
```
Your purchase includes a personal-use license: print as many copies as you need for yourself and your household. Please don't share, resell or upload the files. Counselors, teachers and support groups can ask us about a group license.
```

Q: `Is this a replacement for therapy or medical care?`
```
No. Our journals are self-reflection tools for general wellbeing. They are not medical advice, diagnosis or treatment, and they support, not replace, care from a licensed professional. If anxiety is getting in the way of daily life, please talk with a doctor or a licensed mental health professional. In the US, you can call or text 988 any time.
```

Then **Add section** > **Saved Section** > `Help and disclaimer`.

**20. Policies page.** Page dropdown > **Policies**. Add four **Text** sections, one per block from `policies.md`, heading = the block's first line:
1. `Refund policy` (block 1)
2. `Digital delivery` (block 2)
3. `Terms of use` (block 3)
4. `Privacy` (block 4)

Then **Saved Section** > `Help and disclaimer` (it covers blocks 5 and 6).
If Payhip's account settings also have store policy fields, paste the same blocks there.

**21. Contact page.** Page dropdown > **Contact** > **Contact Us** section:
- Heading: `Say hello`
- Text:
```
Questions about a file, printing or a group license? Send us a note and we'll write back within two business days. If you are in crisis, please don't wait for us: in the US, call or text 988, or call 911 in an emergency.
```

Click **Publish**.

---

## Part F: Menu and footer (5 min)

**22. Menu.** **Header** > **Navigation Links** > **Edit Navigation Links**. Remove the defaults, then **+ Add Link** for each, in this order:

| Label | Links to |
|---|---|
| `Shop` | All Products |
| `Collections` | If the menu supports a dropdown, nest Calm Wings, Calm Petals, Calm Nights under it. If not, add the three as their own links (`Calm Wings`, `Calm Petals`, `Calm Nights`) instead of "Collections". |
| `Free Sampler` | the sampler product |
| `About` | About |
| `FAQ` | FAQ |
| `Contact` | Contact |

On a phone these fold into the menu icon, so 6 to 8 links is fine.

**23. Footer.** Click **Footer**:
- Footer type: **Simple** (needed for social icons)
- Links: `Shop`, `Free Sampler`, `FAQ`, `Contact`, `Refund policy` (Policies page), `Terms of use` (Policies page), `Privacy` (Policies page)
- Footer text, if there's a text field:
```
Peace by Page journals support, not replace, professional care. In crisis in the US, call or text 988.
```
- Show social media icons: **Yes**
- **Advanced** > **Format** > **Show powered by Payhip**: your call. Keep it (free) or pick **No** to hide it.

**24.** Click **Publish**.

---

## Part G: Account settings and phone check (5 min)

**25. Store name and tagline** (Settings > Your Store, or similar): name `Peace by Page`, tagline `Calming printable journals. One page at a time.`

**26. Social links** (Settings > **Your Store** tab): Facebook page and Pinterest (`https://www.pinterest.com/Peacebypage/`) now. Instagram after 10/18 when the account is warmed up. TikTok has no icon slot; skip it.

**27. Phone check.** Open payhip.com/PeaceByPage on your phone and tap through:
- [ ] Home loads with the hero, three editions, sampler, newsletter and help block
- [ ] Each "Shop Calm ___" button opens the right collection
- [ ] "Get the free sampler" opens the $0 sampler
- [ ] Menu opens and every link works
- [ ] Shop page shows square product images in 2 columns
- [ ] FAQ answers open and close
- [ ] Footer links reach the Policies page
- [ ] No cut-off words in any image (if the hero is cramped, switch to Option B or back)

Done. Tell Jarvis "store built" and anything that looked off.

---

## File list (in `PeaceByPage_StoreImages.zip`)

| File | Size | Where it goes |
|---|---|---|
| `hero-art.png` | 1600 x 1200 | Home hero (Image with Text) |
| `hero-desktop.png` | 2400 x 1000 | Option B hero (Slideshow) |
| `hero-mobile.png` | 1080 x 1350 | Option B hero, mobile image if offered |
| `edition-calm-wings.png` | 1200 x 1200 | Choose your edition, item 1 (also a good collection image) |
| `edition-calm-petals.png` | 1200 x 1200 | item 2 |
| `edition-calm-nights.png` | 1200 x 1200 | item 3 |
| `free-sampler.png` | 1200 x 1200 | Free sampler section; also usable as the sampler's product image 1 |
| `about.png` | 1200 x 1200 | About teaser and About page |
| `header-logo.png` | 1200 x 300, transparent | Header logo |
| `social-share.png` | 1200 x 630 | Social Media tab on each custom page |
| `payhip-logo.png` | 1000 x 1000 | About Me section (from the Brand folder) |

Rebuild with `python3 launch/make_store_assets.py` (from `ventures/calm-pages/`). Images are rendered from the real product PDFs.

Sources: Payhip help center articles Store Builder, Custom Page, Basic List Section, Add Extra Buttons, Testimonials Section, Optimize Product Images, Add an Announcement Bar, Add Social Profiles, Remove "Powered by Payhip", Add a Favicon, Switching Themes, Custom Fonts, Newsletters, Embed Code, Add Header or Footer Code, Contact Form, Saved Sections, Use Payhip as a Lead Magnet; payhip.com/pricing; payhip.com/blog/new-themes-and-sections (all read 10/6/2026).
