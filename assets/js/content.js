async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Could not load ${path}`);
  }
  return response.json();
}

function text(value) {
  return String(value || "").replace(/[&<>"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;"
  })[character]);
}

function renderCredits(credits) {
  if (!credits || !Object.keys(credits).length) {
    return "";
  }

  const items = Object.entries(credits)
    .filter(([, value]) => value)
    .map(([label, value]) => `<div><dt>${text(label)}</dt><dd>${text(value)}</dd></div>`)
    .join("");

  return `<dl class="credits">${items}</dl>`;
}

function sortNewestFirst(items) {
  return [...items].sort((a, b) => Number(b.sortOrder || b.year || 0) - Number(a.sortOrder || a.year || 0));
}

function slug(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function youtubeEmbedUrl(url) {
  if (!url) return "";

  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtu.be")) {
      return `https://www.youtube.com/embed/${text(parsed.pathname.slice(1))}`;
    }

    if (parsed.hostname.includes("youtube.com")) {
      const videoId = parsed.searchParams.get("v");
      return videoId ? `https://www.youtube.com/embed/${text(videoId)}` : "";
    }
  } catch (error) {
    return "";
  }

  return "";
}

async function renderWorks() {
  const mount = document.querySelector("[data-works]");
  if (!mount) return;

  try {
    const data = await loadJson("/content/works.json");
    const works = sortNewestFirst(data.works || []).filter((work) => work.published !== false);

    if (!works.length) {
      mount.innerHTML = '<p class="empty-state">No works published yet.</p>';
      return;
    }

    mount.innerHTML = works.map((work) => {
      const videoUrl = youtubeEmbedUrl(work.video);

      return `
        <article class="work-card ${work.image ? "" : "work-card-no-image"}" id="${text(work.id || slug(work.title))}">
          ${work.image ? `<div class="work-visual"><img src="${text(work.image)}" alt="${text(work.title)}"></div>` : ""}
          <div class="work-body ${videoUrl ? "work-body-with-video" : ""}">
            <div class="work-copy">
              <h2 class="work-title">${text(work.title)}</h2>
              <p class="work-subtitle">${text(work.subtitle)}</p>
              <p class="work-description">${text(work.description)}</p>
              ${renderCredits(work.credits)}
            </div>
            ${videoUrl ? `<div class="video-embed"><iframe src="${videoUrl}" title="${text(work.title)} video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>` : ""}
          </div>
        </article>
      `;
    }).join("");
  } catch (error) {
    mount.innerHTML = '<p class="empty-state">Works could not be loaded.</p>';
  }
}

function renderEventCard(event) {
  return `
    <article class="event-card">
      <p class="event-date">${text(event.date)}</p>
      <div class="event-main">
        <h2 class="event-title">${text(event.title)}</h2>
        ${event.venue || event.location ? `<p class="event-meta">${event.link ? `<a href="${text(event.link)}" target="_blank" rel="noreferrer">${text(event.venue)}</a>` : text(event.venue)}${event.location ? `<br>${text(event.location)}` : ""}</p>` : ""}
        ${event.description ? `<p class="event-description">${text(event.description)}</p>` : ""}
      </div>
      ${event.detailsLink ? `<a class="event-link" href="${text(event.detailsLink)}">Details -></a>` : ""}
    </article>
  `;
}

async function renderEvents() {
  const allEventsMount = document.querySelector("[data-events]");
  const upcomingMount = document.querySelector("[data-upcoming-events]");
  const pastMount = document.querySelector("[data-past-events]");
  if (!allEventsMount && (!upcomingMount || !pastMount)) return;

  try {
    const data = await loadJson("/content/events.json");
    const events = (data.events || []).filter((event) => event.published !== false);
    if (allEventsMount) {
      allEventsMount.innerHTML = events.length ? events.map(renderEventCard).join("") : '<p class="empty-state">No events published yet.</p>';
      return;
    }

    const upcoming = events.filter((event) => event.type === "upcoming");
    const past = events.filter((event) => event.type === "past");

    upcomingMount.innerHTML = upcoming.length ? upcoming.map(renderEventCard).join("") : '<p class="empty-state">No upcoming events published yet.</p>';
    pastMount.innerHTML = past.length ? past.map(renderEventCard).join("") : '<p class="empty-state">No past events published yet.</p>';
  } catch (error) {
    if (allEventsMount) {
      allEventsMount.innerHTML = '<p class="empty-state">Events could not be loaded.</p>';
      return;
    }

    upcomingMount.innerHTML = '<p class="empty-state">Events could not be loaded.</p>';
    pastMount.innerHTML = '<p class="empty-state">Events could not be loaded.</p>';
  }
}

renderWorks();
renderEvents();
