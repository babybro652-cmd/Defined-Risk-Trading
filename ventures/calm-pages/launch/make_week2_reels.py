"""Peace by Page reels, week of 11/3/2026 (V6-V12). Same engine as make_launch_content.videos().
Run: python3 launch/make_week2_reels.py  -> launch/content/videos/6-...mp4 to 12-...mp4"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_launch_content import PDF, PG, SAMPLER, Card, end_card, page_layer, render_video  # noqa: E402


def main():
    w, p, n = PDF["wings"]["journal"], PDF["petals"]["journal"], PDF["nights"]["journal"]
    render_video("6-box-breathing", "wings", [
        Card(page_layer(w, PG["wings"]["box"]), "A 1-minute reset you can do anywhere", enter="fade"),
        Card(page_layer(w, PG["wings"]["box"], width=880), "Trace the square. In for 4.", 2.8),
        Card(page_layer(w, PG["wings"]["box"], width=880), "Hold for 4. Out for 4. Hold for 4.", 2.8),
        Card(page_layer(w, PG["wings"]["sos"]), "It lives in the SOS pages of every journal"),
    ], end_card("wings", "Calm Wings  |  link in bio", "Save this for a hard moment"))
    render_video("7-grounding-54321", "petals", [
        Card(page_layer(p, PG["petals"]["ground"]), "When your thoughts are racing, try this", enter="fade"),
        Card(page_layer(p, PG["petals"]["ground"], width=880), "5 things you can see. 4 you can feel.", 2.8),
        Card(page_layer(p, PG["petals"]["ground"], width=880), "3 you can hear. 2 you can smell. 1 you can taste.", 3.0),
        Card(page_layer(p, PG["petals"]["sos"]), "Written down, so you don't have to remember it"),
    ], end_card("petals", "Calm Petals  |  link in bio", "Save this for later"))
    render_video("8-balanced-thought", "wings", [
        Card(page_layer(w, PG["wings"]["day1"]), "Name one worry. Then write it again, kinder.", enter="fade"),
        Card(page_layer(w, PG["wings"]["thought"]), "Not forced positive. Just more balanced."),
        Card(page_layer(w, PG["wings"]["day1"] + 3), "A few minutes a day, one page at a time"),
    ], end_card("wings", "Calm Wings  |  link in bio", "Free 7-day sampler in the shop"))
    render_video("9-i-handled-it", "nights", [
        Card(page_layer(n, PG["nights"]["handled"]), "Once a week: what did you handle?", enter="fade"),
        Card(page_layer(n, PG["nights"]["handled"], width=880), "The hard thing, what you did, how it went", 2.8),
        Card(page_layer(n, PG["nights"]["reward"]), "Then a page to color. You earned it."),
    ], end_card("nights", "Calm Nights  |  link in bio", "Letter + A4  |  instant download"))
    render_video("10-mood-petals", "petals", [
        Card(page_layer(PDF["petals"]["mood"], 3), "Color one petal a day for your mood", enter="fade"),
        Card(page_layer(PDF["petals"]["mood"], 3, width=880), "Pick a color for each feeling", 2.8),
        Card(page_layer(PDF["petals"]["mood"], 5), "At the end of the month, you can see the pattern"),
    ], end_card("petals", "Mood tracker  |  link in bio", "12 undated months"))
    render_video("11-three-good-things", "wings", [
        Card(page_layer(w, PG["wings"]["day1"] + 1), "Three good things. They can be small.", enter="fade"),
        Card(page_layer(w, PG["wings"]["day1"] + 1, width=880), "Coffee. A text back. Getting outside.", 2.8),
        Card(page_layer(SAMPLER, 3), "Try it free for 7 days"),
    ], end_card("sampler", "Free sampler  |  link in bio", "Letter + A4  |  $0"))
    render_video("12-worry-time", "nights", [
        Card(page_layer(n, PG["nights"]["worry"]), "Worries at bedtime? Give them a time slot.", enter="fade"),
        Card(page_layer(n, PG["nights"]["worry"], width=880), "Write them down. Pick 15 minutes tomorrow.", 2.8),
        Card(page_layer(n, PG["nights"]["winddown"]), "Then a wind-down list for tonight"),
    ], end_card("nights", "Calm Nights  |  link in bio", "Letter + A4  |  instant download"))


if __name__ == "__main__":
    main()
