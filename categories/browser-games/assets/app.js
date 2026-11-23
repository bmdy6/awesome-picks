"use strict";

(function () {
  const colors = {
    shooting: ["#3d7b66", "#304d83"],
    vehicles: ["#856047", "#333d67"],
    strategy: ["#4e6489", "#412f61"],
    action: ["#99536b", "#4f3c89"],
    building: ["#4b8b8b", "#2f4a74"],
    party: ["#6753a1", "#423e75"],
  };
  const icons = {
    shooting: "🎯",
    vehicles: "🚀",
    strategy: "🗺️",
    action: "⚔️",
    building: "🏙️",
    party: "🎉",
  };
  const $ = (selector) => document.querySelector(selector);
  let catalog = null;
  let category = "all";

  function make(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  function safeUrl(raw) {
    if (typeof raw !== "string") return null;
    try {
      const url = new URL(raw);
      if (!["https:", "http:"].includes(url.protocol)) return null;
      return url.href;
    } catch {
      return null;
    }
  }

  function addAnchor(parent, url, text, className) {
    const verified = safeUrl(url);
    if (!verified) return null;
    const a = make("a", className, text);
    a.href = verified;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    parent.appendChild(a);
    return a;
  }

  function getCategory(game) {
    return catalog.categories.find((item) => item.id === game.category);
  }

  function cover(game, type, index) {
    const holder = make("a", type);
    holder.href = safeUrl(game.play_url);
    holder.target = "_blank";
    holder.rel = "noopener noreferrer";
    holder.setAttribute("aria-label", game.name + " 官方游玩页");
    holder.appendChild(make("span", "cover-fallback", game.name + " · 官方图片暂缺"));
    const palette = colors[game.category] || ["#33445d", "#634e8b"];
    holder.style.setProperty("--cover-a", palette[0]);
    holder.style.setProperty("--cover-b", palette[1]);
    holder.appendChild(make("span", "cover-icon", icons[game.category] || "🎮"));
    holder.appendChild(make("span", "cover-glare"));
    if (safeUrl(game.cover_url)) {
      const img = make("img");
      img.alt = game.name + " 官方图片";
      img.loading = "lazy";
      img.decoding = "async";
      img.referrerPolicy = "no-referrer";
      img.addEventListener("error", () => img.remove());
      img.src = game.cover_url;
      holder.appendChild(img);
    }
    if (type === "spotlight-cover") {
      holder.appendChild(make("span", "spotlight-number", "PICK / " + String(index + 1).padStart(2, "0")));
    } else {
      const cn = getCategory(game);
      holder.appendChild(make("span", "cover-topline", (cn ? cn.emoji + " " + cn.name : "浏览器游戏")));
    }
    return holder;
  }

  function sourceText(game) {
    if (game.source_status === "open") return "源码 ↗";
    if (game.source_status === "unavailable") return "源码待恢复";
    if (game.source_status === "unknown") return "授权待核对 ↗";
    return "未提供源码";
  }

  function spotlight(game, index) {
    const card = make("article", "spotlight");
    card.appendChild(cover(game, "spotlight-cover", index));
    const body = make("div", "spotlight-body");
    body.appendChild(make("div", "mini-meta", (getCategory(game)?.emoji || "🎮") + "  " + (getCategory(game)?.name || "游戏")));
    body.appendChild(make("h3", "", game.name));
    body.appendChild(make("p", "", game.summary));
    const actions = make("div", "spotlight-actions");
    addAnchor(actions, game.play_url, "前往试玩 ↗");
    if (game.source_status === "open" && game.source_url) addAnchor(actions, game.source_url, "查看源码 ↗");
    body.appendChild(actions);
    card.appendChild(body);
    return card;
  }

  function gameCard(game) {
    const card = make("article", "game-card");
    card.appendChild(cover(game, "game-cover", 0));
    const body = make("div", "game-card-body");
    body.appendChild(make("div", "mini-meta", game.featured ? "✳ 重点推荐" : "◦ 精选收录"));
    body.appendChild(make("h3", "game-card-name", game.name));
    body.appendChild(make("p", "game-description", game.summary));
    const tags = make("div", "tag-list");
    for (const label of game.labels || []) tags.appendChild(make("span", "tag", label));
    if (game.zh_status === "yes") tags.appendChild(make("span", "tag is-zh", "简体中文已确认"));
    if (game.zh_status === "partial") tags.appendChild(make("span", "tag is-zh", "部分中文"));
    body.appendChild(tags);
    const actions = make("div", "card-actions");
    addAnchor(actions, game.play_url, "▶ 打开游戏 ↗", "play-link");
    if (game.source_url && game.source_status !== "unavailable") {
      addAnchor(actions, game.source_url, sourceText(game), "source-link");
    } else {
      actions.appendChild(make("span", "source-absent", sourceText(game)));
    }
    body.appendChild(actions);
    if (game.note) body.appendChild(make("p", "card-note", game.note));
    card.appendChild(body);
    return card;
  }

  function createCategories() {
    const bar = $("#category-filters");
    for (const item of catalog.categories) {
      const button = make("button", "category-btn", item.emoji + "  " + item.name);
      button.type = "button";
      button.dataset.category = item.id;
      button.setAttribute("aria-pressed", String(item.id === "all"));
      button.addEventListener("click", () => {
        category = item.id;
        show();
      });
      bar.appendChild(button);
    }
  }

  function show() {
    if (!catalog) return;
    const query = $("#search").value.trim().toLocaleLowerCase("zh-CN");
    const sourceOnly = $("#only-source").checked;
    const zhOnly = $("#only-zh").checked;
    const games = catalog.games.filter((game) => {
      if (category !== "all" && game.category !== category) return false;
      if (sourceOnly && game.source_status !== "open") return false;
      if (zhOnly && game.zh_status !== "yes" && game.zh_status !== "partial") return false;
      const searchable = [game.name, game.summary, ...(game.labels || []), game.note || ""].join(" ").toLocaleLowerCase("zh-CN");
      return !query || searchable.includes(query);
    });
    const grid = $("#game-grid");
    grid.replaceChildren();
    for (const game of games) grid.appendChild(gameCard(game));
    $("#result-count").textContent = "显示 " + games.length + " / " + catalog.games.length + " 款";
    $("#empty-state").hidden = games.length !== 0;
    for (const button of document.querySelectorAll(".category-btn")) {
      const active = button.dataset.category === category;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    }
  }

  async function init() {
    try {
      const response = await fetch("data/games.json", { cache: "no-cache" });
      if (!response.ok) throw new Error("目录 HTTP " + response.status);
      catalog = await response.json();
      if (!Array.isArray(catalog.games) || !Array.isArray(catalog.categories)) throw new Error("数据结构无效");
      $("#game-total").textContent = String(catalog.games.length);
      $("#category-total").textContent = String(catalog.categories.length - 1);
      const featured = catalog.games.filter((game) => game.featured).slice(0, 8);
      const hero = $("#featured-grid");
      hero.replaceChildren();
      featured.forEach((game, index) => hero.appendChild(spotlight(game, index)));
      createCategories();
      $("#search").addEventListener("input", show);
      $("#only-source").addEventListener("change", show);
      $("#only-zh").addEventListener("change", show);
      $("#clear-filters").addEventListener("click", () => {
        category = "all";
        $("#search").value = "";
        $("#only-source").checked = false;
        $("#only-zh").checked = false;
        show();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey) return;
        if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
        event.preventDefault();
        $("#search").focus();
      });
      show();
    } catch (error) {
      $("#featured-grid").textContent = "目录暂时无法加载，请从 GitHub README 查看游戏列表。";
      $("#game-grid").replaceChildren();
      $("#game-grid").appendChild(make("p", "loading", "目录加载失败：" + error.message + "。请在 HTTP 环境打开本页，或访问仓库 README。"));
      $("#result-count").textContent = "加载失败";
    }
  }

  init();
})();
