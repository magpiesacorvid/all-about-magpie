<style>
  :root {
    --bg: #242424;
    --text: #e6edf3;
    --link: #58a6ff;
    --border: #444;
  }
  body.light-mode {
    --bg: #ffffff;
    --text: #1f2328;
    --link: #0969da;
    --border: #d0d7de;
  }
  body {
    background-color: var(--bg);
    color: var(--text);
    transition: background-color 0.2s ease, color 0.2s ease;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }
  a { color: var(--link); }
  table {
    background-color: transparent;
    border-collapse: collapse;
    margin: 0 auto;
  }
  th, td {
    background-color: transparent !important;
    color: var(--text);
    text-align: center !important;
    vertical-align: middle;
    border: 1px solid var(--border);
    padding: 8px 14px;
  }
  #theme-toggle-btn {
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 1000;
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text);
    cursor: pointer;
    font-size: 14px;
  }
</style>

<button id="theme-toggle-btn" onclick="toggleTheme()">Light Mode</button>

<script>
  function applyTheme(mode) {
    if (mode === "light") {
      document.body.classList.add("light-mode");
      document.getElementById("theme-toggle-btn").textContent = "Dark Mode";
    } else {
      document.body.classList.remove("light-mode");
      document.getElementById("theme-toggle-btn").textContent = "Light Mode";
    }
  }

  function toggleTheme() {
    const isLight = document.body.classList.contains("light-mode");
    const next = isLight ? "dark" : "light";
    localStorage.setItem("theme", next);
    applyTheme(next);
  }

  (function () {
    const saved = localStorage.getItem("theme") || "dark";
    applyTheme(saved);
  })();
</script>

<h2 align="center">Oh I LOVE TALKING!! HELLO!!! (They/Them, Adult)</h2>

<p align="center"><img src="https://komarev.com/ghpvc/?username=magpiesacorvid&color=blue" alt="Profile Views"></p>

<h1 align="center">LOOK AT MY REPOSITORIES, I MADE AN ANIMAL GENERATOR!</h1>

<p align="center">
  <img src="https://i.pinimg.com/736x/e8/c7/bf/e8c7bf72f3714cabf94ce214acaf26c2.jpg" alt="Banner" width="300">
</p>

<p align="center">Hello!!! You can call me Magpie!! You'll usually see me near the Overwatch and Deadlock area on Pony Town, maaaaybe the library too!<br>
I wouldn't call myself a gamer, those are like, the ONLY games I've ever played.<br>
Catch me playing Celeste, Paige, Silver, D.va, Vendetta and Lucio, in that order of most to least likely..<br>
I'm a musician, and a linguist, and I LOOOOOVE animals so freaking much, I have over 4,000 animal images saved on my computer, my favourite animal is either a Magpie (durr) or an African Palm Civet!!!!!!!<br>
I have about 30 string instruments, ASK ME ABOUT THEM!!!!!!!!! I say about.. it's probably more.. i like WRITING and READING not maths.. blargh!!<br>
My Discord is 7forasecret, my Twitter is magpiencorvid and my steam is "Super Evil Bloodthirsty Unicorn", add me ANYWHERE i love TALKING..</p>

<p align="center">
  <img src="https://i.pinimg.com/1200x/43/95/ee/4395ee0d213df6c0b0a74d14de51dafe.jpg" alt="Banner" width="300">
</p>

<p align="center">
  <img src="https://i.pinimg.com/1200x/41/14/42/4114421c7804e65db4df3243fdb17724.jpg" alt="Banner" width="300">
</p>

<p align="center">Yeah... That's everything.. FOR NOW!!!!!!!!!<br>
I'm the worst player EVER!! Evidence BELOW...</p>

<!-- START_STATS -->

<h2 align="center">Game Stats</h2>

<h3 align="center"><img src="https://cdn.fastly.steamstatic.com/apps/deadlock/images/react/oldgods/rem_helper.png?2" height="22" valign="middle"> <span style="color:#eedfbf">Deadlock</span> <img src="https://cdn.fastly.steamstatic.com/apps/deadlock/images/react/oldgods/rem_helper.png?2" height="22" valign="middle"></h3>

<p align="center">Wins: 14<br>Losses: 14<br>Win Rate: 50.0%</p>

<h4 align="center">Heroes</h4>

<div align="center" markdown="1">

| Celeste | Silver | Paige | Ivy |
|:---:|:---:|:---:|:---:|
| <img src="https://deadlock.wiki/images/7/70/Celeste_Gloat.png" width="60"> | <img src="https://deadlock.wiki/images/4/44/Silver_Gloat_Portrait.png" width="60"> | <img src="https://deadlock.wiki/images/0/02/Paige_Critical.png" width="60"> | <img src="https://deadlock.wiki/images/3/37/Ivy_Critical_.png" width="60"> |
| 11W - 9L (55.0%) | 3W - 2L (60.0%) | 0W - 2L (0.0%) | 0W - 1L (0.0%) |

</div>

<h3 align="center"><img src="https://cdn.betterttv.net/emote/698afc803df753bf3f83fcbd/3x.webp" height="22" valign="middle"> Ove<span style="color:#ef6414">rwa</span>tch <img src="https://cdn.betterttv.net/emote/698afc803df753bf3f83fcbd/3x.webp" height="22" valign="middle"></h3>

<p align="center">Wins: 2963<br>Losses: 2838<br>Win Rate: 51.1%</p>

<h4 align="center">Heroes</h4>

<div align="center" markdown="1">

| D.Va | Lucio | Freja | Symmetra |
|:---:|:---:|:---:|:---:|
| <img src="https://cdn3.emoji.gg/emojis/5341-dvapeace.png" width="60"> | <img src="https://cdn3.emoji.gg/emojis/8866-luciocool.png" width="60"> | <img src="https://i.pinimg.com/736x/31/33/7a/31337adb5d3962e15a2c2ad9fe3856dc.jpg" width="60"> | <img src="https://cdn3.emoji.gg/emojis/8861-symmetragiggle.png" width="60"> |
| 377W - 348L (52.0%) | 247W - 183L (57.4%) | 116W - 111L (51.1%) | 59W - 38L (60.8%) |

</div>

<!-- END_STATS -->
